from datetime import timedelta

from fastapi import APIRouter, Depends, Body
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.crud import serialize
from app.core.response import ok, fail
from app.models.procurement import (
    Supplier, SupplierMaterial, PurchaseOrder, PurchaseOrderLine,
)
from app.models.inventory import RawMaterial, InventoryRawMaterial
from app.models.product import BOMLine, BOMHeader
from app.models.production import ProductionOrder
from app.models.quality import QualityCheck

router = APIRouter()


def _po_view(o: PurchaseOrder, db: Session) -> dict:
    row = serialize(o)
    sup = db.get(Supplier, o.supplier_id)
    row["supplier_name"] = sup.name if sup else "-"
    lines = db.scalars(select(PurchaseOrderLine).where(PurchaseOrderLine.po_id == o.id)).all()
    out_lines = []
    for l in lines:
        lr = serialize(l)
        rm = db.get(RawMaterial, l.material_id)
        lr["material_name"] = rm.name if rm else "-"
        out_lines.append(lr)
    row["lines"] = out_lines
    row["lines_count"] = len(lines)
    return row


@router.get("/{factory_id}/procurement/purchase-orders")
def list_pos(factory_id: int, page: int = 1, page_size: int = 20, status: str | None = None, db: Session = Depends(get_db)):
    from app.core.crud import list_resources
    filters = {"status": status} if status else None
    rows, total = list_resources(db, PurchaseOrder, factory_id, page=page, page_size=page_size,
                                 search_fields=["po_number"], filters=filters, order_by="order_date")
    rows = [_po_view(db.get(PurchaseOrder, r["id"]), db) for r in rows]
    return ok(rows, "OK", total=total, page=page, page_size=page_size)


@router.post("/{factory_id}/procurement/purchase-orders")
def create_po(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    lines = data.pop("lines", [])
    total = 0.0
    po = PurchaseOrder(factory_id=factory_id, supplier_id=data["supplier_id"],
                       po_number=data.get("po_number"), order_date=data.get("order_date"),
                       expected_delivery=data.get("expected_delivery"), status=data.get("status", "planned"),
                       currency=data.get("currency", "USD"), notes=data.get("notes"))
    db.add(po)
    db.flush()
    for l in lines:
        qty = float(l.get("qty_ordered", 0))
        price = float(l.get("unit_price", 0))
        total += qty * price
        db.add(PurchaseOrderLine(po_id=po.id, material_id=l["material_id"], qty_ordered=qty,
                                 unit_price=price, qty_received=0, quality_status="pending"))
    po.total_value = round(total, 2)
    db.commit()
    return ok(_po_view(po, db), "PO created")


@router.get("/{factory_id}/procurement/purchase-orders/{rid}")
def get_po(factory_id: int, rid: int, db: Session = Depends(get_db)):
    o = db.get(PurchaseOrder, rid)
    if not o or o.factory_id != factory_id:
        return fail("Not found")
    return ok(_po_view(o, db))


@router.put("/{factory_id}/procurement/purchase-orders/{rid}")
def update_po(factory_id: int, rid: int, data: dict = Body(...), db: Session = Depends(get_db)):
    o = db.get(PurchaseOrder, rid)
    if not o or o.factory_id != factory_id:
        return fail("Not found")
    for k, v in data.items():
        if k in ("lines", "id", "factory_id"):
            continue
        setattr(o, k, v)
    if "lines" in data:
        db.query(PurchaseOrderLine).where(PurchaseOrderLine.po_id == rid).delete()
        for l in data["lines"]:
            db.add(PurchaseOrderLine(po_id=rid, material_id=l["material_id"],
                                     qty_ordered=l["qty_ordered"], unit_price=l.get("unit_price", 0),
                                     quality_status="pending"))
    db.commit()
    return ok(_po_view(o, db), "Updated")


@router.delete("/{factory_id}/procurement/purchase-orders/{rid}")
def delete_po(factory_id: int, rid: int, db: Session = Depends(get_db)):
    o = db.get(PurchaseOrder, rid)
    if not o or o.factory_id != factory_id:
        return fail("Not found")
    o.is_deleted = True
    db.commit()
    return ok(None, "Deleted")


@router.post("/{factory_id}/procurement/purchase-orders/{rid}/receive/{line_id}")
def receive_line(factory_id: int, rid: int, line_id: int, data: dict = Body(default={}), db: Session = Depends(get_db)):
    line = db.get(PurchaseOrderLine, line_id)
    if not line or line.po_id != rid:
        return fail("Not found")
    qty = data.get("qty_received", line.qty_ordered)
    line.qty_received = qty
    line.quality_status = data.get("quality_status", "accepted")
    po = db.get(PurchaseOrder, rid)
    if po:
        po.status = "received"
        po.actual_delivery = __import__("datetime").datetime.utcnow()
    # update inventory
    inv = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.material_id == line.material_id)).first()
    if inv:
        inv.qty_on_hand += qty
        inv.qty_available = inv.qty_on_hand - inv.qty_reserved
    db.commit()
    return ok(None, "Received")


@router.get("/{factory_id}/procurement/requirements")
def requirements(factory_id: int, db: Session = Depends(get_db)):
    orders = db.scalars(select(ProductionOrder).where(
        ProductionOrder.factory_id == factory_id, ProductionOrder.status.in_(["planned", "in_progress"]))).all()
    gross: dict[int, float] = {}
    for o in orders:
        if not o.product_id:
            continue
        for bl in db.scalars(select(BOMLine).join(BOMHeader, BOMLine.bom_id == BOMHeader.id).where(BOMHeader.product_id == o.product_id)).all():
            gross[bl.material_id] = gross.get(bl.material_id, 0) + o.planned_qty * bl.quantity_required
    out = []
    for mid, g in gross.items():
        rm = db.get(RawMaterial, mid)
        inv = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.material_id == mid)).first()
        on_hand = inv.qty_available if inv else 0
        net = round(max(0, g - on_hand), 1)
        if net > 0:
            sup = db.scalars(select(SupplierMaterial).where(
                SupplierMaterial.material_id == mid, SupplierMaterial.is_preferred == True)).first()
            supplier_name = "-"
            if sup:
                s = db.get(Supplier, sup.supplier_id)
                supplier_name = s.name if s else "-"
            out.append({"material_id": mid, "material": rm.name if rm else "-",
                        "gross_req": round(g, 1), "on_hand": on_hand, "net_req": net,
                        "po_date": (__import__("datetime").date.today() + timedelta(days=rm.lead_time_days if rm else 7)).isoformat(),
                        "supplier": supplier_name})
    return ok(out)


@router.get("/{factory_id}/procurement/suppliers/performance")
def supplier_performance(factory_id: int, db: Session = Depends(get_db)):
    suppliers = db.scalars(select(Supplier).where(
        Supplier.factory_id == factory_id, Supplier.is_deleted == False)).all()
    out = []
    for s in suppliers:
        pos = db.scalars(select(PurchaseOrder).where(
            PurchaseOrder.factory_id == factory_id, PurchaseOrder.supplier_id == s.id)).all()
        on_time = sum(1 for p in pos if p.actual_delivery and p.expected_delivery and p.actual_delivery <= p.expected_delivery)
        total = len(pos) or 1
        otd = round(on_time / total * 100, 1)
        lines = db.scalars(select(PurchaseOrderLine).where(
            PurchaseOrderLine.po_id.in_([p.id for p in pos]))).all()
        accepted = sum(1 for l in lines if l.quality_status == "accepted")
        q = round(accepted / (len(lines) or 1) * 100, 1)
        out.append({"id": s.id, "name": s.name, "otd": otd, "quality": q,
                    "active_pos": sum(1 for p in pos if p.status in ("issued", "in_transit", "confirmed")),
                    "rating": s.rating})
    return ok(out)

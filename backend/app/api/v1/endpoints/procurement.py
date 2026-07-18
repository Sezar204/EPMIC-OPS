Input
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.engines.mrp_engine import MRPEngine
from app.services.operations import InventoryService
from app.repositories.modules import PurchaseOrderRepo
from app.models import PurchaseOrder, PurchaseOrderLine, Supplier

router = APIRouter()


@router.get("/purchase-orders/{factory_id}")
def list_pos(factory_id: int, db: Session = Depends(get_db)):
    items = db.query(PurchaseOrder).filter(PurchaseOrder.factory_id == factory_id).all()
    return ok([{
        "id": i.id, "factory_id": i.factory_id, "supplier_id": i.supplier_id,
        "po_number": i.po_number, "order_date": i.order_date.isoformat(),
        "expected_delivery": i.expected_delivery.isoformat(),
        "actual_delivery": i.actual_delivery.isoformat() if i.actual_delivery else None,
        "status": i.status, "total_value": i.total_value, "currency": i.currency,
    } for i in items], total=len(items))


@router.get("/purchase-orders/{factory_id}/{po_id}")
def get_po(factory_id: int, po_id: int, db: Session = Depends(get_db)):
    obj = PurchaseOrderRepo(db).get_with_lines(po_id)
    if not obj or obj.factory_id != factory_id: raise HTTPException(status_code=404, detail="Not found")
    return ok({"id": obj.id, "po_number": obj.po_number, "supplier_id": obj.supplier_id,
               "status": obj.status, "lines": [{
                   "id": l.id, "material_id": l.material_id, "qty_ordered": l.qty_ordered,
                   "qty_received": l.qty_received, "unit_price": l.unit_price,
               } for l in (obj.lines or [])]})


@router.post("/purchase-orders/{factory_id}")
def create_po(factory_id: int, payload: dict, db: Session = Depends(get_db)):
    data = payload.copy()
    lines = data.pop("lines", [])
    obj = PurchaseOrder(factory_id=factory_id, total_value=0, **data)
    db.add(obj); db.flush()
    total = 0
    for ln in lines:
        db.add(PurchaseOrderLine(po_id=obj.id, **ln))
        total += ln["qty_ordered"] * ln["unit_price"]
    obj.total_value = total
    db.commit()
    return ok({"id": obj.id}, "PO created")


@router.put("/purchase-orders/{factory_id}/{po_id}")
def update_po(factory_id: int, po_id: int, payload: dict, db: Session = Depends(get_db)):
    obj = PurchaseOrderRepo(db).get(po_id)
    if not obj or obj.factory_id != factory_id: raise HTTPException(404, "Not found")
    for k, v in payload.items(): setattr(obj, k, v)
    db.commit()
    return ok(None, "PO updated")


@router.delete("/purchase-orders/{factory_id}/{po_id}")
def delete_po(factory_id: int, po_id: int, db: Session = Depends(get_db)):
    ok_flag = PurchaseOrderRepo(db).delete(po_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Not found")
    db.commit()
    return ok(None, "PO deleted")


@router.get("/requirements/{factory_id}")
def requirements(factory_id: int, db: Session = Depends(get_db)):
    r = MRPEngine().run(db, factory_id)
    return ok(r.data.get("requirements", []))


@router.get("/suppliers/performance/{factory_id}")
def perf(factory_id: int, db: Session = Depends(get_db)):
    sups = db.query(Supplier).filter(Supplier.factory_id == factory_id).all()
    pos  = db.query(PurchaseOrder).filter(PurchaseOrder.factory_id == factory_id).all()
    out = []
    for s in sups:
        s_pos = [p for p in pos if p.supplier_id == s.id]
        delivered = [p for p in s_pos if p.status in ("received", "closed")]
        on_time = sum(1 for p in delivered if p.actual_delivery and p.actual_delivery <= p.expected_delivery)
        otd = (on_time / len(delivered) * 100) if delivered else 95
        out.append({
            "supplier_id": s.id, "supplier_name": s.name, "code": s.code,
            "rating": s.rating, "active_pos": len([p for p in s_pos if p.status not in ("closed", "cancelled")]),
            "on_time_delivery_pct": round(otd, 1), "quality_acceptance_pct": 96.5,
            "monthly_otd": [{"month": f"M-{i}", "value": round(otd + (i % 3 - 1) * 1.5, 1)} for i in range(6, 0, -1)],
        })
    return ok(out)

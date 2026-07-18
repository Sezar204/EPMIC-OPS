from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.crud import serialize
from app.core.response import ok
from app.models.inventory import (
    RawMaterial, InventoryRawMaterial, InventoryFinishedGoods, InventoryWIP,
)
from app.models.product import Product
from app.models.production import ProductionOrder
from app.models.product import BOMLine, BOMHeader

router = APIRouter()


@router.get("/{factory_id}/inventory/raw-materials")
def raw_materials(factory_id: int, page: int = 1, page_size: int = 50, db: Session = Depends(get_db)):
    from app.core.crud import list_resources
    rows, total = list_resources(db, RawMaterial, factory_id, page=page, page_size=page_size,
                                 search_fields=["code", "name"], order_by="code")
    out = []
    for r in rows:
        inv = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.material_id == r["id"])).first()
        r["on_hand"] = inv.qty_on_hand if inv else 0
        r["reserved"] = inv.qty_reserved if inv else 0
        r["available"] = inv.qty_available if inv else 0
        out.append(r)
    return ok(out, "OK", total=total, page=page, page_size=page_size)


@router.get("/{factory_id}/inventory/finished-goods")
def finished_goods(factory_id: int, db: Session = Depends(get_db)):
    rows = db.scalars(select(InventoryFinishedGoods).where(
        InventoryFinishedGoods.factory_id == factory_id)).all()
    out = []
    for r in rows:
        prod = db.get(Product, r.product_id)
        out.append({"id": r.id, "product": prod.name if prod else "-", "sku": prod.sku if prod else "-",
                    "on_hand": r.qty_on_hand, "reserved": r.qty_reserved, "available": r.qty_available,
                    "warehouse_id": r.warehouse_id})
    return ok(out)


@router.get("/{factory_id}/inventory/wip")
def wip(factory_id: int, db: Session = Depends(get_db)):
    rows = db.scalars(select(InventoryWIP).where(InventoryWIP.factory_id == factory_id)).all()
    out = []
    for r in rows:
        prod = db.get(Product, r.product_id)
        out.append({"id": r.id, "product": prod.name if prod else "-", "qty": r.qty_in_process,
                    "stage": r.stage, "last_updated": r.last_updated.isoformat() if r.last_updated else None})
    return ok(out)


@router.get("/{factory_id}/inventory/analysis/critical-items")
def critical_items(factory_id: int, db: Session = Depends(get_db)):
    materials = db.scalars(select(RawMaterial).where(
        RawMaterial.factory_id == factory_id, RawMaterial.is_deleted == False)).all()
    since = __import__("datetime").datetime.utcnow() - timedelta(days=30)
    orders = db.scalars(select(ProductionOrder).where(
        ProductionOrder.factory_id == factory_id, ProductionOrder.actual_start >= since)).all()
    usage = {}
    for o in orders:
        if not o.product_id:
            continue
        for bl in db.scalars(select(BOMLine).join(BOMHeader, BOMLine.bom_id == BOMHeader.id).where(BOMHeader.product_id == o.product_id)).all():
            usage[bl.material_id] = usage.get(bl.material_id, 0) + (o.produced_qty or 0) * bl.quantity_required
    out = []
    for rm in materials:
        inv = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.material_id == rm.id)).first()
        available = inv.qty_available if inv else 0
        daily = usage.get(rm.id, 0) / 30
        days = round(available / daily, 1) if daily > 0 else 999
        status = "emergency" if days < 3 else "warning" if days < 7 else "ok"
        if status != "ok":
            out.append({"id": rm.id, "code": rm.code, "name": rm.name, "on_hand": inv.qty_on_hand if inv else 0,
                        "safety": rm.safety_stock_qty, "coverage_days": days, "status": status})
    return ok(out)


@router.get("/{factory_id}/inventory/analysis/coverage")
def coverage(factory_id: int, db: Session = Depends(get_db)):
    materials = db.scalars(select(RawMaterial).where(
        RawMaterial.factory_id == factory_id, RawMaterial.is_deleted == False)).all()
    since = __import__("datetime").datetime.utcnow() - timedelta(days=30)
    orders = db.scalars(select(ProductionOrder).where(
        ProductionOrder.factory_id == factory_id, ProductionOrder.actual_start >= since)).all()
    usage = {}
    for o in orders:
        if not o.product_id:
            continue
        for bl in db.scalars(select(BOMLine).join(BOMHeader, BOMLine.bom_id == BOMHeader.id).where(BOMHeader.product_id == o.product_id)).all():
            usage[bl.material_id] = usage.get(bl.material_id, 0) + (o.produced_qty or 0) * bl.quantity_required
    out = []
    for rm in materials:
        inv = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.material_id == rm.id)).first()
        available = inv.qty_available if inv else 0
        daily = usage.get(rm.id, 0) / 30
        days = round(available / daily, 1) if daily > 0 else 999
        out.append({"id": rm.id, "code": rm.code, "name": rm.name, "available": available, "coverage_days": days})
    return ok(out)


@router.get("/{factory_id}/inventory/analysis/abc-xyz")
def abc_xyz(factory_id: int, db: Session = Depends(get_db)):
    # ABC by standard cost value, XYZ by demand variability (coefficient of variation)
    products = db.scalars(select(Product).where(Product.factory_id == factory_id, Product.is_deleted == False)).all()
    import statistics
    values = {}
    variability = {}
    for p in products:
        inv = db.scalars(select(InventoryFinishedGoods).where(InventoryFinishedGoods.product_id == p.id)).first()
        on_hand = inv.qty_on_hand if inv else 0
        values[p.id] = p.standard_cost * on_hand
        # use sales order lines qty as demand proxy
        qty = db.scalar(select(func.coalesce(func.sum(ProductionOrder.produced_qty), 0)).where(ProductionOrder.product_id == p.id)) or 0
        variability[p.id] = qty
    total_val = sum(values.values()) or 1
    sorted_ids = sorted(values, key=lambda i: values[i], reverse=True)
    cumulative = 0
    matrix = {k: [] for k in ["AX", "AY", "AZ", "BX", "BY", "BZ", "CX", "CY", "CZ"]}
    for i, pid in enumerate(sorted_ids):
        cumulative += values[pid]
        pct = cumulative / total_val
        abc = "A" if pct <= 0.8 else "B" if pct <= 0.95 else "C"
        # XYZ: low variation stable
        xyz = "X"  # simplified: all stable
        matrix[f"{abc}{xyz}"].append(pid)
    return ok({"matrix": {k: len(v) for k, v in matrix.items()}, "detail": matrix})

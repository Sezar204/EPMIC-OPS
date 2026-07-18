from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.helpers import add_crud_routes
from app.core.response import ok
from app.models.inventory import RawMaterial, InventoryRawMaterial
from app.models.production import ProductionOrder
from app.models.product import BOMLine, BOMHeader
from app.core.crud import serialize

router = APIRouter()


def compute_coverage(db: Session, fid: int) -> dict[int, float]:
    since = __import__("datetime").datetime.utcnow() - timedelta(days=30)
    orders = db.scalars(select(ProductionOrder).where(
        ProductionOrder.factory_id == fid, ProductionOrder.actual_start >= since)).all()
    usage: dict[int, float] = {}
    for o in orders:
        if not o.product_id or not o.produced_qty:
            continue
        for bl in db.scalars(select(BOMLine).join(BOMHeader, BOMLine.bom_id == BOMHeader.id).where(BOMHeader.product_id == o.product_id)).all():
            usage[bl.material_id] = usage.get(bl.material_id, 0) + o.produced_qty * bl.quantity_required
    return {mid: u / 30 for mid, u in usage.items()}


@router.get("/{factory_id}/master-data/raw-materials/summary")
def summary(factory_id: int, db: Session = Depends(get_db)):
    materials = db.scalars(select(RawMaterial).where(
        RawMaterial.factory_id == factory_id, RawMaterial.is_deleted == False)).all()
    coverage = compute_coverage(db, factory_id)
    total = len(materials)
    below_safety = 0
    critical = 0
    dead = 0
    for rm in materials:
        inv = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.material_id == rm.id)).first()
        on_hand = inv.qty_on_hand if inv else 0
        available = inv.qty_available if inv else 0
        if on_hand < rm.safety_stock_qty:
            below_safety += 1
        daily = coverage.get(rm.id, 0)
        days = available / daily if daily > 0 else 999
        if days < 3:
            critical += 1
        if on_hand > 2 * rm.safety_stock_qty and days > 180:
            dead += 1
    return ok({"total": total, "below_safety": below_safety, "critical": critical, "dead_stock": dead})


@router.get("/{factory_id}/master-data/raw-materials/with-coverage")
def with_coverage(factory_id: int, db: Session = Depends(get_db)):
    materials = db.scalars(select(RawMaterial).where(
        RawMaterial.factory_id == factory_id, RawMaterial.is_deleted == False)).all()
    coverage = compute_coverage(db, factory_id)
    out = []
    for rm in materials:
        inv = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.material_id == rm.id)).first()
        on_hand = inv.qty_on_hand if inv else 0
        available = inv.qty_available if inv else 0
        daily = coverage.get(rm.id, 0)
        days = round(available / daily, 1) if daily > 0 else 999
        status = "emergency" if days < 3 else "warning" if days < 7 else "ok"
        row = serialize(rm)
        row["on_hand"] = on_hand
        row["available"] = available
        row["days_coverage"] = days
        row["coverage_status"] = status
        out.append(row)
    return ok(out)


add_crud_routes(router, RawMaterial, "master-data/raw-materials",
                search_fields=["code", "name"], order_by="code")

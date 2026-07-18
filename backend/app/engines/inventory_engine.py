from datetime import timedelta

from sqlalchemy import select

from app.engines.base import BaseEngine
from app.models.inventory import RawMaterial, InventoryRawMaterial
from app.models.production import ProductionOrder
from app.models.product import BOMLine, BOMHeader


class InventoryEngine(BaseEngine):
    name = "inventory_engine"

    def execute(self, db, factory_id: int):
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
        items = []
        dead = 0
        excess = 0
        for rm in materials:
            inv = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.material_id == rm.id)).first()
            available = inv.qty_available if inv else 0
            daily = usage.get(rm.id, 0) / 30
            days = round(available / daily, 1) if daily > 0 else 999
            cls = "A" if rm.standard_cost >= 2 else "B" if rm.standard_cost >= 0.5 else "C"
            xyz = "X" if daily > 0 else "Z"
            if days > 180 and available > 2 * rm.safety_stock_qty:
                dead += 1
            if available > 3 * rm.safety_stock_qty:
                excess += 1
            items.append({"code": rm.code, "name": rm.name, "coverage_days": days,
                          "abc": cls, "xyz": xyz, "value": round(rm.standard_cost * available, 2)})
        return self._ok("Inventory classification complete",
                        {"items": items, "dead_stock": dead, "excess_stock": excess})

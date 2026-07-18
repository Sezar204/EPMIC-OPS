from datetime import timedelta

from sqlalchemy import select

from app.engines.base import BaseEngine
from app.models.production import ProductionOrder
from app.models.product import BOMLine, BOMHeader
from app.models.inventory import RawMaterial, InventoryRawMaterial
from app.models.procurement import SupplierMaterial, PurchaseOrder, PurchaseOrderLine


class MRPEngine(BaseEngine):
    name = "mrp_engine"

    def execute(self, db, factory_id: int):
        orders = db.scalars(select(ProductionOrder).where(
            ProductionOrder.factory_id == factory_id,
            ProductionOrder.status.in_(["planned", "in_progress"]))).all()
        gross: dict[int, float] = {}
        for o in orders:
            if not o.product_id:
                continue
            for bl in db.scalars(select(BOMLine).join(BOMHeader, BOMLine.bom_id == BOMHeader.id).where(BOMHeader.product_id == o.product_id)).all():
                gross[bl.material_id] = gross.get(bl.material_id, 0) + o.planned_qty * bl.quantity_required
        reqs = []
        for mid, g in gross.items():
            inv = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.material_id == mid)).first()
            available = inv.qty_available if inv else 0
            net = round(max(0, g - available), 2)
            if net > 0:
                rm = db.get(RawMaterial, mid)
                link = db.scalars(select(SupplierMaterial).where(
                    SupplierMaterial.material_id == mid, SupplierMaterial.is_preferred == True)).first()
                supplier_id = link.supplier_id if link else None
                reqs.append({"material_id": mid, "material": rm.name if rm else "-",
                             "net_req": net, "supplier_id": supplier_id})
        return self._ok(f"Computed {len(reqs)} material requirements", {"requirements": reqs})

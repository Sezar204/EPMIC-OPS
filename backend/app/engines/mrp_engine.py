Input
"""MRP engine — explodes BOMs from production plan, computes net requirements,
suggests planned POs."""
from datetime import date, timedelta
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.engines import BaseEngine, EngineResult
from app.models import (
    ProductionOrder, Product, BOMHeader, BOMLine, RawMaterial,
    InventoryRawMaterial, SupplierMaterial, Supplier, PurchaseOrder,
    PurchaseOrderLine,
)


class MRPEngine(BaseEngine):
    name = "mrp"

    def _execute(self, db: Session, factory_id: int, r: EngineResult, horizon_days: int = 14, **kwargs):
        horizon_end = date.today() + timedelta(days=horizon_days)
        orders = db.scalars(select(ProductionOrder).where(
            ProductionOrder.factory_id == factory_id,
            ProductionOrder.planned_start <= horizon_end,
            ProductionOrder.status.in_(["planned", "in_progress", "confirmed"]),
        )).all()

        # Aggregate gross requirements per material
        gross: dict[int, float] = {}
        for o in orders:
            bom = db.scalars(select(BOMHeader).where(
                BOMHeader.product_id == o.product_id, BOMHeader.status == "active"
            )).first()
            if not bom: continue
            for bl in bom.lines or []:
                gross[bl.material_id] = gross.get(bl.material_id, 0) + \
                    bl.quantity_required * o.planned_qty * (1 + bl.loss_factor_pct / 100)

        # Subtract on-hand
        on_hand = {i.material_id: i.qty_on_hand for i in db.scalars(
            select(InventoryRawMaterial).where(InventoryRawMaterial.factory_id == factory_id)
        ).all()}

        r.data["requirements"] = []
        for mat_id, need in gross.items():
            oh = on_hand.get(mat_id, 0)
            net = max(0, need - oh)
            if net <= 0:
                continue
            mat = db.get(RawMaterial, mat_id)
            if not mat: continue
            sm = db.scalars(select(SupplierMaterial).where(
                SupplierMaterial.material_id == mat_id, SupplierMaterial.is_preferred == True  # noqa: E712
            )).first()
            supplier = db.get(Supplier, sm.supplier_id) if sm else None
            po_date = date.today() + timedelta(days=max(0, (mat.lead_time_days or 7) - 2))
            r.data["requirements"].append({
                "material_id": mat_id,
                "material_code": mat.code,
                "material_name": mat.name,
                "period_date": horizon_end.isoformat(),
                "gross_requirement": round(need, 2),
                "on_hand": round(oh, 2),
                "net_requirement": round(net, 2),
                "suggested_po_date": po_date.isoformat(),
                "preferred_supplier_id": supplier.id if supplier else None,
                "preferred_supplier_name": supplier.name if supplier else None,
            })

        r.items_processed = len(r.data["requirements"])
        if r.data["requirements"]:
            r.notes.append(f"Identified {len(r.data['requirements'])} net requirements")
        db.commit()

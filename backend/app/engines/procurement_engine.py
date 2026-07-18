Input
"""Procurement engine — turns MRP output into draft POs with preferred suppliers."""
from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.engines import BaseEngine, EngineResult
from app.models import (
    PurchaseOrder, PurchaseOrderLine, Supplier, RawMaterial,
    SupplierMaterial, InventoryRawMaterial,
)


class ProcurementEngine(BaseEngine):
    name = "procurement"

    def _execute(self, db: Session, factory_id: int, r: EngineResult, **kwargs):
        # Find materials below reorder point
        materials = {m.id: m for m in db.scalars(select(RawMaterial).where(
            RawMaterial.factory_id == factory_id
        )).all()}
        invs = {i.material_id: i for i in db.scalars(select(InventoryRawMaterial).where(
            InventoryRawMaterial.factory_id == factory_id
        )).all()}
        created = 0
        for mat_id, mat in materials.items():
            inv = invs.get(mat_id)
            if not inv: continue
            if inv.qty_on_hand < mat.reorder_point_qty:
                sm = db.scalars(select(SupplierMaterial).where(
                    SupplierMaterial.material_id == mat_id,
                    SupplierMaterial.is_preferred == True,  # noqa: E712
                )).first()
                if not sm: continue
                sup = db.get(Supplier, sm.supplier_id)
                if not sup: continue
                qty = (mat.safety_stock_qty * 3) - inv.qty_on_hand
                if qty < sm.min_order_qty:
                    qty = sm.min_order_qty
                po = PurchaseOrder(
                    factory_id=factory_id,
                    supplier_id=sup.id,
                    po_number=f"PO-DRAFT-{date.today().strftime('%Y%m%d')}-{created+1:03d}",
                    order_date=date.today(),
                    expected_delivery=date.today().toordinal() + mat.lead_time_days,
                    status="planned",
                    total_value=round(qty * sm.supplier_price, 2),
                    currency="USD",
                )
                po.expected_delivery = date.fromordinal(po.expected_delivery)
                db.add(po); db.flush()
                db.add(PurchaseOrderLine(
                    po_id=po.id, material_id=mat_id,
                    qty_ordered=qty, unit_price=sm.supplier_price,
                ))
                created += 1
        r.items_processed = created
        r.notes.append(f"Created {created} draft POs")
        db.commit()

from datetime import timedelta

from sqlalchemy import select, func

from app.engines.base import BaseEngine
from app.models.inventory import RawMaterial, InventoryRawMaterial
from app.models.procurement import PurchaseOrder
from app.models.quality import QualityCheck
from app.models.alert import Alert
from app.models.maintenance import MaintenanceWorkOrder, MaintenanceSchedule


class AlertEngine(BaseEngine):
    name = "alert_engine"

    def execute(self, db, factory_id: int):
        return self.run(db, factory_id)

    def run(self, db, factory_id: int):
        created = 0
        # inventory coverage
        materials = db.scalars(select(RawMaterial).where(
            RawMaterial.factory_id == factory_id, RawMaterial.is_deleted == False)).all()
        for rm in materials:
            inv = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.material_id == rm.id)).first()
            on_hand = inv.qty_on_hand if inv else 0
            if on_hand < rm.safety_stock_qty:
                sev = "emergency" if on_hand == 0 else "critical"
                if not self._exists(db, factory_id, "low_stock", rm.id):
                    db.add(Alert(factory_id=factory_id, alert_type="low_stock", severity=sev,
                                 title=f"{rm.name} below safety stock",
                                 message=f"On hand {on_hand} vs safety {rm.safety_stock_qty}.",
                                 source_module="inventory", source_id=rm.id))
                    created += 1
        # overdue purchase orders
        today = __import__("datetime").datetime.utcnow()
        pos = db.scalars(select(PurchaseOrder).where(
            PurchaseOrder.factory_id == factory_id, PurchaseOrder.status.in_(["issued", "in_transit", "confirmed"]),
            PurchaseOrder.expected_delivery < today)).all()
        for po in pos:
            if not self._exists(db, factory_id, "delivery", po.id):
                db.add(Alert(factory_id=factory_id, alert_type="delivery", severity="warning",
                             title=f"Purchase order {po.po_number} overdue",
                             message="Expected delivery passed.", source_module="procurement", source_id=po.id))
                created += 1
        # overdue PM
        scheds = db.scalars(select(MaintenanceSchedule).where(
            MaintenanceSchedule.factory_id == factory_id, MaintenanceSchedule.next_due < today)).all()
        for s in scheds:
            if not self._exists(db, factory_id, "maintenance", s.id):
                db.add(Alert(factory_id=factory_id, alert_type="maintenance", severity="warning",
                             title="Preventive maintenance overdue", source_module="maintenance",
                             source_id=s.machine_id, message="Scheduled PM is past due."))
                created += 1
        # recent quality failures
        qc = db.scalars(select(QualityCheck).where(
            QualityCheck.factory_id == factory_id, QualityCheck.status == "failed",
            QualityCheck.checked_at >= today - timedelta(days=7))).all()
        for q in qc:
            if not self._exists(db, factory_id, "quality", q.id):
                db.add(Alert(factory_id=factory_id, alert_type="quality", severity="critical",
                             title="Quality check failed", source_module="quality", source_id=q.id,
                             message=f"Defect rate {q.defect_rate_pct}%."))
                created += 1
        db.commit()
        return self._ok(f"Generated {created} alerts", {"created": created})

    def _exists(self, db, fid, atype, sid):
        return db.scalar(select(func.count()).select_from(Alert).where(
            Alert.factory_id == fid, Alert.alert_type == atype, Alert.source_id == sid,
            Alert.is_resolved == False)) > 0

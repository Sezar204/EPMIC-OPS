Input
"""Alert engine — scans all modules and raises alerts for threshold breaches."""
from datetime import date, datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.engines import BaseEngine, EngineResult
from app.models import (
    Alert, InventoryRawMaterial, RawMaterial, Machine, ProductionOrder,
    SalesOrder, MaintenanceSchedule, AttendanceRecord, QualityCheck,
)


class AlertEngine(BaseEngine):
    name = "alert"

    def _execute(self, db: Session, factory_id: int, r: EngineResult, **kwargs):
        r.items_processed += self._check_inventory(db, factory_id)
        r.items_processed += self._check_machines(db, factory_id)
        r.items_processed += self._check_production(db, factory_id)
        r.items_processed += self._check_sales(db, factory_id)
        r.items_processed += self._check_maintenance(db, factory_id)
        r.items_processed += self._check_attendance(db, factory_id)
        r.items_processed += self._check_quality(db, factory_id)
        db.commit()

    # --- helpers ---
    def _add(self, db, factory_id, alert_type, severity, title, message, source_id=None):
        existing = db.scalars(select(Alert).where(
            Alert.factory_id == factory_id,
            Alert.alert_type == alert_type,
            Alert.source_id == source_id,
            Alert.is_resolved == False,  # noqa: E712
        )).first()
        if existing:
            return 0
        a = Alert(
            factory_id=factory_id, alert_type=alert_type, severity=severity,
            title=title, message=message, source_id=source_id,
            source_module="alert_engine",
        )
        db.add(a)
        return 1

    def _check_inventory(self, db, factory_id) -> int:
        count = 0
        mats = {m.id: m for m in db.scalars(select(RawMaterial).where(
            RawMaterial.factory_id == factory_id
        )).all()}
        for inv in db.scalars(select(InventoryRawMaterial).where(
            InventoryRawMaterial.factory_id == factory_id
        )).all():
            mat = mats.get(inv.material_id)
            if not mat: continue
            if inv.qty_on_hand == 0:
                count += self._add(db, factory_id, "inventory_depleted", "emergency",
                                   f"Stock depleted: {mat.name}", f"Material {mat.code} is at 0 units.",
                                   source_id=mat.id)
            elif inv.qty_on_hand < mat.safety_stock_qty:
                sev = "critical" if inv.qty_on_hand < mat.safety_stock_qty * 0.5 else "warning"
                count += self._add(db, factory_id, "inventory_below_safety", sev,
                                   f"Below safety stock: {mat.name}",
                                   f"On hand {inv.qty_on_hand} < safety {mat.safety_stock_qty}.",
                                   source_id=mat.id)
        return count

    def _check_machines(self, db, factory_id) -> int:
        count = 0
        for m in db.scalars(select(Machine).where(
            Machine.factory_id == factory_id
        )).all():
            if m.status == "down":
                count += self._add(db, factory_id, "machine_down", "critical",
                                   f"Machine down: {m.name}", f"Machine {m.code} reported down.", source_id=m.id)
            elif m.status == "maintenance":
                count += self._add(db, factory_id, "machine_maintenance", "info",
                                   f"Machine in maintenance: {m.name}", f"Machine {m.code} under maintenance.", source_id=m.id)
        return count

    def _check_production(self, db, factory_id) -> int:
        count = 0
        today = date.today()
        late = db.scalars(select(ProductionOrder).where(
            ProductionOrder.factory_id == factory_id,
            ProductionOrder.planned_end < today,
            ProductionOrder.status.in_(["planned", "in_progress"]),
        )).all()
        for o in late:
            count += self._add(db, factory_id, "production_overdue", "warning",
                               f"Production order overdue: {o.order_number}",
                               f"Planned end {o.planned_end} passed; status={o.status}.",
                               source_id=o.id)
        return count

    def _check_sales(self, db, factory_id) -> int:
        count = 0
        soon = date.today() + timedelta(days=3)
        at_risk = db.scalars(select(SalesOrder).where(
            SalesOrder.factory_id == factory_id,
            SalesOrder.required_delivery <= soon,
            SalesOrder.status.in_(["draft", "confirmed", "in_production"]),
        )).all()
        for so in at_risk:
            count += self._add(db, factory_id, "sales_at_risk", "warning",
                               f"Sales order at risk: {so.order_number}",
                               f"Required delivery {so.required_delivery} approaching.", source_id=so.id)
        return count

    def _check_maintenance(self, db, factory_id) -> int:
        count = 0
        today = date.today()
        for s in db.scalars(select(MaintenanceSchedule).where(
            MaintenanceSchedule.factory_id == factory_id,
            MaintenanceSchedule.is_active == 1,
            MaintenanceSchedule.next_due_date < today,
        )).all():
            count += self._add(db, factory_id, "maintenance_overdue", "warning",
                               f"PM overdue: machine {s.machine_id}",
                               f"Next due {s.next_due_date} passed.", source_id=s.id)
        return count

    def _check_attendance(self, db, factory_id) -> int:
        count = 0
        cutoff = date.today() - timedelta(days=1)
        absent = db.scalars(select(AttendanceRecord).where(
            AttendanceRecord.factory_id == factory_id,
            AttendanceRecord.attendance_date >= cutoff,
            AttendanceRecord.status == "absent",
        )).count()
        if absent > 3:
            count += self._add(db, factory_id, "attendance_high_absent", "warning",
                               f"High absenteeism: {absent} workers absent",
                               f"More than 3 workers absent on {cutoff}.")
        return count

    def _check_quality(self, db, factory_id) -> int:
        count = 0
        cutoff = datetime.utcnow() - timedelta(days=7)
        for c in db.scalars(select(QualityCheck).where(
            QualityCheck.factory_id == factory_id,
            QualityCheck.checked_at >= cutoff,
            QualityCheck.status == "failed",
        )).all():
            count += self._add(db, factory_id, "quality_failure", "critical",
                               f"Quality check failed",
                               f"{c.check_type.upper()} check failed — defect rate {c.defect_rate_pct}%.",
                               source_id=c.id)
        return count

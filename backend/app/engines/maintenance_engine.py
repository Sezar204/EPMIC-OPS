Input
"""Maintenance engine — recalculates MTBF, MTTR, updates PM next-due dates."""
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.engines import BaseEngine, EngineResult
from app.models import (
    MaintenanceSchedule, MaintenanceWorkOrder, MachineBreakdown, Machine,
)


class MaintenanceEngine(BaseEngine):
    name = "maintenance"

    def _execute(self, db: Session, factory_id: int, r: EngineResult, **kwargs):
        schedules = db.scalars(select(MaintenanceSchedule).where(
            MaintenanceSchedule.factory_id == factory_id,
            MaintenanceSchedule.is_active == 1,
        )).all()
        advanced = 0
        for s in schedules:
            completed = db.scalars(select(MaintenanceWorkOrder).where(
                MaintenanceWorkOrder.machine_id == s.machine_id,
                MaintenanceWorkOrder.status == "completed",
                MaintenanceWorkOrder.completed_at >= s.last_done_date,
            )).all()
            if completed:
                last = max(c.completed_at for c in completed if c.completed_at)
                s.last_done_date = last.date()
                s.next_due_date = last.date() + timedelta(days=s.frequency_days)
                advanced += 1

        # Auto-create PM work orders for overdue schedules
        today = date.today()
        new_wos = 0
        for s in schedules:
            if s.next_due_date and s.next_due_date <= today:
                existing = db.scalars(select(MaintenanceWorkOrder).where(
                    MaintenanceWorkOrder.machine_id == s.machine_id,
                    MaintenanceWorkOrder.status.in_(["created", "assigned", "in_progress"]),
                )).first()
                if not existing:
                    db.add(MaintenanceWorkOrder(
                        factory_id=factory_id,
                        machine_id=s.machine_id,
                        wo_number=f"WO-PM-{date.today().strftime('%Y%m%d')}-{new_wos+1:03d}",
                        type=s.type,
                        status="created",
                        priority="medium",
                        description=f"PM auto-created: {s.description or 'preventive maintenance'}",
                        downtime_hours=s.estimated_hours,
                    ))
                    new_wos += 1

        r.items_processed = advanced + new_wos
        r.notes.append(f"Advanced {advanced} PM schedules; created {new_wos} PM WOs")
        db.commit()

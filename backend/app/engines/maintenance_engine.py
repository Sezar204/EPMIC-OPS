from datetime import timedelta

from sqlalchemy import select, func

from app.engines.base import BaseEngine
from app.models.maintenance import MaintenanceSchedule, MaintenanceWorkOrder, MachineBreakdown


class MaintenanceEngine(BaseEngine):
    name = "maintenance_engine"

    def execute(self, db, factory_id: int):
        now = __import__("datetime").datetime.utcnow()
        wos = db.scalars(select(MaintenanceWorkOrder).where(
            MaintenanceWorkOrder.factory_id == factory_id)).all()
        breakdowns = db.scalars(select(MachineBreakdown).where(
            MachineBreakdown.factory_id == factory_id)).all()
        total_runtime = 30 * 24  # assume 30-day window
        total_breakdowns = len(breakdowns)
        total_dt = sum(w.downtime_hours for w in wos)
        mtbf = round(total_runtime / total_breakdowns, 1) if total_breakdowns else 999
        mttr = round(total_dt / total_breakdowns, 1) if total_breakdowns else 0
        availability = round(100 - (total_dt / (total_runtime) * 100), 1) if total_runtime else 100
        # update overdue schedules
        overdue = 0
        scheds = db.scalars(select(MaintenanceSchedule).where(
            MaintenanceSchedule.factory_id == factory_id, MaintenanceSchedule.active == True)).all()
        for s in scheds:
            if s.next_due and s.next_due < now:
                overdue += 1
                if s.last_done:
                    from datetime import timedelta as td
                    s.next_due = s.last_done + td(days=s.frequency_days)
        db.commit()
        return self._ok("Maintenance metrics computed",
                        {"mtbf": mtbf, "mttr": mttr, "availability": max(0, availability),
                         "overdue_pm": overdue})

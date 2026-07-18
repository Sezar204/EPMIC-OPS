from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.helpers import add_crud_routes
from app.core.response import ok
from app.models.maintenance import MaintenanceSchedule, MaintenanceWorkOrder, MachineBreakdown
from app.models.production import Machine

router = APIRouter()
add_crud_routes(router, MaintenanceSchedule, "maintenance/schedules", order_by="next_due")
add_crud_routes(router, MaintenanceWorkOrder, "maintenance/work-orders", order_by="created_at")
add_crud_routes(router, MachineBreakdown, "maintenance/breakdowns", order_by="occurred_at")


@router.get("/{factory_id}/maintenance/metrics")
def metrics(factory_id: int, db: Session = Depends(get_db)):
    wos = db.scalars(select(MaintenanceWorkOrder).where(
        MaintenanceWorkOrder.factory_id == factory_id)).all()
    open_ = sum(1 for w in wos if w.status in ("created", "assigned", "in_progress"))
    in_progress = sum(1 for w in wos if w.status == "in_progress")
    overdue = sum(1 for w in wos if w.status != "completed" and w.due_date and w.due_date < datetime.utcnow()) if hasattr(MaintenanceWorkOrder, "due_date") else 0
    completed_month = sum(1 for w in wos if w.status == "completed" and w.completed_at and w.completed_at >= datetime.utcnow() - timedelta(days=30))
    total_dt = sum(w.downtime_hours for w in wos)
    machines = db.scalars(select(Machine).where(Machine.factory_id == factory_id, Machine.is_deleted == False)).all()
    # availability = uptime / (uptime + downtime)
    availability = 100.0
    if machines and total_dt:
        availability = round(100 - (total_dt / (len(machines) * 24 * 30) * 100), 1)
    return ok({"open": open_, "in_progress": in_progress, "overdue": overdue,
               "completed_month": completed_month, "availability": max(0, availability),
               "total_downtime": total_dt})

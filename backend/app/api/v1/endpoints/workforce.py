from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.helpers import add_crud_routes
from app.core.response import ok
from app.models.workforce import Worker, ShiftAssignment, AttendanceRecord

router = APIRouter()
add_crud_routes(router, Worker, "workforce/workers", search_fields=["employee_id", "name"], order_by="employee_id")
add_crud_routes(router, ShiftAssignment, "workforce/shift-assignments", order_by="day_of_week")
add_crud_routes(router, AttendanceRecord, "workforce/attendance", order_by="record_date")


@router.get("/{factory_id}/workforce/metrics")
def metrics(factory_id: int, day: str | None = None, db: Session = Depends(get_db)):
    target = date.fromisoformat(day) if day else date.today()
    recs = db.scalars(select(AttendanceRecord).where(
        AttendanceRecord.factory_id == factory_id, AttendanceRecord.record_date == target)).all()
    total = len(recs) or 1
    present = sum(1 for r in recs if r.status in ("present", "late"))
    absent = sum(1 for r in recs if r.status == "absent")
    ot = sum(r.overtime_hours or 0 for r in recs)
    headcount = db.scalar(select(func.count()).select_from(Worker).where(Worker.factory_id == factory_id, Worker.is_deleted == False)) or 0
    return ok({
        "present_pct": round(present / total * 100, 1),
        "absent_pct": round(absent / total * 100, 1),
        "ot_hours": round(ot, 1),
        "headcount": headcount,
        "date": target.isoformat(),
    })

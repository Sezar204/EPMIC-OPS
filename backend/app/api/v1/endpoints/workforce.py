Input
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.schemas.workforce import (
    WorkerCreate, WorkerUpdate, ShiftAssignmentCreate, AttendanceCreate,
)
from app.services.quality_maint_wf import WorkforceService
from app.repositories.modules import WorkerRepo, ShiftAssignmentRepo, AttendanceRepo
from app.models import Worker, ShiftAssignment, AttendanceRecord

router = APIRouter()


@router.get("/workers/{factory_id}")
def list_workers(factory_id: int, db: Session = Depends(get_db)):
    items = db.query(Worker).filter(Worker.factory_id == factory_id).all()
    return ok([{
        "id": i.id, "factory_id": i.factory_id, "employee_id": i.employee_id,
        "name": i.name, "department": i.department, "role": i.role,
        "skills": i.skills or [], "status": i.status,
    } for i in items], total=len(items))


@router.post("/workers/{factory_id}")
def create_worker(factory_id: int, payload: WorkerCreate, db: Session = Depends(get_db)):
    obj = Worker(factory_id=factory_id, **payload.model_dump())
    db.add(obj); db.commit()
    return ok({"id": obj.id, "employee_id": obj.employee_id}, "Worker created")


@router.put("/workers/{factory_id}/{worker_id}")
def update_worker(factory_id: int, worker_id: int, payload: WorkerUpdate, db: Session = Depends(get_db)):
    obj = WorkerRepo(db).get(worker_id)
    if not obj: raise HTTPException(404, "Not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit()
    return ok(None, "Worker updated")


@router.delete("/workers/{factory_id}/{worker_id}")
def delete_worker(factory_id: int, worker_id: int, db: Session = Depends(get_db)):
    ok_flag = WorkerRepo(db).delete(worker_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Not found")
    db.commit()
    return ok(None, "Worker deleted")


@router.get("/shift-assignments/{factory_id}")
def list_assignments(factory_id: int, week: str | None = None, db: Session = Depends(get_db)):
    items = db.query(ShiftAssignment).filter(ShiftAssignment.factory_id == factory_id).all()
    return ok([{
        "id": i.id, "factory_id": i.factory_id, "worker_id": i.worker_id,
        "shift_id": i.shift_id, "assignment_date": i.assignment_date.isoformat(),
        "line_id": i.line_id,
    } for i in items], total=len(items))


@router.post("/shift-assignments/{factory_id}")
def create_assignment(factory_id: int, payload: ShiftAssignmentCreate, db: Session = Depends(get_db)):
    obj = ShiftAssignment(factory_id=factory_id, **payload.model_dump())
    db.add(obj); db.commit()
    return ok({"id": obj.id}, "Assignment created")


@router.get("/attendance/{factory_id}")
def list_att(factory_id: int, date_str: str | None = None, db: Session = Depends(get_db)):
    d = date.fromisoformat(date_str) if date_str else date.today()
    items = db.query(AttendanceRecord).filter(
        AttendanceRecord.factory_id == factory_id, AttendanceRecord.attendance_date == d
    ).all()
    return ok([{
        "id": i.id, "worker_id": i.worker_id, "attendance_date": i.attendance_date.isoformat(),
        "scheduled_hours": i.scheduled_hours, "actual_hours": i.actual_hours,
        "ot_hours": i.ot_hours, "status": i.status, "notes": i.notes,
    } for i in items], total=len(items))


@router.post("/attendance/{factory_id}")
def create_att(factory_id: int, payload: AttendanceCreate, db: Session = Depends(get_db)):
    obj = AttendanceRecord(factory_id=factory_id, **payload.model_dump())
    db.add(obj); db.commit()
    return ok({"id": obj.id}, "Attendance recorded")


@router.get("/metrics/{factory_id}")
def metrics(factory_id: int, db: Session = Depends(get_db)):
    return ok(WorkforceService.metrics(db, factory_id))

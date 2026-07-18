Input
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.schemas.maintenance import (
    MaintenanceScheduleCreate, WorkOrderCreate, WorkOrderUpdate, BreakdownCreate,
)
from app.services.quality_maint_wf import MaintenanceService
from app.repositories.modules import WorkOrderRepo, MaintenanceScheduleRepo, BreakdownRepo
from app.models import (
    MaintenanceSchedule, MaintenanceWorkOrder, MachineBreakdown, Machine,
)

router = APIRouter()


@router.get("/schedules/{factory_id}")
def list_schedules(factory_id: int, db: Session = Depends(get_db)):
    items = db.query(MaintenanceSchedule).filter(MaintenanceSchedule.factory_id == factory_id).all()
    return ok([{
        "id": i.id, "factory_id": i.factory_id, "machine_id": i.machine_id,
        "type": i.type, "frequency_days": i.frequency_days,
        "next_due_date": i.next_due_date.isoformat(),
        "last_done_date": i.last_done_date.isoformat() if i.last_done_date else None,
        "description": i.description, "is_active": i.is_active,
    } for i in items], total=len(items))


@router.post("/schedules/{factory_id}")
def create_schedule(factory_id: int, payload: MaintenanceScheduleCreate, db: Session = Depends(get_db)):
    obj = MaintenanceSchedule(factory_id=factory_id, **payload.model_dump())
    db.add(obj); db.commit()
    return ok({"id": obj.id}, "Schedule created")


@router.get("/work-orders/{factory_id}")
def list_wos(factory_id: int, db: Session = Depends(get_db)):
    items = db.query(MaintenanceWorkOrder).filter(MaintenanceWorkOrder.factory_id == factory_id).all()
    return ok([{
        "id": i.id, "factory_id": i.factory_id, "machine_id": i.machine_id,
        "wo_number": i.wo_number, "type": i.type, "status": i.status, "priority": i.priority,
        "description": i.description, "assigned_to": i.assigned_to,
        "downtime_hours": i.downtime_hours,
        "started_at": i.started_at.isoformat() if i.started_at else None,
        "completed_at": i.completed_at.isoformat() if i.completed_at else None,
    } for i in items], total=len(items))


@router.post("/work-orders/{factory_id}")
def create_wo(factory_id: int, payload: WorkOrderCreate, db: Session = Depends(get_db)):
    obj = MaintenanceWorkOrder(factory_id=factory_id, **payload.model_dump())
    db.add(obj); db.commit()
    return ok({"id": obj.id}, "WO created")


@router.put("/work-orders/{factory_id}/{wo_id}")
def update_wo(factory_id: int, wo_id: int, payload: WorkOrderUpdate, db: Session = Depends(get_db)):
    obj = WorkOrderRepo(db).get(wo_id)
    if not obj: raise HTTPException(404, "Not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit()
    return ok(None, "WO updated")


@router.get("/breakdowns/{factory_id}")
def list_bds(factory_id: int, db: Session = Depends(get_db)):
    items = db.query(MachineBreakdown).filter(MachineBreakdown.factory_id == factory_id).all()
    return ok([{
        "id": i.id, "factory_id": i.factory_id, "machine_id": i.machine_id,
        "occurred_at": i.occurred_at.isoformat() if i.occurred_at else None,
        "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None,
        "cause_category": i.cause_category, "description": i.description,
    } for i in items], total=len(items))


@router.post("/breakdowns/{factory_id}")
def create_bd(factory_id: int, payload: BreakdownCreate, db: Session = Depends(get_db)):
    obj = MachineBreakdown(factory_id=factory_id, **payload.model_dump())
    db.add(obj); db.commit()
    return ok({"id": obj.id}, "Breakdown recorded")


@router.get("/assets/{factory_id}")
def assets(factory_id: int, db: Session = Depends(get_db)):
    return ok(MaintenanceService.asset_summary(db, factory_id))


@router.get("/metrics/{factory_id}")
def metrics(factory_id: int, db: Session = Depends(get_db)):
    return ok(MaintenanceService.metrics(db, factory_id))

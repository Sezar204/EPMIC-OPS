Input
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.services.operations import ProductionService
from app.repositories.modules import ProductionOrderRepo
from app.models import ProductionOrder

router = APIRouter()


@router.get("/orders/{factory_id}")
def list_orders(factory_id: int, db: Session = Depends(get_db)):
    items = db.query(ProductionOrder).filter(ProductionOrder.factory_id == factory_id).all()
    return ok([{
        "id": i.id, "factory_id": i.factory_id, "order_number": i.order_number,
        "product_id": i.product_id, "line_id": i.line_id,
        "planned_qty": i.planned_qty, "actual_qty": i.actual_qty,
        "planned_start": i.planned_start.isoformat(),
        "planned_end":   i.planned_end.isoformat(),
        "status": i.status, "priority": i.priority,
    } for i in items], total=len(items))


@router.post("/orders/{factory_id}")
def create_order(factory_id: int, payload: dict, db: Session = Depends(get_db)):
    obj = ProductionOrder(factory_id=factory_id, **payload)
    db.add(obj); db.commit()
    return ok({"id": obj.id}, "Created")


@router.put("/orders/{factory_id}/{order_id}")
def update_order(factory_id: int, order_id: int, payload: dict, db: Session = Depends(get_db)):
    obj = ProductionOrderRepo(db).get(order_id)
    if not obj or obj.factory_id != factory_id: raise HTTPException(404, "Not found")
    for k, v in payload.items(): setattr(obj, k, v)
    db.commit()
    return ok(None, "Updated")


@router.delete("/orders/{factory_id}/{order_id}")
def delete_order(factory_id: int, order_id: int, db: Session = Depends(get_db)):
    ok_flag = ProductionOrderRepo(db).delete(order_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Not found")
    db.commit()
    return ok(None, "Deleted")


@router.get("/schedule/daily/{factory_id}")
def daily(factory_id: int, date_str: str | None = None, db: Session = Depends(get_db)):
    d = date.fromisoformat(date_str) if date_str else date.today()
    return ok(ProductionService.daily_schedule(db, factory_id, d))


@router.get("/schedule/weekly/{factory_id}")
def weekly(factory_id: int, week: str | None = None, db: Session = Depends(get_db)):
    d = date.fromisoformat(week) if week else date.today()
    return ok(ProductionService.weekly_schedule(db, factory_id, d))


@router.get("/capacity/analysis/{factory_id}")
def analysis(factory_id: int, db: Session = Depends(get_db)):
    return ok(ProductionService.capacity_analysis(db, factory_id))

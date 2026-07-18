from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.helpers import add_crud_routes
from app.core.response import ok
from app.models.production import Shift

router = APIRouter()


@router.get("/{factory_id}/master-data/shifts/summary")
def summary(factory_id: int, db: Session = Depends(get_db)):
    f = factory_id
    total = db.scalar(select(func.count()).select_from(Shift).where(
        Shift.factory_id == f, Shift.is_deleted == False)) or 0
    active = db.scalar(select(func.count()).select_from(Shift).where(
        Shift.factory_id == f, Shift.is_deleted == False, Shift.is_active == True)) or 0
    headcount = db.scalar(select(func.coalesce(func.sum(Shift.headcount), 0)).select_from(Shift).where(
        Shift.factory_id == f, Shift.is_deleted == False)) or 0
    return ok({"total": total, "active": active, "headcount": headcount})


add_crud_routes(router, Shift, "master-data/shifts",
                search_fields=["name"], order_by="name")

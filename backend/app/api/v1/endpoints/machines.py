from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.helpers import add_crud_routes
from app.core.response import ok
from app.models.production import Machine

router = APIRouter()


@router.get("/{factory_id}/master-data/machines/summary")
def summary(factory_id: int, db: Session = Depends(get_db)):
    f = factory_id
    total = db.scalar(select(func.count()).select_from(Machine).where(
        Machine.factory_id == f, Machine.is_deleted == False)) or 0
    active = db.scalar(select(func.count()).select_from(Machine).where(
        Machine.factory_id == f, Machine.is_deleted == False, Machine.status == "active")) or 0
    maintenance = db.scalar(select(func.count()).select_from(Machine).where(
        Machine.factory_id == f, Machine.is_deleted == False, Machine.status == "maintenance")) or 0
    down = db.scalar(select(func.count()).select_from(Machine).where(
        Machine.factory_id == f, Machine.is_deleted == False, Machine.status == "down")) or 0
    return ok({"total": total, "active": active, "maintenance": maintenance, "down": down})


add_crud_routes(router, Machine, "master-data/machines",
                search_fields=["code", "name"], order_by="code")

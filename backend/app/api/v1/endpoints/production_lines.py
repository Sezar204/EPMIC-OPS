from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.helpers import add_crud_routes
from app.core.response import ok
from app.models.production import ProductionLine

router = APIRouter()


@router.get("/{factory_id}/master-data/production-lines/summary")
def summary(factory_id: int, db: Session = Depends(get_db)):
    f = factory_id
    total = db.scalar(select(func.count()).select_from(ProductionLine).where(
        ProductionLine.factory_id == f, ProductionLine.is_deleted == False)) or 0
    active = db.scalar(select(func.count()).select_from(ProductionLine).where(
        ProductionLine.factory_id == f, ProductionLine.is_deleted == False, ProductionLine.status == "active")) or 0
    idle = db.scalar(select(func.count()).select_from(ProductionLine).where(
        ProductionLine.factory_id == f, ProductionLine.is_deleted == False, ProductionLine.status == "idle")) or 0
    down = db.scalar(select(func.count()).select_from(ProductionLine).where(
        ProductionLine.factory_id == f, ProductionLine.is_deleted == False, ProductionLine.status == "down")) or 0
    return ok({"total": total, "active": active, "idle": idle, "down": down})


add_crud_routes(router, ProductionLine, "master-data/production-lines",
                search_fields=["code", "name"], order_by="code")

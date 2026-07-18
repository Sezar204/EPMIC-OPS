from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.helpers import add_crud_routes
from app.core.response import ok
from app.models.warehouse import Warehouse

router = APIRouter()


@router.get("/{factory_id}/master-data/warehouses/summary")
def summary(factory_id: int, db: Session = Depends(get_db)):
    f = factory_id
    whs = db.scalars(select(Warehouse).where(
        Warehouse.factory_id == f, Warehouse.is_deleted == False)).all()
    total = len(whs)
    total_capacity = sum(w.total_capacity for w in whs)
    types = {}
    for w in whs:
        types[w.type] = types.get(w.type, 0) + 1
    return ok({"total": total, "total_capacity": total_capacity, "types": types})


add_crud_routes(router, Warehouse, "master-data/warehouses",
                search_fields=["code", "name"], order_by="code")

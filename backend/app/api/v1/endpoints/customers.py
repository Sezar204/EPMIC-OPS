from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.helpers import add_crud_routes
from app.core.response import ok
from app.models.sales import Customer

router = APIRouter()


@router.get("/{factory_id}/master-data/customers/summary")
def summary(factory_id: int, db: Session = Depends(get_db)):
    f = factory_id
    total = db.scalar(select(func.count()).select_from(Customer).where(
        Customer.factory_id == f, Customer.is_deleted == False)) or 0
    b2b = db.scalar(select(func.count()).select_from(Customer).where(
        Customer.factory_id == f, Customer.is_deleted == False, Customer.type == "b2b")) or 0
    b2c = db.scalar(select(func.count()).select_from(Customer).where(
        Customer.factory_id == f, Customer.is_deleted == False, Customer.type == "b2c")) or 0
    dist = db.scalar(select(func.count()).select_from(Customer).where(
        Customer.factory_id == f, Customer.is_deleted == False, Customer.type == "distributor")) or 0
    return ok({"total": total, "b2b": b2b, "b2c": b2c, "distributors": dist})


add_crud_routes(router, Customer, "master-data/customers",
                search_fields=["code", "name"], order_by="code")

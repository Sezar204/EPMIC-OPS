from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.helpers import add_crud_routes
from app.core.response import ok
from app.models.product import Product, BOMHeader

router = APIRouter()


@router.get("/{factory_id}/master-data/products/summary")
def summary(factory_id: int, db: Session = Depends(get_db)):
    f = factory_id
    total = db.scalar(select(func.count()).select_from(Product).where(
        Product.factory_id == f, Product.is_deleted == False)) or 0
    finished = db.scalar(select(func.count()).select_from(Product).where(
        Product.factory_id == f, Product.is_deleted == False, Product.type == "finished")) or 0
    semi = db.scalar(select(func.count()).select_from(Product).where(
        Product.factory_id == f, Product.is_deleted == False, Product.type == "semi-finished")) or 0
    with_bom = db.scalar(select(func.count()).select_from(BOMHeader).where(
        BOMHeader.factory_id == f, BOMHeader.is_deleted == False)) or 0
    return ok({"total": total, "finished": finished, "semi_finished": semi, "with_bom": with_bom})


add_crud_routes(router, Product, "master-data/products",
                search_fields=["sku", "name"], order_by="sku")

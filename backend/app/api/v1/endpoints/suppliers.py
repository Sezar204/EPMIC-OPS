from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.helpers import add_crud_routes
from app.core.response import ok
from app.models.procurement import Supplier, SupplierMaterial
from app.models.inventory import RawMaterial
from app.core.crud import serialize

router = APIRouter()


def _with_materials(row: dict, db: Session, fid: int) -> dict:
    links = db.scalars(select(SupplierMaterial).where(SupplierMaterial.supplier_id == row["id"])).all()
    out = []
    for l in links:
        rm = db.get(RawMaterial, l.material_id)
        out.append({"material_id": l.material_id, "material_name": rm.name if rm else "-",
                    "is_preferred": l.is_preferred, "lead_time_days": l.lead_time_days,
                    "unit_price": l.unit_price})
    row["materials"] = out
    return row


@router.get("/{factory_id}/master-data/suppliers/summary")
def summary(factory_id: int, db: Session = Depends(get_db)):
    f = factory_id
    total = db.scalar(select(func.count()).select_from(Supplier).where(
        Supplier.factory_id == f, Supplier.is_deleted == False)) or 0
    active = db.scalar(select(func.count()).select_from(Supplier).where(
        Supplier.factory_id == f, Supplier.is_deleted == False, Supplier.status == "active")) or 0
    blacklisted = db.scalar(select(func.count()).select_from(Supplier).where(
        Supplier.factory_id == f, Supplier.is_deleted == False, Supplier.status == "blacklisted")) or 0
    avg = db.scalar(select(func.coalesce(func.avg(Supplier.rating), 0)).select_from(Supplier).where(
        Supplier.factory_id == f, Supplier.is_deleted == False)) or 0
    return ok({"total": total, "active": active, "blacklisted": blacklisted, "avg_rating": round(float(avg), 2)})


add_crud_routes(router, Supplier, "master-data/suppliers",
                search_fields=["code", "name"], order_by="code", transform=_with_materials)

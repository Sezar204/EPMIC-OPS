from fastapi import APIRouter, Depends, Body
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.crud import serialize
from app.core.response import ok, fail
from app.models.product import Product, BOMHeader, BOMLine
from app.models.inventory import RawMaterial

router = APIRouter()


def _with_product(row: dict, db: Session, fid: int) -> dict:
    p = db.get(Product, row.get("product_id"))
    if p:
        row["product_name"] = p.name
        row["product_sku"] = p.sku
    return row


@router.get("/{factory_id}/master-data/bom")
def list_bom(factory_id: int, page: int = 1, page_size: int = 20, search: str | None = None,
             db: Session = Depends(get_db)):
    from app.core.crud import list_resources
    rows, total = list_resources(db, BOMHeader, factory_id, page=page, page_size=page_size,
                                 search=search, search_fields=["name", "version"], order_by="id")
    rows = [_with_product(r, db, factory_id) for r in rows]
    return ok(rows, "OK", total=total, page=page, page_size=page_size)


@router.get("/{factory_id}/master-data/bom/summary")
def summary(factory_id: int, db: Session = Depends(get_db)):
    base = select(BOMHeader).where(BOMHeader.factory_id == factory_id, BOMHeader.is_deleted == False)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    active = db.scalar(select(func.count()).select_from(base.subquery()).where(BOMHeader.status == "active")) or 0
    products_covered = db.scalar(select(func.count(func.distinct(BOMHeader.product_id)).select_from(base.subquery())) or 0) or 0
    return ok({"total": total, "active": active, "products_covered": products_covered})


@router.post("/{factory_id}/master-data/bom")
def create_bom(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    lines = data.pop("lines", [])
    header = BOMHeader(factory_id=factory_id,
                       product_id=data["product_id"],
                       version=data.get("version", "1.0"),
                       name=data.get("name", ""),
                       status=data.get("status", "active"),
                       yield_pct=data.get("yield_pct", 100),
                       effective_date=data.get("effective_date"),
                       notes=data.get("notes"))
    db.add(header)
    db.flush()
    for seq, l in enumerate(lines, start=1):
        db.add(BOMLine(bom_id=header.id, material_id=l["material_id"],
                       quantity_required=l["quantity_required"], unit=l.get("unit", "kg"),
                       loss_factor_pct=l.get("loss_factor_pct", 0),
                       is_alternative=l.get("is_alternative", False),
                       alt_material_id=l.get("alt_material_id"),
                       sequence_no=l.get("sequence_no", seq)))
    db.commit()
    return ok(serialize(header), "BOM created")


@router.get("/{factory_id}/master-data/bom/{rid}")
def get_bom(factory_id: int, rid: int, db: Session = Depends(get_db)):
    header = db.get(BOMHeader, rid)
    if not header or header.factory_id != factory_id:
        return fail("Not found")
    row = serialize(header)
    line_rows = db.scalars(select(BOMLine).where(BOMLine.bom_id == rid).order_by(BOMLine.sequence_no)).all()
    out_lines = []
    for l in line_rows:
        lr = serialize(l)
        rm = db.get(RawMaterial, l.material_id)
        if rm:
            lr["material_name"] = rm.name
            lr["material_code"] = rm.code
        out_lines.append(lr)
    row["lines"] = out_lines
    _with_product(row, db, factory_id)
    return ok(row)


@router.put("/{factory_id}/master-data/bom/{rid}")
def update_bom(factory_id: int, rid: int, data: dict = Body(...), db: Session = Depends(get_db)):
    header = db.get(BOMHeader, rid)
    if not header or header.factory_id != factory_id:
        return fail("Not found")
    for k, v in data.items():
        if k in ("lines", "id", "factory_id"):
            continue
        setattr(header, k, v)
    if "lines" in data:
        db.query(BOMLine).where(BOMLine.bom_id == rid).delete()
        for seq, l in enumerate(data["lines"], start=1):
            db.add(BOMLine(bom_id=rid, material_id=l["material_id"],
                           quantity_required=l["quantity_required"], unit=l.get("unit", "kg"),
                           loss_factor_pct=l.get("loss_factor_pct", 0),
                           is_alternative=l.get("is_alternative", False),
                           alt_material_id=l.get("alt_material_id"),
                           sequence_no=l.get("sequence_no", seq)))
    db.commit()
    return ok(serialize(header), "BOM updated")


@router.delete("/{factory_id}/master-data/bom/{rid}")
def delete_bom(factory_id: int, rid: int, db: Session = Depends(get_db)):
    header = db.get(BOMHeader, rid)
    if not header or header.factory_id != factory_id:
        return fail("Not found")
    header.is_deleted = True
    db.commit()
    return ok(None, "Deleted")


@router.post("/{factory_id}/master-data/bom/cost-preview")
def cost_preview(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    total = 0.0
    for l in data.get("lines", []):
        rm = db.get(RawMaterial, l.get("material_id"))
        if rm:
            qty = float(l.get("quantity_required", 0)) * (1 + float(l.get("loss_factor_pct", 0)) / 100)
            total += rm.standard_cost * qty
    return ok({"total_material_cost": round(total, 2)})

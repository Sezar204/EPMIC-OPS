from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.crud import list_resources, create_resource, serialize
from app.core.response import ok, fail
from app.models.kpi import KPIDefinition, KPIValue

router = APIRouter()


@router.get("/{factory_id}/kpis")
def list_kpis(factory_id: int, category: str | None = None, period_type: str = "daily",
              db: Session = Depends(get_db)):
    defs = db.scalars(select(KPIDefinition).where(
        KPIDefinition.factory_id == factory_id, KPIDefinition.is_active == True)).all()
    if category:
        defs = [d for d in defs if d.category == category]
    out = []
    for d in defs:
        vals = db.scalars(select(KPIValue).where(
            KPIValue.kpi_id == d.id, KPIValue.period_type == period_type
        ).order_by(KPIValue.period_date)).all()
        latest = vals[-1] if vals else None
        trend = [v.value for v in vals[-30:]]
        out.append({
            "id": d.id, "code": d.code, "name": d.name, "category": d.category,
            "unit": d.unit, "target_value": d.target_value, "display_format": d.display_format,
            "higher_is_better": d.higher_is_better, "is_custom": d.is_custom,
            "value": latest.value if latest else 0, "status": latest.status if latest else "good",
            "trend": trend,
        })
    return ok(out)


@router.get("/{factory_id}/kpis/{category}")
def kpis_by_category(factory_id: int, category: str, period_type: str = "daily", db: Session = Depends(get_db)):
    defs = db.scalars(select(KPIDefinition).where(
        KPIDefinition.factory_id == factory_id, KPIDefinition.category == category, KPIDefinition.is_active == True)).all()
    out = []
    for d in defs:
        latest = db.scalars(select(KPIValue).where(
            KPIValue.kpi_id == d.id, KPIValue.period_type == period_type).order_by(KPIValue.period_date.desc())).first()
        out.append({"code": d.code, "name": d.name, "value": latest.value if latest else 0,
                    "status": latest.status if latest else "good", "target": d.target_value})
    return ok(out)


@router.post("/{factory_id}/kpis/custom")
def create_custom(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    obj = create_resource(db, KPIDefinition, data, factory_id)
    return ok(obj, "Custom KPI created")

Input
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.models import KPIDefinition, KPIValue

router = APIRouter()


@router.get("/")
def list_all(db: Session = Depends(get_db)):
    items = db.scalars(select(KPIDefinition).where(KPIDefinition.is_active == True)).all()  # noqa: E712
    return ok([{
        "id": i.id, "code": i.code, "name": i.name, "category": i.category,
        "unit": i.unit, "target_value": i.target_value,
        "warning_threshold": i.warning_threshold,
        "critical_threshold": i.critical_threshold,
        "higher_is_better": i.higher_is_better,
        "display_format": i.display_format,
    } for i in items], total=len(items))


@router.get("/{category}")
def by_category(category: str, db: Session = Depends(get_db)):
    items = db.scalars(select(KPIDefinition).where(
        KPIDefinition.category == category, KPIDefinition.is_active == True  # noqa: E712
    )).all()
    return ok([{"id": i.id, "code": i.code, "name": i.name} for i in items], total=len(items))

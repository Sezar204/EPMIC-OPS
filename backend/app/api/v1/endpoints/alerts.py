from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.crud import serialize
from app.core.response import ok, fail
from app.models.alert import Alert

router = APIRouter()


@router.get("/{factory_id}/alerts")
def list_alerts(factory_id: int, severity: str | None = None, is_resolved: bool | None = None,
                is_read: bool | None = None, source_module: str | None = None,
                limit: int = 50, db: Session = Depends(get_db)):
    stmt = select(Alert).where(Alert.factory_id == factory_id)
    if severity:
        stmt = stmt.where(Alert.severity == severity)
    if is_resolved is not None:
        stmt = stmt.where(Alert.is_resolved == is_resolved)
    if is_read is not None:
        stmt = stmt.where(Alert.is_read == is_read)
    if source_module:
        stmt = stmt.where(Alert.source_module == source_module)
    stmt = stmt.order_by(Alert.created_at.desc()).limit(limit)
    rows = db.scalars(stmt).all()
    return ok([serialize(r) for r in rows])


@router.put("/{factory_id}/alerts/{alert_id}/read")
def mark_read(factory_id: int, alert_id: int, db: Session = Depends(get_db)):
    a = db.get(Alert, alert_id)
    if not a or a.factory_id != factory_id:
        return fail("Not found")
    a.is_read = True
    db.commit()
    return ok(None, "Marked read")


@router.put("/{factory_id}/alerts/{alert_id}/resolve")
def resolve(factory_id: int, alert_id: int, db: Session = Depends(get_db)):
    a = db.get(Alert, alert_id)
    if not a or a.factory_id != factory_id:
        return fail("Not found")
    a.is_resolved = True
    a.resolved_at = __import__("datetime").datetime.utcnow()
    db.commit()
    return ok(None, "Resolved")

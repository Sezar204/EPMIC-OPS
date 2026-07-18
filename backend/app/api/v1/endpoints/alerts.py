Input
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.models import Alert

router = APIRouter()


@router.get("/")
def list_all(limit: int = 200, db: Session = Depends(get_db)):
    items = db.scalars(select(Alert).order_by(Alert.created_at.desc()).limit(limit)).all()
    return ok([{
        "id": a.id, "factory_id": a.factory_id, "alert_type": a.alert_type,
        "severity": a.severity, "title": a.title, "message": a.message,
        "is_read": a.is_read, "is_resolved": a.is_resolved,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    } for a in items], total=len(items))

Input
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.models import Decision

router = APIRouter()


@router.get("/")
def list_all(limit: int = 200, db: Session = Depends(get_db)):
    items = db.scalars(select(Decision).order_by(Decision.created_at.desc()).limit(limit)).all()
    return ok([{
        "id": d.id, "factory_id": d.factory_id, "decision_type": d.decision_type,
        "title": d.title, "description": d.description, "recommendation": d.recommendation,
        "impact_summary": d.impact_summary, "status": d.status, "priority": d.priority,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    } for d in items], total=len(items))

from fastapi import APIRouter, Depends, Body
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.crud import serialize
from app.core.response import ok, fail
from app.models.alert import Decision

router = APIRouter()


@router.get("/{factory_id}/decisions/pending")
def pending(factory_id: int, db: Session = Depends(get_db)):
    rows = db.scalars(select(Decision).where(
        Decision.factory_id == factory_id, Decision.status == "pending"
    ).order_by(Decision.priority != "urgent", Decision.created_at.desc())).all()
    return ok([serialize(r) for r in rows])


def _decide(factory_id: int, rid: int, status: str, db: Session):
    d = db.get(Decision, rid)
    if not d or d.factory_id != factory_id:
        return None
    d.status = status
    d.decided_at = __import__("datetime").datetime.utcnow()
    db.commit()
    return d


@router.put("/{factory_id}/decisions/{rid}/approve")
def approve(factory_id: int, rid: int, data: dict = Body(default={}), db: Session = Depends(get_db)):
    d = _decide(factory_id, rid, "approved", db)
    if not d:
        return fail("Not found")
    if data.get("notes"):
        d.decision_notes = data["notes"]
    return ok(serialize(d), "Approved")


@router.put("/{factory_id}/decisions/{rid}/reject")
def reject(factory_id: int, rid: int, data: dict = Body(default={}), db: Session = Depends(get_db)):
    d = _decide(factory_id, rid, "rejected", db)
    if not d:
        return fail("Not found")
    if data.get("notes"):
        d.decision_notes = data["notes"]
    return ok(serialize(d), "Rejected")

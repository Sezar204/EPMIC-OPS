Input
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.services.corporate import CorporateService

router = APIRouter()


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    return ok(CorporateService.overview(db))


@router.get("/critical-alerts")
def critical_alerts(db: Session = Depends(get_db)):
    return ok(CorporateService.critical_alerts(db))


@router.get("/pending-decisions")
def pending_decisions(db: Session = Depends(get_db)):
    return ok(CorporateService.pending_decisions(db))


@router.get("/group-kpis")
def group_kpis(db: Session = Depends(get_db)):
    return ok(CorporateService.group_kpis(db))

quality.py
Input
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.schemas.quality import QualityCheckCreate, NCRCreate, CAPACreate
from app.services.quality_maint_wf import QualityService
from app.models import (
    QualityCheck, NonConformanceReport, CAPARecord,
)

router = APIRouter()


@router.get("/checks/{factory_id}")
def list_checks(factory_id: int, db: Session = Depends(get_db)):
    items = db.query(QualityCheck).filter(QualityCheck.factory_id == factory_id).all()
    return ok([{
        "id": i.id, "factory_id": i.factory_id, "check_type": i.check_type,
        "status": i.status, "sample_size": i.sample_size, "defects_found": i.defects_found,
        "defect_rate_pct": i.defect_rate_pct, "decision": i.decision,
        "checked_at": i.checked_at.isoformat() if i.checked_at else None,
        "product_id": i.product_id, "material_id": i.material_id,
    } for i in items], total=len(items))


@router.post("/checks/{factory_id}")
def create_check(factory_id: int, payload: QualityCheckCreate, db: Session = Depends(get_db)):
    qc = QualityService.create_check(db, factory_id, payload)
    return ok({"id": qc.id}, "Check recorded")


@router.get("/ncr/{factory_id}")
def list_ncr(factory_id: int, db: Session = Depends(get_db)):
    items = db.query(NonConformanceReport).filter(NonConformanceReport.factory_id == factory_id).all()
    return ok([{
        "id": i.id, "factory_id": i.factory_id, "ncr_number": i.ncr_number,
        "title": i.title, "severity": i.severity, "status": i.status,
        "created_at": i.created_at.isoformat() if i.created_at else None,
        "closed_at": i.closed_at.isoformat() if i.closed_at else None,
    } for i in items], total=len(items))


@router.post("/ncr/{factory_id}")
def create_ncr(factory_id: int, payload: NCRCreate, db: Session = Depends(get_db)):
    from datetime import date
    obj = NonConformanceReport(
        factory_id=factory_id,
        ncr_number=f"NCR-{date.today().strftime('%Y%m%d')}-{int(__import__('time').time())%10000:04d}",
        **payload.model_dump(),
    )
    db.add(obj); db.commit()
    return ok({"id": obj.id}, "NCR created")


@router.get("/capa/{factory_id}")
def list_capa(factory_id: int, db: Session = Depends(get_db)):
    items = db.query(CAPARecord).filter(CAPARecord.factory_id == factory_id).all()
    return ok([{
        "id": i.id, "factory_id": i.factory_id, "capa_number": i.capa_number,
        "type": i.type, "description": i.description, "responsible_person": i.responsible_person,
        "due_date": i.due_date.isoformat() if i.due_date else None,
        "completed_at": i.completed_at.isoformat() if i.completed_at else None,
        "status": i.status,
    } for i in items], total=len(items))


@router.post("/capa/{factory_id}")
def create_capa(factory_id: int, payload: CAPACreate, db: Session = Depends(get_db)):
    from datetime import date
    obj = CAPARecord(
        factory_id=factory_id,
        capa_number=f"CAPA-{date.today().strftime('%Y%m%d')}-{int(__import__('time').time())%10000:04d}",
        **payload.model_dump(),
    )
    db.add(obj); db.commit()
    return ok({"id": obj.id}, "CAPA created")


@router.get("/metrics/{factory_id}")
def metrics(factory_id: int, db: Session = Depends(get_db)):
    return ok(QualityService.metrics(db, factory_id))

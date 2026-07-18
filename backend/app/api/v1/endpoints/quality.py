from fastapi import APIRouter, Depends, Body
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.crud import list_resources, create_resource, get_resource, update_resource, delete_resource, serialize
from app.core.response import ok, fail
from app.models.quality import QualityCheck, NonConformanceReport, CAPARecord

router = APIRouter()


@router.get("/{factory_id}/quality/checks")
def list_checks(factory_id: int, page: int = 1, page_size: int = 20,
                check_type: str | None = None, status: str | None = None, db: Session = Depends(get_db)):
    filters = {}
    if check_type: filters["check_type"] = check_type
    if status: filters["status"] = status
    rows, total = list_resources(db, QualityCheck, factory_id, page=page, page_size=page_size,
                                 filters=filters, order_by="checked_at")
    return ok(rows, "OK", total=total, page=page, page_size=page_size)


@router.post("/{factory_id}/quality/checks")
def create_check(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    sample = int(data.get("sample_size", 0) or 0)
    defects = int(data.get("defects_found", 0) or 0)
    data["defect_rate_pct"] = round(defects / sample * 100, 2) if sample else 0
    if "status" not in data:
        data["status"] = "passed" if defects == 0 else ("failed" if data["defect_rate_pct"] > 5 else "passed")
    obj = create_resource(db, QualityCheck, data, factory_id)
    return ok(obj, "Check recorded")


@router.get("/{factory_id}/quality/checks/{rid}")
def get_check(factory_id: int, rid: int, db: Session = Depends(get_db)):
    obj = get_resource(db, QualityCheck, rid, factory_id)
    return ok(obj) if obj else fail("Not found")


@router.put("/{factory_id}/quality/checks/{rid}")
def update_check(factory_id: int, rid: int, data: dict = Body(...), db: Session = Depends(get_db)):
    obj = update_resource(db, QualityCheck, rid, data, factory_id)
    return ok(obj, "Updated") if obj else fail("Not found")


@router.delete("/{factory_id}/quality/checks/{rid}")
def delete_check(factory_id: int, rid: int, db: Session = Depends(get_db)):
    return ok(None, "Deleted") if delete_resource(db, QualityCheck, rid, factory_id) else fail("Not found")


# ---- NCR ----
@router.get("/{factory_id}/quality/ncr")
def list_ncr(factory_id: int, db: Session = Depends(get_db)):
    rows, total = list_resources(db, NonConformanceReport, factory_id, order_by="opened_at")
    return ok(rows, "OK", total=total)


@router.post("/{factory_id}/quality/ncr")
def create_ncr(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    n = db.scalars(select(NonConformanceReport).where(NonConformanceReport.factory_id == factory_id)).all()
    data["ncr_number"] = f"NCR-2026-{len(n) + 1:03d}"
    obj = create_resource(db, NonConformanceReport, data, factory_id)
    return ok(obj, "NCR created")


@router.get("/{factory_id}/quality/ncr/{rid}")
def get_ncr(factory_id: int, rid: int, db: Session = Depends(get_db)):
    obj = get_resource(db, NonConformanceReport, rid, factory_id)
    return ok(obj) if obj else fail("Not found")


@router.put("/{factory_id}/quality/ncr/{rid}")
def update_ncr(factory_id: int, rid: int, data: dict = Body(...), db: Session = Depends(get_db)):
    obj = update_resource(db, NonConformanceReport, rid, data, factory_id)
    return ok(obj, "Updated") if obj else fail("Not found")


# ---- CAPA ----
@router.get("/{factory_id}/quality/capa")
def list_capa(factory_id: int, db: Session = Depends(get_db)):
    rows, total = list_resources(db, CAPARecord, factory_id, order_by="due_date")
    return ok(rows, "OK", total=total)


@router.post("/{factory_id}/quality/capa")
def create_capa(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    c = db.scalars(select(CAPARecord).where(CAPARecord.factory_id == factory_id)).all()
    data["capa_number"] = f"CAPA-2026-{len(c) + 1:03d}"
    obj = create_resource(db, CAPARecord, data, factory_id)
    return ok(obj, "CAPA created")


@router.get("/{factory_id}/quality/capa/{rid}")
def get_capa(factory_id: int, rid: int, db: Session = Depends(get_db)):
    obj = get_resource(db, CAPARecord, rid, factory_id)
    return ok(obj) if obj else fail("Not found")


@router.put("/{factory_id}/quality/capa/{rid}")
def update_capa(factory_id: int, rid: int, data: dict = Body(...), db: Session = Depends(get_db)):
    obj = update_resource(db, CAPARecord, rid, data, factory_id)
    return ok(obj, "Updated") if obj else fail("Not found")


@router.get("/{factory_id}/quality/metrics")
def metrics(factory_id: int, db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(QualityCheck).where(QualityCheck.factory_id == factory_id)) or 0
    failed = db.scalar(select(func.count()).select_from(QualityCheck).where(QualityCheck.factory_id == factory_id, QualityCheck.status == "failed")) or 0
    closed_capa = db.scalar(select(func.count()).select_from(CAPARecord).where(CAPARecord.factory_id == factory_id, CAPARecord.status == "closed")) or 0
    total_capa = db.scalar(select(func.count()).select_from(CAPARecord).where(CAPARecord.factory_id == factory_id)) or 0
    defect_rate = round(failed / total * 100, 2) if total else 0
    fpy = round((total - failed) / total * 100, 1) if total else 100
    closure = round(closed_capa / total_capa * 100, 1) if total_capa else 100
    return ok({"defect_rate": defect_rate, "fpy": fpy, "capa_closure": closure, "total_checks": total})

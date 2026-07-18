Input
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.services.reports import ReportService

router = APIRouter()


@router.get("/library")
def library():
    return ok(ReportService.library())


@router.post("/generate")
def generate(
    report_id: str,
    date_from: Optional[date] = None,
    date_to:   Optional[date] = None,
    fmt:       str  = Query("excel", pattern="^(excel|csv|pdf)$"),
    db: Session = Depends(get_db),
):
    data, media, filename = ReportService.generate(db, report_id, date_from, date_to, fmt)
    return Response(content=data, media_type=media,
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})

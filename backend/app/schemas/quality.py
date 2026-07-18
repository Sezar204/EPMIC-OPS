Input
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas import ORMBase


class QualityCheckCreate(BaseModel):
    check_type: str
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    product_id: Optional[int] = None
    material_id: Optional[int] = None
    sample_size: int
    defects_found: int = 0
    decision: Optional[str] = None
    notes: Optional[str] = None


class QualityCheckUpdate(BaseModel):
    status: Optional[str] = None
    decision: Optional[str] = None
    notes: Optional[str] = None


class QualityCheckRead(ORMBase):
    id: int
    factory_id: int
    check_type: str
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    product_id: Optional[int] = None
    material_id: Optional[int] = None
    status: str
    checked_at: Optional[datetime] = None
    sample_size: int
    defects_found: int
    defect_rate_pct: float
    decision: Optional[str] = None


class NCRCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "medium"
    quality_check_id: Optional[int] = None
    root_cause: Optional[str] = None
    notes: Optional[str] = None


class NCRRead(ORMBase):
    id: int
    factory_id: int
    ncr_number: str
    title: str
    severity: str
    status: str
    quality_check_id: Optional[int] = None
    closed_at: Optional[datetime] = None


class CAPACreate(BaseModel):
    type: str = "corrective"
    ncr_id: Optional[int] = None
    description: str
    responsible_person: Optional[str] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class CAPARead(ORMBase):
    id: int
    factory_id: int
    capa_number: str
    type: str
    ncr_id: Optional[int] = None
    description: str
    responsible_person: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str


class QualityMetrics(BaseModel):
    factory_id: int
    defect_rate_pct: float
    first_pass_yield_pct: float
    capa_closure_rate_pct: float
    supplier_quality_pct: float
    weekly_defect_trend: List[dict] = []
    top_defect_categories: List[dict] = []

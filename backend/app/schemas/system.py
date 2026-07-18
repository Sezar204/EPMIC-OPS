Input
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas import ORMBase


class KPIDefinitionCreate(BaseModel):
    code: str
    name: str
    category: str
    formula: Optional[str] = None
    unit: Optional[str] = None
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    higher_is_better: bool = True
    display_format: str = "number"


class KPIDefinitionRead(ORMBase):
    id: int
    code: str
    name: str
    category: str
    unit: Optional[str] = None
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    higher_is_better: bool
    display_format: str
    is_custom: bool


class KPIValueRead(ORMBase):
    id: int
    kpi_id: int
    factory_id: int
    period_type: str
    period_date: datetime
    value: float
    status: str


class AlertRead(ORMBase):
    id: int
    factory_id: int
    alert_type: str
    severity: str
    title: str
    message: Optional[str] = None
    source_module: Optional[str] = None
    is_read: bool
    is_resolved: bool
    created_at: datetime


class DecisionRead(ORMBase):
    id: int
    factory_id: int
    decision_type: str
    title: str
    description: Optional[str] = None
    recommendation: Optional[str] = None
    impact_summary: Optional[dict] = None
    status: str
    priority: str
    created_at: datetime


class BackupInfo(BaseModel):
    filename: str
    backup_type: str
    file_size_bytes: int
    created_at: datetime
    status: str
    file_path: str


class SystemInfo(BaseModel):
    app_name: str
    app_version: str
    os: str
    db_path: str
    db_size_bytes: int
    backup_count: int
    uptime_seconds: float


class IntegrityResult(BaseModel):
    status: str
    issues: List[str] = []


class ReportDef(BaseModel):
    id: str
    name: str
    category: str
    description: str
    parameters: List[str] = []


class ReportRequest(BaseModel):
    report_id: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    filters: dict = {}


class DashboardSummary(BaseModel):
    factory_id: int
    health_score: float
    critical_alerts: int
    pending_decisions: int
    plan_adherence_pct: float
    production_today: dict
    kpis: dict

Input
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas import ORMBase


class MaintenanceScheduleCreate(BaseModel):
    machine_id: int
    type: str = "preventive"
    frequency_days: int = 30
    next_due_date: date
    description: Optional[str] = None
    estimated_hours: float = 2


class MaintenanceScheduleRead(ORMBase):
    id: int
    factory_id: int
    machine_id: int
    type: str
    frequency_days: int
    next_due_date: date
    last_done_date: Optional[date] = None
    description: Optional[str] = None
    is_active: int


class WorkOrderCreate(BaseModel):
    machine_id: int
    wo_number: str
    type: str = "preventive"
    priority: str = "medium"
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    root_cause: Optional[str] = None
    notes: Optional[str] = None


class WorkOrderUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    downtime_hours: Optional[float] = None
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    notes: Optional[str] = None


class WorkOrderRead(ORMBase):
    id: int
    factory_id: int
    machine_id: int
    wo_number: str
    type: str
    status: str
    priority: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    downtime_hours: float


class BreakdownCreate(BaseModel):
    machine_id: int
    occurred_at: datetime
    cause_category: Optional[str] = None
    description: Optional[str] = None
    impact_on_production: Optional[str] = None
    resolved_at: Optional[datetime] = None


class BreakdownRead(ORMBase):
    id: int
    factory_id: int
    machine_id: int
    work_order_id: Optional[int] = None
    occurred_at: datetime
    resolved_at: Optional[datetime] = None
    cause_category: Optional[str] = None
    description: Optional[str] = None


class AssetSummary(BaseModel):
    machine_id: int
    code: str
    name: str
    line_name: Optional[str] = None
    status: str
    availability_pct: float
    mtbf_hours: float
    mttr_hours: float
    next_pm_date: Optional[date] = None
    open_work_orders: int


class MaintenanceMetrics(BaseModel):
    factory_id: int
    availability_pct: float
    avg_mtbf_hours: float
    avg_mttr_hours: float
    pm_compliance_pct: float
    availability_trend: List[dict] = []
    breakdown_frequency: List[dict] = []

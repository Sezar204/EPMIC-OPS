Input
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas import ORMBase


class WorkerCreate(BaseModel):
    employee_id: str
    name: str
    department: Optional[str] = None
    role: Optional[str] = None
    skills: List[str] = []
    status: str = "active"
    notes: Optional[str] = None


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    skills: Optional[List[str]] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class WorkerRead(ORMBase):
    id: int
    factory_id: int
    employee_id: str
    name: str
    department: Optional[str] = None
    role: Optional[str] = None
    skills: List[str] = []
    status: str


class ShiftAssignmentCreate(BaseModel):
    worker_id: int
    shift_id: int
    assignment_date: date
    line_id: Optional[int] = None
    notes: Optional[str] = None


class ShiftAssignmentRead(ORMBase):
    id: int
    factory_id: int
    worker_id: int
    shift_id: int
    assignment_date: date
    line_id: Optional[int] = None


class AttendanceCreate(BaseModel):
    worker_id: int
    attendance_date: date
    scheduled_hours: float = 8
    actual_hours: float = 0
    ot_hours: float = 0
    status: str = "present"
    notes: Optional[str] = None


class AttendanceRead(ORMBase):
    id: int
    factory_id: int
    worker_id: int
    attendance_date: date
    scheduled_hours: float
    actual_hours: float
    ot_hours: float
    status: str


class WorkforceMetrics(BaseModel):
    factory_id: int
    attendance_rate_pct: float
    absenteeism_pct: float
    total_ot_hours: float
    headcount: int
    attendance_trend: List[dict] = []
    ot_by_worker: List[dict] = []

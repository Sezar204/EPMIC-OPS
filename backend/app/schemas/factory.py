Input
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas import ORMBase


class FactoryCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=200)
    type: str = Field(..., pattern="^(b2b|b2c|hybrid)$")
    status: str = "active"
    location: Optional[str] = None
    currency: str = "USD"
    timezone: str = "UTC"
    working_start: str = "08:00"
    working_end: str = "17:00"
    notes: Optional[str] = None


class FactoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    working_start: Optional[str] = None
    working_end: Optional[str] = None
    notes: Optional[str] = None


class FactoryRead(ORMBase):
    id: int
    code: str
    name: str
    type: str
    status: str
    location: Optional[str] = None
    currency: str
    timezone: str
    working_start: str
    working_end: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FactoryHealthScore(BaseModel):
    factory_id: int
    total_score: float
    plan_adherence: float
    machine_availability: float
    quality_rate: float
    inventory_health: float
    order_fulfillment: float
    workforce_stability: float
    status: str


class FactoryCalendarEntry(BaseModel):
    calendar_date: date
    is_working_day: bool = True
    holiday_name: Optional[str] = None
    notes: Optional[str] = None


# ---------- Production Line ----------
class ProductionLineCreate(BaseModel):
    code: str
    name: str
    type: str = "discrete"
    capacity_per_hour: float = 0
    capacity_unit: str = "pcs"
    status: str = "active"
    changeover_minutes: int = 0
    notes: Optional[str] = None


class ProductionLineUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    capacity_per_hour: Optional[float] = None
    capacity_unit: Optional[str] = None
    status: Optional[str] = None
    changeover_minutes: Optional[int] = None
    notes: Optional[str] = None


class ProductionLineRead(ORMBase):
    id: int
    factory_id: int
    code: str
    name: str
    type: str
    capacity_per_hour: float
    capacity_unit: str
    status: str
    changeover_minutes: int
    notes: Optional[str] = None


# ---------- Machine ----------
class MachineCreate(BaseModel):
    code: str
    name: str
    line_id: Optional[int] = None
    type: Optional[str] = None
    capacity: Optional[float] = None
    capacity_unit: Optional[str] = None
    criticality: str = "medium"
    status: str = "active"
    purchase_date: Optional[date] = None
    warranty_expiry: Optional[date] = None
    notes: Optional[str] = None


class MachineUpdate(BaseModel):
    name: Optional[str] = None
    line_id: Optional[int] = None
    type: Optional[str] = None
    capacity: Optional[float] = None
    capacity_unit: Optional[str] = None
    criticality: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class MachineRead(ORMBase):
    id: int
    factory_id: int
    line_id: Optional[int] = None
    code: str
    name: str
    type: Optional[str] = None
    capacity: Optional[float] = None
    capacity_unit: Optional[str] = None
    criticality: str
    status: str
    purchase_date: Optional[date] = None
    warranty_expiry: Optional[date] = None


# ---------- Shift ----------
class ShiftCreate(BaseModel):
    name: str
    start_time: str
    end_time: str
    break_minutes: int = 0
    days_of_week: str = "1,2,3,4,5"
    headcount: int = 1
    is_active: bool = True


class ShiftUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    break_minutes: Optional[int] = None
    days_of_week: Optional[str] = None
    headcount: Optional[int] = None
    is_active: Optional[bool] = None


class ShiftRead(ORMBase):
    id: int
    factory_id: int
    name: str
    start_time: str
    end_time: str
    break_minutes: int
    days_of_week: str
    headcount: int
    is_active: bool


# ---------- Warehouse ----------
class WarehouseCreate(BaseModel):
    code: str
    name: str
    type: str = "general"
    total_capacity: float = 0
    capacity_unit: str = "sqm"
    storage_conditions: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    total_capacity: Optional[float] = None
    storage_conditions: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class WarehouseRead(ORMBase):
    id: int
    factory_id: int
    code: str
    name: str
    type: str
    total_capacity: float
    capacity_unit: str
    storage_conditions: Optional[str] = None
    location: Optional[str] = None

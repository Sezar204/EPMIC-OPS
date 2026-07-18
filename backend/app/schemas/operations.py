Input
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas import ORMBase


# ---------- Production Order ----------
class ProductionOrderCreate(BaseModel):
    order_number: str
    product_id: int
    line_id: Optional[int] = None
    planned_qty: float
    planned_start: date
    planned_end: date
    priority: int = 3
    sales_order_id: Optional[int] = None
    notes: Optional[str] = None


class ProductionOrderUpdate(BaseModel):
    line_id: Optional[int] = None
    actual_qty: Optional[float] = None
    status: Optional[str] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    priority: Optional[int] = None
    notes: Optional[str] = None


class ProductionOrderRead(ORMBase):
    id: int
    factory_id: int
    order_number: str
    product_id: int
    line_id: Optional[int] = None
    planned_qty: float
    actual_qty: float
    planned_start: date
    planned_end: date
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    status: str
    priority: int


class DailyScheduleEntry(BaseModel):
    line_id: int
    line_name: str
    line_code: str
    date: date
    blocks: List[dict] = []
    utilization_pct: float = 0


class CapacityAnalysisEntry(BaseModel):
    line_id: int
    line_name: str
    line_code: str
    total_capacity_hours: float
    used_hours: float
    utilization_pct: float
    status: str  # ok | warning | overload


# ---------- Inventory ----------
class RawMaterialStockRead(ORMBase):
    id: int
    material_id: int
    material_code: str
    material_name: str
    warehouse_id: Optional[int] = None
    qty_on_hand: float
    qty_reserved: float
    qty_available: float
    safety_stock_qty: float
    reorder_point_qty: float
    days_coverage: Optional[float] = None
    coverage_status: str  # critical | warning | ok
    last_updated: datetime


class FinishedGoodStockRead(ORMBase):
    id: int
    product_id: int
    product_sku: str
    product_name: str
    qty_on_hand: float
    qty_reserved: float
    qty_available: float
    warehouse_id: Optional[int] = None
    last_updated: datetime


class WIPRead(ORMBase):
    id: int
    production_order_id: Optional[int] = None
    product_id: int
    line_id: Optional[int] = None
    quantity: float
    stage: str


class ABCXYZCell(BaseModel):
    cell: str
    count: int
    total_value: float
    items: List[int] = []


class ABCXYZMatrix(BaseModel):
    matrix: List[ABCXYZCell] = []
    total_items: int = 0
    total_value: float = 0


class CriticalItem(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    qty_on_hand: float
    safety_stock_qty: float
    days_coverage: float
    status: str
    recommended_action: str


class InventoryUpdate(BaseModel):
    qty_delta: float
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    warehouse_id: Optional[int] = None
    notes: Optional[str] = None

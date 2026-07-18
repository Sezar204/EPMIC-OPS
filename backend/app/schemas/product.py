Input
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas import ORMBase


# ---------- Product ----------
class ProductCreate(BaseModel):
    sku: str
    name: str
    category: Optional[str] = None
    unit_of_measure: str = "pcs"
    standard_cost: float = 0
    selling_price: float = 0
    min_order_qty: float = 1
    lead_time_days: int = 0
    shelf_life_days: Optional[int] = None
    type: str = "finished"
    notes: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: Optional[str] = None
    standard_cost: Optional[float] = None
    selling_price: Optional[float] = None
    min_order_qty: Optional[float] = None
    lead_time_days: Optional[int] = None
    shelf_life_days: Optional[int] = None
    type: Optional[str] = None
    notes: Optional[str] = None


class ProductRead(ORMBase):
    id: int
    factory_id: int
    sku: str
    name: str
    category: Optional[str] = None
    unit_of_measure: str
    standard_cost: float
    selling_price: float
    min_order_qty: float
    lead_time_days: int
    shelf_life_days: Optional[int] = None
    type: str


# ---------- Raw Material ----------
class RawMaterialCreate(BaseModel):
    code: str
    name: str
    category: Optional[str] = None
    unit_of_measure: str = "kg"
    standard_cost: float = 0
    safety_stock_qty: float = 0
    reorder_point_qty: float = 0
    lead_time_days: int = 0
    shelf_life_days: Optional[int] = None
    storage_conditions: Optional[str] = None
    notes: Optional[str] = None


class RawMaterialUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: Optional[str] = None
    standard_cost: Optional[float] = None
    safety_stock_qty: Optional[float] = None
    reorder_point_qty: Optional[float] = None
    lead_time_days: Optional[int] = None
    storage_conditions: Optional[str] = None
    notes: Optional[str] = None


class RawMaterialRead(ORMBase):
    id: int
    factory_id: int
    code: str
    name: str
    category: Optional[str] = None
    unit_of_measure: str
    standard_cost: float
    safety_stock_qty: float
    reorder_point_qty: float
    lead_time_days: int
    shelf_life_days: Optional[int] = None


# ---------- BOM ----------
class BOMLineCreate(BaseModel):
    material_id: int
    quantity_required: float
    unit: str = "kg"
    loss_factor_pct: float = 0
    is_alternative: bool = False
    alt_material_id: Optional[int] = None
    sequence_no: int = 1
    notes: Optional[str] = None


class BOMLineRead(ORMBase):
    id: int
    bom_id: int
    material_id: int
    quantity_required: float
    unit: str
    loss_factor_pct: float
    is_alternative: bool
    alt_material_id: Optional[int] = None
    sequence_no: int


class BOMCreate(BaseModel):
    product_id: int
    version: str = "1.0"
    name: str
    status: str = "active"
    yield_pct: float = 100
    effective_date: Optional[date] = None
    notes: Optional[str] = None
    lines: List[BOMLineCreate] = []


class BOMUpdate(BaseModel):
    version: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    yield_pct: Optional[float] = None
    effective_date: Optional[date] = None
    notes: Optional[str] = None
    lines: Optional[List[BOMLineCreate]] = None


class BOMRead(ORMBase):
    id: int
    factory_id: int
    product_id: int
    version: str
    name: str
    status: str
    yield_pct: float
    effective_date: Optional[date] = None
    lines: List[BOMLineRead] = []

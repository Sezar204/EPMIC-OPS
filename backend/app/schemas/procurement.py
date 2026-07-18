Input
from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from app.schemas import ORMBase


class SupplierCreate(BaseModel):
    code: str
    name: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    payment_terms_days: Optional[int] = None
    rating: int = 3
    status: str = "active"
    notes: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    payment_terms_days: Optional[int] = None
    rating: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class SupplierRead(ORMBase):
    id: int
    factory_id: int
    code: str
    name: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    payment_terms_days: Optional[int] = None
    rating: int
    status: str


class POLineCreate(BaseModel):
    material_id: int
    qty_ordered: float
    unit_price: float = 0
    notes: Optional[str] = None


class POLineRead(ORMBase):
    id: int
    po_id: int
    material_id: int
    qty_ordered: float
    unit_price: float
    qty_received: float
    quality_status: str


class POCreate(BaseModel):
    supplier_id: int
    po_number: str
    order_date: date
    expected_delivery: date
    currency: str = "USD"
    notes: Optional[str] = None
    lines: List[POLineCreate] = []


class POUpdate(BaseModel):
    expected_delivery: Optional[date] = None
    actual_delivery: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class PORead(ORMBase):
    id: int
    factory_id: int
    supplier_id: int
    po_number: str
    order_date: date
    expected_delivery: date
    actual_delivery: Optional[date] = None
    status: str
    total_value: float
    currency: str
    lines: List[POLineRead] = []


class MRPRequirement(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    period_date: date
    gross_requirement: float
    on_hand: float
    net_requirement: float
    suggested_po_date: date
    preferred_supplier_id: Optional[int] = None
    preferred_supplier_name: Optional[str] = None


class SupplierPerformance(BaseModel):
    supplier_id: int
    supplier_name: str
    on_time_delivery_pct: float
    quality_acceptance_pct: float
    active_pos: int
    rating: int
    monthly_otd: List[dict] = []

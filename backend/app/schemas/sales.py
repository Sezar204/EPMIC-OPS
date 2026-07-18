Input
from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from app.schemas import ORMBase


class CustomerCreate(BaseModel):
    code: str
    name: str
    type: str = "b2b"
    priority: int = 3
    credit_limit: Optional[float] = None
    payment_terms_days: Optional[int] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[int] = None
    credit_limit: Optional[float] = None
    payment_terms_days: Optional[int] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None


class CustomerRead(ORMBase):
    id: int
    factory_id: int
    code: str
    name: str
    type: str
    priority: int
    credit_limit: Optional[float] = None
    payment_terms_days: Optional[int] = None
    contact_name: Optional[str] = None


class SalesOrderLineCreate(BaseModel):
    product_id: int
    quantity: float
    unit_price: float = 0
    discount_pct: float = 0
    required_date: Optional[date] = None
    notes: Optional[str] = None


class SalesOrderLineRead(ORMBase):
    id: int
    order_id: int
    product_id: int
    quantity: float
    unit_price: float
    discount_pct: float
    line_total: float
    status: str
    fulfilled_qty: float


class SalesOrderCreate(BaseModel):
    customer_id: int
    order_number: str
    order_date: date
    required_delivery: date
    currency: str = "USD"
    is_rush_order: bool = False
    priority: int = 3
    notes: Optional[str] = None
    lines: List[SalesOrderLineCreate] = []


class SalesOrderUpdate(BaseModel):
    required_delivery: Optional[date] = None
    confirmed_delivery: Optional[date] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    notes: Optional[str] = None


class SalesOrderRead(ORMBase):
    id: int
    factory_id: int
    customer_id: int
    order_number: str
    order_date: date
    required_delivery: date
    confirmed_delivery: Optional[date] = None
    status: str
    total_value: float
    currency: str
    is_rush_order: bool
    priority: int
    lines: List[SalesOrderLineRead] = []


class DemandForecastRead(ORMBase):
    id: int
    factory_id: int
    product_id: int
    period_date: date
    period_type: str
    forecast_type: str
    historical_qty: float
    system_forecast_qty: float
    manual_adjusted_qty: Optional[float] = None
    final_qty: float


class DemandForecastUpdate(BaseModel):
    product_id: int
    period_date: date
    manual_adjusted_qty: float


class CTPResult(BaseModel):
    can_commit: bool
    committed_date: Optional[date] = None
    earliest_date: Optional[date] = None
    bottleneck: Optional[str] = None
    margin_pct: Optional[float] = None
    risk: str  # red | yellow | green
    details: dict = {}

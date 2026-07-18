Input
from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from app.schemas import ORMBase


class ProductCostCreate(BaseModel):
    product_id: int
    period_date: date
    std_material_cost: float = 0
    act_material_cost: float = 0
    std_labor_cost: float = 0
    act_labor_cost: float = 0
    std_overhead_cost: float = 0
    act_overhead_cost: float = 0
    std_total_cost: float = 0
    act_total_cost: float = 0
    revenue: float = 0
    notes: Optional[str] = None


class ProductCostRead(ORMBase):
    id: int
    factory_id: int
    product_id: int
    period_date: date
    std_material_cost: float
    act_material_cost: float
    std_labor_cost: float
    act_labor_cost: float
    std_overhead_cost: float
    act_overhead_cost: float
    std_total_cost: float
    act_total_cost: float
    revenue: float
    variance_pct: float = 0
    status: str = "good"


class VarianceAnalysis(BaseModel):
    factory_id: int
    period: str
    total_variance: float
    material_variance: float
    labor_variance: float
    overhead_variance: float
    by_product: List[dict] = []


class ProfitabilityRow(BaseModel):
    product_id: int
    product_sku: str
    product_name: str
    revenue: float
    cost: float
    margin: float
    margin_pct: float
    trend: List[float] = []


class ProfitabilityReport(BaseModel):
    factory_id: int
    period: str
    total_revenue: float
    total_cost: float
    gross_profit: float
    avg_margin_pct: float
    rows: List[ProfitabilityRow] = []

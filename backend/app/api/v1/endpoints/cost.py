Input
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.schemas.cost import ProductCostCreate
from app.services.quality_maint_wf import CostService
from app.models import ProductCost

router = APIRouter()


@router.get("/product-costs/{factory_id}")
def list_costs(factory_id: int, db: Session = Depends(get_db)):
    items = db.query(ProductCost).filter(ProductCost.factory_id == factory_id).all()
    out = []
    for c in items:
        v = c.act_total_cost - c.std_total_cost
        vp = (v / c.std_total_cost * 100) if c.std_total_cost else 0
        status = "good" if abs(vp) < 5 else ("warning" if abs(vp) < 10 else "danger")
        out.append({
            "id": c.id, "factory_id": c.factory_id, "product_id": c.product_id,
            "period_date": c.period_date.isoformat(),
            "std_material_cost": c.std_material_cost, "act_material_cost": c.act_material_cost,
            "std_labor_cost":    c.std_labor_cost,    "act_labor_cost":    c.act_labor_cost,
            "std_overhead_cost": c.std_overhead_cost, "act_overhead_cost": c.act_overhead_cost,
            "std_total_cost":    c.std_total_cost,    "act_total_cost":    c.act_total_cost,
            "revenue": c.revenue, "variance_pct": round(vp, 1), "status": status,
        })
    return ok(out, total=len(out))


@router.post("/product-costs/{factory_id}")
def create_cost(factory_id: int, payload: ProductCostCreate, db: Session = Depends(get_db)):
    c = CostService.save_cost(db, factory_id, payload)
    return ok({"id": c.id}, "Cost recorded")


@router.get("/analysis/variance/{factory_id}")
def variance(factory_id: int, period: str | None = None, db: Session = Depends(get_db)):
    p = date.fromisoformat(period) if period else None
    return ok(CostService.variance_analysis(db, factory_id, p))


@router.get("/analysis/profitability/{factory_id}")
def profitability(factory_id: int, period: str | None = None, db: Session = Depends(get_db)):
    p = date.fromisoformat(period) if period else None
    return ok(CostService.profitability(db, factory_id, p))

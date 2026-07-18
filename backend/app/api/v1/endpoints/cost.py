from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.helpers import add_crud_routes
from app.core.response import ok
from app.models.cost import ProductCost
from app.models.product import Product
from app.models.sales import SalesOrder, SalesOrderLine

router = APIRouter()
add_crud_routes(router, ProductCost, "cost/product-costs", order_by="period_label")


@router.get("/{factory_id}/cost/analysis/variance")
def variance(factory_id: int, period: str | None = None, db: Session = Depends(get_db)):
    q = select(ProductCost).where(ProductCost.factory_id == factory_id)
    if period:
        q = q.where(ProductCost.period_label == period)
    costs = db.scalars(q).all()
    out = []
    for c in costs:
        p = db.get(Product, c.product_id)
        var = round((c.act_total - c.std_total) / c.std_total * 100, 2) if c.std_total else 0
        status = "ok" if abs(var) < 5 else "warning" if abs(var) < 10 else "critical"
        out.append({"product": p.name if p else "-", "sku": p.sku if p else "-",
                    "std_total": c.std_total, "act_total": c.act_total,
                    "variance_pct": var, "status": status})
    total_var = round(sum(o["act_total"] - o["std_total"] for o in out), 2)
    return ok({"rows": out, "total_variance": total_var,
               "material": round(sum(o["act_total"] for o in out), 2)})


@router.get("/{factory_id}/cost/analysis/profitability")
def profitability(factory_id: int, db: Session = Depends(get_db)):
    products = db.scalars(select(Product).where(Product.factory_id == factory_id, Product.is_deleted == False)).all()
    out = []
    for p in products:
        revenue = db.scalar(select(func.coalesce(func.sum(SalesOrderLine.line_total), 0)).where(
            SalesOrderLine.product_id == p.id,
            SalesOrderLine.order_id.in_(select(SalesOrder.id).where(SalesOrder.factory_id == factory_id, SalesOrder.is_deleted == False))
        )) or 0
        cost = db.scalar(select(func.coalesce(func.sum(ProductCost.act_total), 0)).where(ProductCost.product_id == p.id)) or 0
        margin = revenue - cost
        margin_pct = round(margin / revenue * 100, 1) if revenue else 0
        out.append({"product": p.name, "sku": p.sku, "revenue": round(revenue, 2),
                    "cost": round(cost, 2), "margin": round(margin, 2), "margin_pct": margin_pct})
    out.sort(key=lambda x: x["margin_pct"], reverse=True)
    total_rev = sum(o["revenue"] for o in out)
    total_cost = sum(o["cost"] for o in out)
    return ok({"rows": out, "revenue": round(total_rev, 2), "cost": round(total_cost, 2),
               "gross_profit": round(total_rev - total_cost, 2),
               "avg_margin": round((total_rev - total_cost) / total_rev * 100, 1) if total_rev else 0})

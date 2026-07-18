Input
"""Demand forecasting — moving average + simple seasonal factor."""
from datetime import date, timedelta
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.engines import BaseEngine, EngineResult
from app.models import (
    DemandForecast, Product, SalesOrder, SalesOrderLine,
)


class DemandEngine(BaseEngine):
    name = "demand"

    def _execute(self, db: Session, factory_id: int, r: EngineResult, **kwargs):
        out = self.forecast(db, factory_id)
        r.data["forecasts"] = out[:50]
        r.items_processed = len(out)
        db.commit()

    def forecast(self, db: Session, factory_id: int) -> List[dict]:
        """Compute a 3-month moving-average forecast for each product,
        persisted to demand_forecasts (one row per product per month)."""
        products = db.scalars(select(Product).where(Product.factory_id == factory_id)).all()
        out: list = []
        cutoff = date.today() - timedelta(days=90)
        for p in products:
            sos = db.scalars(select(SalesOrder).where(
                SalesOrder.factory_id == factory_id,
                SalesOrder.order_date >= cutoff,
            )).all()
            total_qty = 0.0
            for so in sos:
                for ln in so.lines or []:
                    if ln.product_id == p.id:
                        total_qty += ln.quantity
            avg = total_qty / 3 if total_qty else 0
            period = date.today().replace(day=1)
            existing = db.scalars(select(DemandForecast).where(
                DemandForecast.factory_id == factory_id,
                DemandForecast.product_id == p.id,
                DemandForecast.period_date == period,
                DemandForecast.forecast_type == "b2c",
            )).first()
            if existing:
                existing.system_forecast_qty = round(avg, 1)
                existing.final_qty = existing.manual_adjusted_qty or existing.system_forecast_qty
            else:
                df = DemandForecast(
                    factory_id=factory_id, product_id=p.id,
                    period_date=period, period_type="monthly",
                    forecast_type="b2c",
                    historical_qty=round(total_qty, 1),
                    system_forecast_qty=round(avg, 1),
                    final_qty=round(avg, 1),
                )
                db.add(df)
            out.append({
                "product_id": p.id,
                "product_sku": p.sku,
                "product_name": p.name,
                "period_date": period.isoformat(),
                "historical_qty": round(total_qty, 1),
                "system_forecast_qty": round(avg, 1),
                "final_qty": round(avg, 1),
            })
        db.commit()
        return out

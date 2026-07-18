from sqlalchemy import select, func

from app.engines.base import BaseEngine
from app.models.sales import DemandForecast
from app.models.product import Product


class DemandEngine(BaseEngine):
    name = "demand_engine"

    def execute(self, db, factory_id: int):
        products = db.scalars(select(Product).where(
            Product.factory_id == factory_id, Product.is_deleted == False)).all()
        forecasts = []
        for p in products:
            fcs = db.scalars(select(DemandForecast).where(
                DemandForecast.factory_id == factory_id, DemandForecast.product_id == p.id
            ).order_by(DemandForecast.period_label)).all()
            hist = [f.historical for f in fcs if f.historical]
            if len(hist) >= 2:
                system = round(sum(hist[-3:]) / min(3, len(hist)), 0)
                for f in fcs:
                    if not f.historical:
                        f.system_forecast = system
                        f.final_forecast = f.manual_forecast if f.manual_forecast else system
                forecasts.append({"sku": p.sku, "system_forecast": system})
        db.commit()
        return self._ok(f"Forecasted {len(forecasts)} products", {"forecasts": forecasts})

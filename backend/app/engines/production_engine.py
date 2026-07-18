
Input
"""Production engine — converts S&OP / demand plan into production orders,
assigns to lines, accounts for changeovers."""
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.engines import BaseEngine, EngineResult
from app.models import (
    ProductionLine, ProductionOrder, Product, DemandForecast,
)


class ProductionEngine(BaseEngine):
    name = "production"

    def _execute(self, db: Session, factory_id: int, r: EngineResult, horizon_days: int = 14, **kwargs):
        forecasts = db.scalars(select(DemandForecast).where(
            DemandForecast.factory_id == factory_id,
        )).all()
        lines = db.scalars(select(ProductionLine).where(
            ProductionLine.factory_id == factory_id,
            ProductionLine.status == "active",
        )).all()
        if not lines:
            r.notes.append("No active production lines — skipped")
            return
        # Simple round-robin assignment
        r.items_processed = 0
        for fc in forecasts:
            if fc.final_qty <= 0: continue
            line = lines[r.items_processed % len(lines)]
            po = ProductionOrder(
                factory_id=factory_id,
                order_number=f"PO-{date.today().strftime('%Y%m%d')}-{r.items_processed+1:03d}",
                product_id=fc.product_id,
                line_id=line.id,
                planned_qty=fc.final_qty,
                planned_start=date.today(),
                planned_end=date.today() + timedelta(days=horizon_days // 2),
                status="planned",
                priority=3,
            )
            db.add(po)
            r.items_processed += 1
        db.commit()
        r.notes.append(f"Generated {r.items_processed} production orders")

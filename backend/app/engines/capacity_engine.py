Input
"""Capacity engine — computes utilization per line and identifies overloads."""
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.engines import BaseEngine, EngineResult
from app.models import ProductionLine, ProductionOrder


class CapacityEngine(BaseEngine):
    name = "capacity"

    def _execute(self, db: Session, factory_id: int, r: EngineResult, **kwargs):
        lines = db.scalars(select(ProductionLine).where(
            ProductionLine.factory_id == factory_id,
        )).all()
        start = date.today() - timedelta(days=7)
        out = []
        overloads = 0
        for line in lines:
            orders = db.scalars(select(ProductionOrder).where(
                ProductionOrder.factory_id == factory_id,
                ProductionOrder.line_id == line.id,
                ProductionOrder.planned_start >= start,
            )).all()
            cap_h = line.capacity_per_hour * 8  # 8h shift
            used_h = sum(o.planned_qty / max(1, line.capacity_per_hour) + (line.changeover_minutes / 60)
                         for o in orders)
            util = (used_h / (cap_h * 7)) * 100 if cap_h else 0
            status = "ok"
            if util > 100: status = "overload"; overloads += 1
            elif util > 85: status = "warning"
            out.append({
                "line_id": line.id, "line_code": line.code, "line_name": line.name,
                "capacity_per_hour": line.capacity_per_hour,
                "utilization_pct": round(util, 1),
                "status": status,
            })
        r.data["lines"] = out
        r.data["overloads"] = overloads
        r.items_processed = len(out)
        if overloads:
            r.alerts_created += overloads
        db.commit()

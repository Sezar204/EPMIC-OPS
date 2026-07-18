from datetime import timedelta

from sqlalchemy import select, func

from app.engines.base import BaseEngine
from app.models.production import ProductionLine, ProductionOrder


class CapacityEngine(BaseEngine):
    name = "capacity_engine"

    def execute(self, db, factory_id: int):
        lines = db.scalars(select(ProductionLine).where(
            ProductionLine.factory_id == factory_id, ProductionLine.is_deleted == False)).all()
        orders = db.scalars(select(ProductionOrder).where(ProductionOrder.factory_id == factory_id)).all()
        since = __import__("datetime").datetime.utcnow() - timedelta(days=7)
        out = []
        for l in lines:
            produced = sum(o.produced_qty for o in orders if o.line_id == l.id and o.actual_start and o.actual_start >= since)
            cap = l.capacity_per_hour * 8 * 7
            util = round(produced / cap * 100, 1) if cap else 0
            out.append({"line": l.name, "utilization": util,
                        "status": "overload" if util > 100 else "balanced" if util > 70 else "underutilized"})
        out.sort(key=lambda x: x["utilization"], reverse=True)
        return self._ok("Capacity analysis complete", {"lines": out})

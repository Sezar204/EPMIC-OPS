from datetime import timedelta

from sqlalchemy import select, func

from app.engines.base import BaseEngine
from app.models.production import ProductionLine, ProductionOrder
from app.models.sales import SalesOrder


class WhatIfEngine(BaseEngine):
    name = "what_if_engine"

    def execute(self, db, factory_id: int, body: dict | None = None):
        body = body or {}
        scenario = body.get("scenario_type", "DEMAND_CHANGE")
        params = body.get("parameters", {})
        horizon = int(body.get("horizon_days", 30))

        # baseline metrics
        lines = db.scalars(select(ProductionLine).where(
            ProductionLine.factory_id == factory_id, ProductionLine.is_deleted == False)).all()
        cap_total = sum(l.capacity_per_hour * 8 * horizon for l in lines)
        orders = db.scalars(select(SalesOrder).where(
            SalesOrder.factory_id == factory_id, SalesOrder.is_deleted == False,
            SalesOrder.status.in_(["confirmed", "in_production"]))).all()
        baseline_demand = sum(l.quantity for o in orders for l in o.lines) if False else \
            db.scalar(select(func.coalesce(func.sum(SalesOrderLine_qty := __import__("sqlalchemy").column("quantity")), 0))) if False else self._sum_demand(db, factory_id)

        before = {"capacity": cap_total, "demand": baseline_demand,
                  "utilization": round(baseline_demand / cap_total * 100, 1) if cap_total else 0}
        after = dict(before)

        if scenario == "DEMAND_CHANGE":
            pct = float(params.get("change_pct", 10))
            after["demand"] = round(baseline_demand * (1 + pct / 100), 0)
        elif scenario == "ADD_SHIFT":
            after["capacity"] = round(cap_total * (1 + float(params.get("capacity_increase_pct", 33)) / 100), 0)
        elif scenario == "LINE_DOWN":
            after["capacity"] = round(cap_total * (1 - float(params.get("capacity_loss_pct", 25)) / 100), 0)
        elif scenario == "SUPPLIER_FAILURE":
            after["risk"] = "material_shortage" if params.get("critical", True) else "low"
        elif scenario == "RUSH_ORDER":
            after["demand"] = baseline_demand + float(params.get("extra_units", 100))
        elif scenario == "PRICE_CHANGE":
            after["margin_impact_pct"] = float(params.get("price_change_pct", -5))

        if after.get("capacity"):
            after["utilization"] = round(after["demand"] / after["capacity"] * 100, 1) if after["capacity"] else 0
        verdict = "FEASIBLE" if after.get("utilization", 0) <= 100 else "OVERLOAD"
        return self._ok(f"What-if simulation: {scenario} -> {verdict}",
                        {"scenario": scenario, "before": before, "after": after, "verdict": verdict})

    def _sum_demand(self, db, factory_id):
        from app.models.sales import SalesOrder, SalesOrderLine
        from sqlalchemy import select, func
        return db.scalar(select(func.coalesce(func.sum(SalesOrderLine.quantity), 0)).where(
            SalesOrderLine.order_id.in_(
                select(SalesOrder.id).where(SalesOrder.factory_id == factory_id, SalesOrder.is_deleted == False)
            ))) or 0

Input
"""What-if engine — read-only simulation. NEVER writes to the database.

Supports: DEMAND_CHANGE, SUPPLIER_FAILURE, LINE_DOWN, ADD_SHIFT,
          RUSH_ORDER, PRICE_CHANGE.
"""
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.engines import BaseEngine, EngineResult
from app.models import (
    ProductionLine, ProductionOrder, RawMaterial, InventoryRawMaterial, Product,
)


class WhatIfEngine(BaseEngine):
    name = "what_if"

    def _execute(self, db: Session, factory_id: int, r: EngineResult, **kwargs):
        scenario  = kwargs.get("scenario_type", "DEMAND_CHANGE")
        params    = kwargs.get("parameters", {}) or {}
        horizon   = int(kwargs.get("horizon_days", 14))

        if   scenario == "DEMAND_CHANGE":   out = self._demand_change(db, factory_id, params, horizon)
        elif scenario == "SUPPLIER_FAILURE":out = self._supplier_failure(db, factory_id, params, horizon)
        elif scenario == "LINE_DOWN":       out = self._line_down(db, factory_id, params, horizon)
        elif scenario == "ADD_SHIFT":       out = self._add_shift(db, factory_id, params, horizon)
        elif scenario == "RUSH_ORDER":      out = self._rush_order(db, factory_id, params, horizon)
        elif scenario == "PRICE_CHANGE":    out = self._price_change(db, factory_id, params, horizon)
        else:                              out = {"error": f"Unknown scenario: {scenario}"}
        r.data = out
        r.items_processed = 1
        # IMPORTANT: do not commit. Read-only.

    def _baseline_output(self, db, factory_id, horizon):
        orders = db.scalars(select(ProductionOrder).where(
            ProductionOrder.factory_id == factory_id,
            ProductionOrder.planned_start >= date.today(),
            ProductionOrder.planned_start <= date.today() + timedelta(days=horizon),
        )).all()
        return {
            "planned_units": sum(o.planned_qty for o in orders),
            "orders":        len(orders),
        }

    def _demand_change(self, db, factory_id, params, horizon):
        factor = float(params.get("factor", 1.2))
        base = self._baseline_output(db, factory_id, horizon)
        new_units = base["planned_units"] * factor
        return {
            "scenario": "DEMAND_CHANGE",
            "factor":   factor,
            "before":   base,
            "after":    {"planned_units": round(new_units, 0), "orders": base["orders"]},
            "delta":    {"planned_units": round(new_units - base["planned_units"], 0)},
            "recommendation": "Increase shift hours or expedite material procurement." if factor > 1.1 else "Capacity sufficient.",
        }

    def _supplier_failure(self, db, factory_id, params, horizon):
        supplier_id = params.get("supplier_id")
        return {
            "scenario": "SUPPLIER_FAILURE",
            "supplier_id": supplier_id,
            "impact": "Critical materials may be at risk. Activate backup suppliers.",
            "affected_materials_count": 3,
        }

    def _line_down(self, db, factory_id, params, horizon):
        line_id = params.get("line_id")
        line = db.get(ProductionLine, line_id) if line_id else None
        lost_capacity = (line.capacity_per_hour * 8 * horizon) if line else 0
        return {
            "scenario": "LINE_DOWN",
            "line_id": line_id,
            "line_name": line.name if line else None,
            "lost_capacity_units": lost_capacity,
            "recommendation": "Redistribute to other lines; reschedule non-critical orders.",
        }

    def _add_shift(self, db, factory_id, params, horizon):
        extra_hours = float(params.get("hours_per_day", 4))
        new_capacity_pct = 100 * (1 + extra_hours / 8)
        return {
            "scenario": "ADD_SHIFT",
            "extra_hours_per_day": extra_hours,
            "capacity_uplift_pct": round(new_capacity_pct - 100, 1),
            "additional_units":  round(new_capacity_pct * 10, 0),  # demo
        }

    def _rush_order(self, db, factory_id, params, horizon):
        return {
            "scenario": "RUSH_ORDER",
            "qty":        params.get("qty", 1000),
            "delivery_in_days": params.get("delivery_in_days", 2),
            "feasible":   True,
            "recommendation": "Accept with surcharge; assign to night shift.",
        }

    def _price_change(self, db, factory_id, params, horizon):
        factor = float(params.get("factor", 1.1))
        base = self._baseline_output(db, factory_id, horizon)
        return {
            "scenario": "PRICE_CHANGE",
            "factor":   factor,
            "margin_impact_pct": round((1 - factor) * 100, 1),
        }

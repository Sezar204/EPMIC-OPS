from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.helpers import add_crud_routes
from app.core.response import ok
from app.models.production import ProductionOrder, ProductionLine, Machine
from app.models.product import Product

router = APIRouter()
add_crud_routes(router, ProductionOrder, "production/orders", order_by="planned_start")


@router.get("/{factory_id}/production/schedule/daily")
def schedule_daily(factory_id: int, day: str | None = None, db: Session = Depends(get_db)):
    target = date.fromisoformat(day) if day else date.today()
    lines = db.scalars(select(ProductionLine).where(
        ProductionLine.factory_id == factory_id, ProductionLine.is_deleted == False)).all()
    orders = db.scalars(select(ProductionOrder).where(
        ProductionOrder.factory_id == factory_id, ProductionOrder.planned_start != None)).all()
    blocks = []
    for o in orders:
        if o.planned_start and o.planned_start.date() == target:
            prod = db.get(Product, o.product_id)
            line = db.get(ProductionLine, o.line_id)
            blocks.append({
                "line_id": o.line_id, "line": line.name if line else "-",
                "order_number": o.order_number, "product": prod.name if prod else "-",
                "planned": o.planned_qty, "actual": o.produced_qty,
                "status": o.status,
            })
    return ok({"date": target.isoformat(), "lines": [l.name for l in lines], "blocks": blocks})


@router.get("/{factory_id}/production/schedule/weekly")
def schedule_weekly(factory_id: int, week_start: str | None = None, db: Session = Depends(get_db)):
    if week_start:
        start = date.fromisoformat(week_start)
    else:
        today = date.today()
        start = today - timedelta(days=today.weekday())
    days = [start + timedelta(days=i) for i in range(7)]
    lines = db.scalars(select(ProductionLine).where(
        ProductionLine.factory_id == factory_id, ProductionLine.is_deleted == False)).all()
    grid = {}
    orders = db.scalars(select(ProductionOrder).where(ProductionOrder.factory_id == factory_id)).all()
    for l in lines:
        grid[l.name] = {}
        for d in days:
            grid[l.name][d.isoformat()] = []
    for o in orders:
        if o.planned_start:
            for l in lines:
                if o.line_id == l.id:
                    grid[l.name][o.planned_start.date().isoformat()].append({
                        "order_number": o.order_number,
                        "product": (db.get(Product, o.product_id).name if o.product_id else "-"),
                        "utilization": round(o.planned_qty / max(1, l.capacity_per_hour * 8) * 100, 1),
                    })
    return ok({"week_start": start.isoformat(), "days": [d.isoformat() for d in days], "grid": grid})


@router.get("/{factory_id}/production/capacity/analysis")
def capacity_analysis(factory_id: int, db: Session = Depends(get_db)):
    lines = db.scalars(select(ProductionLine).where(
        ProductionLine.factory_id == factory_id, ProductionLine.is_deleted == False)).all()
    orders = db.scalars(select(ProductionOrder).where(ProductionOrder.factory_id == factory_id)).all()
    # produced in last 7 days
    since = date.today() - timedelta(days=7)
    out = []
    for l in lines:
        produced = sum(o.produced_qty for o in orders if o.line_id == l.id and o.actual_start and o.actual_start.date() >= since)
        capacity = l.capacity_per_hour * 8 * 7  # 8h * 7 days
        util = round(produced / capacity * 100, 1) if capacity else 0
        out.append({"line": l.name, "produced": round(produced, 0), "capacity": capacity,
                    "utilization": util, "status": "overload" if util > 100 else "ok"})
    return ok(out)

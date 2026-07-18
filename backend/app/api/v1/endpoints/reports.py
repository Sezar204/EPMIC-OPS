from datetime import date, timedelta

from fastapi import APIRouter, Depends, Body
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok
from app.models.production import ProductionOrder, ProductionLine
from app.models.product import Product
from app.models.inventory import RawMaterial, InventoryRawMaterial, InventoryFinishedGoods
from app.models.procurement import Supplier, PurchaseOrder, PurchaseOrderLine
from app.models.quality import QualityCheck, CAPARecord
from app.models.maintenance import MaintenanceWorkOrder
from app.models.kpi import KPIDefinition, KPIValue

router = APIRouter()

LIBRARY = [
    {"id": "daily_production", "title": "Daily Production Summary", "category": "Production",
     "description": "Production orders and output for the selected day."},
    {"id": "weekly_performance", "title": "Weekly Performance Report", "category": "Production",
     "description": "Line utilization and adherence for the week."},
    {"id": "monthly_executive", "title": "Monthly Executive Summary", "category": "Executive",
     "description": "Key KPIs across the plant."},
    {"id": "inventory_status", "title": "Inventory Status Report", "category": "Inventory",
     "description": "Raw material coverage and critical items."},
    {"id": "supplier_performance", "title": "Supplier Performance Report", "category": "Procurement",
     "description": "OTD and quality by supplier."},
    {"id": "quality_summary", "title": "Quality Summary Report", "category": "Quality",
     "description": "Defect rates, FPY and open CAPAs."},
    {"id": "maintenance_status", "title": "Maintenance Status Report", "category": "Maintenance",
     "description": "Work orders and downtime."},
    {"id": "cost_analysis", "title": "Cost Analysis Report", "category": "Cost",
     "description": "Standard vs actual cost variance."},
]


@router.get("/{factory_id}/reports/library")
def library(factory_id: int, db: Session = Depends(get_db)):
    return ok(LIBRARY)


@router.post("/{factory_id}/reports/generate")
def generate(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    rid = data.get("report_id")
    params = data.get("params", {})
    gen = GENERATORS.get(rid)
    if not gen:
        return ok({"title": "Unknown report", "columns": [], "rows": []})
    title, columns, rows = gen(factory_id, db, params)
    return ok({"title": title, "columns": columns, "rows": rows, "total": len(rows)})


def _daily_production(fid, db, params):
    day = date.fromisoformat(params["day"]) if params.get("day") else date.today()
    orders = db.scalars(select(ProductionOrder).where(
        ProductionOrder.factory_id == fid, ProductionOrder.planned_start != None)).all()
    rows = []
    for o in orders:
        if o.planned_start and o.planned_start.date() == day:
            prod = db.get(Product, o.product_id)
            line = db.get(ProductionLine, o.line_id)
            adh = round(o.produced_qty / o.planned_qty * 100, 1) if o.planned_qty else 0
            rows.append([o.order_number, line.name if line else "-", prod.name if prod else "-",
                         o.planned_qty, o.produced_qty, adh, o.status])
    return "Daily Production Summary", ["Order", "Line", "Product", "Planned", "Actual", "Adherence %", "Status"], rows


def _weekly_performance(fid, db, params):
    today = date.today()
    start = today - timedelta(days=today.weekday())
    lines = db.scalars(select(ProductionLine).where(ProductionLine.factory_id == fid, ProductionLine.is_deleted == False)).all()
    orders = db.scalars(select(ProductionOrder).where(ProductionOrder.factory_id == fid)).all()
    rows = []
    for l in lines:
        produced = sum(o.produced_qty for o in orders if o.line_id == l.id and o.actual_start and o.actual_start.date() >= start)
        cap = l.capacity_per_hour * 8 * 5
        util = round(produced / cap * 100, 1) if cap else 0
        rows.append([l.name, l.capacity_per_hour, round(produced, 0), cap, util])
    return "Weekly Performance Report", ["Line", "Capacity/h", "Produced", "Capacity", "Utilization %"], rows


def _monthly_executive(fid, db, params):
    defs = db.scalars(select(KPIDefinition).where(KPIDefinition.factory_id == fid)).all()
    rows = []
    for d in defs:
        latest = db.scalars(select(KPIValue).where(KPIValue.kpi_id == d.id).order_by(KPIValue.period_date.desc())).first()
        rows.append([d.name, d.category, latest.value if latest else 0, d.target_value, latest.status if latest else "-"])
    return "Monthly Executive Summary", ["KPI", "Category", "Value", "Target", "Status"], rows


def _inventory_status(fid, db, params):
    materials = db.scalars(select(RawMaterial).where(RawMaterial.factory_id == fid, RawMaterial.is_deleted == False)).all()
    rows = []
    for rm in materials:
        inv = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.material_id == rm.id)).first()
        rows.append([rm.code, rm.name, rm.category, inv.qty_on_hand if inv else 0,
                     rm.safety_stock_qty, inv.qty_available if inv else 0])
    return "Inventory Status Report", ["Code", "Name", "Category", "On Hand", "Safety", "Available"], rows


def _supplier_performance(fid, db, params):
    suppliers = db.scalars(select(Supplier).where(Supplier.factory_id == fid, Supplier.is_deleted == False)).all()
    rows = []
    for s in suppliers:
        pos = db.scalars(select(PurchaseOrder).where(PurchaseOrder.factory_id == fid, PurchaseOrder.supplier_id == s.id)).all()
        on_time = sum(1 for p in pos if p.actual_delivery and p.expected_delivery and p.actual_delivery <= p.expected_delivery)
        otd = round(on_time / (len(pos) or 1) * 100, 1)
        rows.append([s.name, len(pos), otd, s.rating, s.status])
    return "Supplier Performance Report", ["Supplier", "POs", "OTD %", "Rating", "Status"], rows


def _quality_summary(fid, db, params):
    total = db.scalar(select(func.count()).select_from(QualityCheck).where(QualityCheck.factory_id == fid)) or 0
    failed = db.scalar(select(func.count()).select_from(QualityCheck).where(QualityCheck.factory_id == fid, QualityCheck.status == "failed")) or 0
    open_capa = db.scalar(select(func.count()).select_from(CAPARecord).where(CAPARecord.factory_id == fid, CAPARecord.status != "closed")) or 0
    return "Quality Summary Report", ["Metric", "Value"], [
        ["Total Checks", total], ["Failed", failed],
        ["Defect Rate %", round(failed / total * 100, 2) if total else 0],
        ["Open CAPAs", open_capa],
    ]


def _maintenance_status(fid, db, params):
    wos = db.scalars(select(MaintenanceWorkOrder).where(MaintenanceWorkOrder.factory_id == fid)).all()
    from collections import Counter
    c = Counter(w.status for w in wos)
    rows = [[k, v] for k, v in c.items()]
    rows.append(["Total Downtime (h)", sum(w.downtime_hours for w in wos)])
    return "Maintenance Status Report", ["Status", "Count"], rows


def _cost_analysis(fid, db, params):
    from app.models.cost import ProductCost
    costs = db.scalars(select(ProductCost).where(ProductCost.factory_id == fid)).all()
    rows = []
    for cc in costs:
        p = db.get(Product, cc.product_id)
        var = round((cc.act_total - cc.std_total) / cc.std_total * 100, 2) if cc.std_total else 0
        rows.append([p.name if p else "-", cc.period_label, cc.std_total, cc.act_total, var])
    return "Cost Analysis Report", ["Product", "Period", "Std Total", "Act Total", "Variance %"], rows


GENERATORS = {
    "daily_production": _daily_production,
    "weekly_performance": _weekly_performance,
    "monthly_executive": _monthly_executive,
    "inventory_status": _inventory_status,
    "supplier_performance": _supplier_performance,
    "quality_summary": _quality_summary,
    "maintenance_status": _maintenance_status,
    "cost_analysis": _cost_analysis,
}

Input
"""Pre-built report definitions and generator dispatch."""
from datetime import date, datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import (
    ProductionOrder, ProductionLine, Product, Customer, SalesOrder,
    RawMaterial, InventoryRawMaterial, Supplier, PurchaseOrder,
    QualityCheck, Machine, MaintenanceWorkOrder, ProductCost,
)
from app.utils.exporter import to_excel, to_csv, to_pdf_simple


REPORTS = [
    {"id": "daily_production",    "name": "Daily Production Summary",   "category": "Production", "description": "Production orders and output for a date range.",     "parameters": ["date_from", "date_to"]},
    {"id": "weekly_performance",  "name": "Weekly Performance Report",  "category": "Production", "description": "Plan vs actual + OEE + quality for a week.",        "parameters": ["date_from"]},
    {"id": "monthly_executive",   "name": "Monthly Executive Summary",  "category": "Executive",  "description": "High-level KPIs and decisions for the month.",      "parameters": ["date_from"]},
    {"id": "inventory_status",    "name": "Inventory Status Report",    "category": "Inventory",  "description": "Current stock, coverage, and critical items.",      "parameters": []},
    {"id": "supplier_performance","name": "Supplier Performance Report","category": "Procurement","description": "OTD, quality, ratings by supplier.",               "parameters": ["date_from", "date_to"]},
    {"id": "quality_summary",     "name": "Quality Summary Report",     "category": "Quality",    "description": "Defects, FPY, CAPA closure, NCRs.",                "parameters": ["date_from", "date_to"]},
    {"id": "maintenance_status",  "name": "Maintenance Status Report",  "category": "Maintenance","description": "Open WOs, PM compliance, breakdowns.",              "parameters": []},
    {"id": "cost_analysis",       "name": "Cost Analysis Report",       "category": "Financial",  "description": "Standard vs actual, variance by product.",         "parameters": ["date_from"]},
]


class ReportService:
    @staticmethod
    def library() -> list:
        return REPORTS

    @staticmethod
    def generate(db: Session, report_id: str, date_from: Optional[date],
                 date_to: Optional[date], fmt: str = "excel") -> tuple[bytes, str, str]:
        if   report_id == "daily_production":     return _daily_production(db, date_from, date_to, fmt)
        elif report_id == "weekly_performance":   return _weekly_performance(db, date_from, fmt)
        elif report_id == "monthly_executive":    return _monthly_executive(db, date_from, fmt)
        elif report_id == "inventory_status":     return _inventory_status(db, fmt)
        elif report_id == "supplier_performance": return _supplier_performance(db, fmt)
        elif report_id == "quality_summary":      return _quality_summary(db, date_from, date_to, fmt)
        elif report_id == "maintenance_status":   return _maintenance_status(db, fmt)
        elif report_id == "cost_analysis":        return _cost_analysis(db, date_from, fmt)
        else:
            raise ValueError(f"Unknown report: {report_id}")


def _format(headers, rows, fmt, title):
    if fmt == "csv":
        return to_csv(headers, rows), "text/csv", f"{title}.csv"
    if fmt == "pdf":
        return to_pdf_simple(title, headers, rows), "application/pdf", f"{title}.pdf"
    return to_excel(headers, rows, title=title), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", f"{title}.xlsx"


def _daily_production(db, df, dt, fmt):
    if df is None: df = date.today()
    if dt is None: dt = df
    orders = db.scalars(select(ProductionOrder).where(
        ProductionOrder.planned_start >= df, ProductionOrder.planned_end <= dt
    )).all()
    products = {p.id: p for p in db.scalars(select(Product)).all()}
    headers = ["Order", "Product", "Planned Qty", "Actual Qty", "Start", "End", "Status"]
    rows = [
        [o.order_number, products[o.product_id].sku if o.product_id in products else o.product_id,
         o.planned_qty, o.actual_qty, o.planned_start, o.planned_end, o.status]
        for o in orders
    ]
    return _format(headers, rows, fmt, "Daily Production Summary")


def _weekly_performance(db, df, fmt):
    if df is None: df = date.today() - timedelta(days=7)
    orders = db.scalars(select(ProductionOrder).where(ProductionOrder.planned_start >= df)).all()
    headers = ["Order", "Planned", "Actual", "Adherence %", "Status"]
    rows = [
        [o.order_number, o.planned_qty, o.actual_qty,
         round((o.actual_qty / o.planned_qty) * 100, 1) if o.planned_qty else 0,
         o.status] for o in orders
    ]
    return _format(headers, rows, fmt, "Weekly Performance Report")


def _monthly_executive(db, df, fmt):
    if df is None: df = date.today().replace(day=1)
    orders = db.scalars(select(ProductionOrder).where(ProductionOrder.planned_start >= df)).all()
    total_planned = sum(o.planned_qty for o in orders) or 1
    total_actual  = sum(o.actual_qty for o in orders)
    headers = ["Metric", "Value"]
    rows = [
        ["Total Planned", total_planned],
        ["Total Actual",  total_actual],
        ["Adherence %",   round(total_actual / total_planned * 100, 1)],
        ["Orders",        len(orders)],
    ]
    return _format(headers, rows, fmt, "Monthly Executive Summary")


def _inventory_status(db, fmt):
    invs = db.scalars(select(InventoryRawMaterial)).all()
    mats = {m.id: m for m in db.scalars(select(RawMaterial)).all()}
    headers = ["Code", "Name", "On Hand", "Safety", "Available", "Status"]
    rows = []
    for i in invs:
        m = mats.get(i.material_id)
        if not m: continue
        status = "OK"
        if i.qty_on_hand == 0:        status = "DEPLETED"
        elif i.qty_on_hand < m.safety_stock_qty: status = "CRITICAL"
        rows.append([m.code, m.name, i.qty_on_hand, m.safety_stock_qty, i.qty_available, status])
    return _format(headers, rows, fmt, "Inventory Status Report")


def _supplier_performance(db, fmt):
    sups = db.scalars(select(Supplier)).all()
    headers = ["Code", "Name", "Rating", "Status", "Active POs"]
    rows = [[s.code, s.name, s.rating, s.status, 0] for s in sups]
    return _format(headers, rows, fmt, "Supplier Performance Report")


def _quality_summary(db, df, dt, fmt):
    if df is None: df = date.today() - timedelta(days=30)
    if dt is None: dt = date.today()
    checks = db.scalars(select(QualityCheck).where(QualityCheck.checked_at >= df)).all()
    headers = ["Type", "Status", "Sample", "Defects", "Defect %", "Date"]
    rows = [[c.check_type, c.status, c.sample_size, c.defects_found, c.defect_rate_pct, c.checked_at] for c in checks]
    return _format(headers, rows, fmt, "Quality Summary Report")


def _maintenance_status(db, fmt):
    wos = db.scalars(select(MaintenanceWorkOrder)).all()
    machines = {m.id: m for m in db.scalars(select(Machine)).all()}
    headers = ["WO #", "Machine", "Type", "Priority", "Status", "Downtime Hrs"]
    rows = [[w.wo_number, machines[w.machine_id].code if w.machine_id in machines else w.machine_id,
             w.type, w.priority, w.status, w.downtime_hours] for w in wos]
    return _format(headers, rows, fmt, "Maintenance Status Report")


def _cost_analysis(db, df, fmt):
    if df is None: df = date.today().replace(day=1)
    costs = db.scalars(select(ProductCost).where(ProductCost.period_date >= df)).all()
    products = {p.id: p for p in db.scalars(select(Product)).all()}
    headers = ["Product", "Std Total", "Act Total", "Variance", "Variance %", "Revenue"]
    rows = []
    for c in costs:
        prod = products.get(c.product_id)
        if not prod: continue
        v = c.act_total_cost - c.std_total_cost
        vp = (v / c.std_total_cost * 100) if c.std_total_cost else 0
        rows.append([prod.sku, round(c.std_total_cost, 2), round(c.act_total_cost, 2),
                     round(v, 2), round(vp, 1), round(c.revenue, 2)])
    return _format(headers, rows, fmt, "Cost Analysis Report")

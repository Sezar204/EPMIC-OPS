from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.crud import list_resources, get_resource, create_resource, update_resource, delete_resource
from app.core.response import ok, fail
from app.models.factory import Factory, FactoryCalendar
from app.models.production import ProductionLine, Machine, ProductionOrder
from app.models.product import Product, BOMHeader
from app.models.inventory import RawMaterial, InventoryRawMaterial
from app.models.sales import SalesOrder, SalesOrderLine, Customer
from app.models.procurement import Supplier, PurchaseOrder, PurchaseOrderLine
from app.models.quality import QualityCheck
from app.models.workforce import Worker, AttendanceRecord
from app.models.alert import Alert, Decision

router = APIRouter()


@router.get("")
def list_factories(db: Session = Depends(get_db)):
    rows, total = list_resources(db, Factory, None, page=1, page_size=500)
    return ok(rows, "OK", total=total)


@router.post("")
def create_factory(data: dict = Body(...), db: Session = Depends(get_db)):
    obj = create_resource(db, Factory, data, factory_id=None)
    return ok(obj, "Factory created")


@router.get("/{factory_id}")
def get_factory(factory_id: int, db: Session = Depends(get_db)):
    obj = get_resource(db, Factory, factory_id)
    if not obj:
        return fail("Factory not found")
    return ok(obj)


@router.put("/{factory_id}")
def update_factory(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    obj = update_resource(db, Factory, factory_id, data, factory_id=None)
    if not obj:
        return fail("Factory not found")
    return ok(obj, "Factory updated")


@router.delete("/{factory_id}")
def delete_factory(factory_id: int, db: Session = Depends(get_db)):
    result = delete_resource(db, Factory, factory_id, factory_id=None)
    if not result:
        return fail("Factory not found")
    return ok(None, "Factory deleted")


# --------------------------------------------------------------------------
# Health score
# --------------------------------------------------------------------------
def compute_health(fid: int, db: Session) -> dict:
    def ratio(numerator, denominator):
        return round(numerator / denominator * 100, 1) if denominator else 100.0

    total_m = db.scalar(select(func.count()).select_from(Machine).where(Machine.factory_id == fid, Machine.is_deleted == False)) or 0
    active_m = db.scalar(select(func.count()).select_from(Machine).where(Machine.factory_id == fid, Machine.is_deleted == False, Machine.status == "active")) or 0
    machine_availability = ratio(active_m, total_m)

    total_po = db.scalar(select(func.count()).select_from(ProductionOrder).where(ProductionOrder.factory_id == fid)) or 0
    produced = db.scalar(select(func.coalesce(func.sum(ProductionOrder.produced_qty), 0)).where(ProductionOrder.factory_id == fid)) or 0
    planned = db.scalar(select(func.coalesce(func.sum(ProductionOrder.planned_qty), 0)).where(ProductionOrder.factory_id == fid)) or 0
    plan_adherence = ratio(produced, planned)

    total_qc = db.scalar(select(func.count()).select_from(QualityCheck).where(QualityCheck.factory_id == fid)) or 0
    passed_qc = db.scalar(select(func.count()).select_from(QualityCheck).where(QualityCheck.factory_id == fid, QualityCheck.status == "passed")) or 0
    quality_rate = ratio(passed_qc, total_qc)

    total_rm = db.scalar(select(func.count()).select_from(RawMaterial).where(RawMaterial.factory_id == fid, RawMaterial.is_deleted == False)) or 0
    healthy_rm = 0
    invs = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.factory_id == fid)).all()
    for inv in invs:
        rm = db.get(RawMaterial, inv.material_id)
        if rm and inv.qty_available >= rm.safety_stock_qty:
            healthy_rm += 1
    inventory_health = ratio(healthy_rm, total_rm)

    total_so = db.scalar(select(func.count()).select_from(SalesOrder).where(SalesOrder.factory_id == fid, SalesOrder.is_deleted == False)) or 0
    fulfilled_so = db.scalar(select(func.count()).select_from(SalesOrder).where(SalesOrder.factory_id == fid, SalesOrder.is_deleted == False, SalesOrder.status.in_(["delivered", "shipped"]))) or 0
    order_fulfillment = ratio(fulfilled_so, total_so)

    total_att = db.scalar(select(func.count()).select_from(AttendanceRecord).where(AttendanceRecord.factory_id == fid)) or 0
    present_att = db.scalar(select(func.count()).select_from(AttendanceRecord).where(AttendanceRecord.factory_id == fid, AttendanceRecord.status.in_(["present", "late"]))) or 0
    workforce_stability = ratio(present_att, total_att)

    scores = [plan_adherence, machine_availability, quality_rate, inventory_health, order_fulfillment, workforce_stability]
    total_score = round(sum(scores) / len(scores), 1)
    status = "excellent" if total_score >= 90 else "good" if total_score >= 75 else "warning" if total_score >= 60 else "critical"
    return {
        "factory_id": fid,
        "total_score": total_score,
        "plan_adherence": plan_adherence,
        "machine_availability": machine_availability,
        "quality_rate": quality_rate,
        "inventory_health": inventory_health,
        "order_fulfillment": order_fulfillment,
        "workforce_stability": workforce_stability,
        "status": status,
    }


@router.get("/{factory_id}/health-score")
def health_score(factory_id: int, db: Session = Depends(get_db)):
    return ok(compute_health(factory_id, db))


# --------------------------------------------------------------------------
# Dashboard summary
# --------------------------------------------------------------------------
@router.get("/{factory_id}/dashboard-summary")
def dashboard_summary(factory_id: int, db: Session = Depends(get_db)):
    today = date.today()
    health = compute_health(factory_id, db)

    critical_alerts = db.scalars(
        select(Alert).where(Alert.factory_id == factory_id, Alert.is_resolved == False,
                            Alert.severity.in_(["critical", "emergency"]))
        .order_by(Alert.created_at.desc()).limit(5)
    ).all()
    pending_decisions = db.scalars(
        select(Decision).where(Decision.factory_id == factory_id, Decision.status == "pending")
        .order_by(Decision.priority != "urgent", Decision.created_at.desc()).limit(5)
    ).all()

    # today's production schedule
    orders = db.scalars(
        select(ProductionOrder).where(ProductionOrder.factory_id == factory_id)
        .order_by(ProductionOrder.planned_start.desc())
    ).all()
    schedule = []
    for o in orders[:10]:
        prod = db.get(Product, o.product_id) if o.product_id else None
        line = db.get(ProductionLine, o.line_id) if o.line_id else None
        adh = round(o.produced_qty / o.planned_qty * 100, 1) if o.planned_qty else 0
        schedule.append({
            "order_number": o.order_number,
            "line": line.name if line else "-",
            "product": prod.name if prod else "-",
            "planned": o.planned_qty,
            "actual": o.produced_qty,
            "adherence": adh,
            "status": o.status,
        })

    # critical materials
    critical_materials = []
    invs = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.factory_id == factory_id)).all()
    for inv in invs:
        rm = db.get(RawMaterial, inv.material_id)
        if not rm:
            continue
        days = round(inv.qty_available / max(1, (inv.qty_on_hand / max(1, 30))), 1) if inv.qty_on_hand else 0
        cov = "emergency" if days < 3 else "warning" if days < 7 else "ok"
        if cov != "ok":
            critical_materials.append({
                "id": rm.id, "code": rm.code, "name": rm.name,
                "on_hand": inv.qty_on_hand, "safety": rm.safety_stock_qty,
                "coverage_days": days, "status": cov,
            })

    counts = {
        "production_lines": db.scalar(select(func.count()).select_from(ProductionLine).where(ProductionLine.factory_id == factory_id, ProductionLine.is_deleted == False)) or 0,
        "machines": db.scalar(select(func.count()).select_from(Machine).where(Machine.factory_id == factory_id, Machine.is_deleted == False)) or 0,
        "products": db.scalar(select(func.count()).select_from(Product).where(Product.factory_id == factory_id, Product.is_deleted == False)) or 0,
        "open_orders": db.scalar(select(func.count()).select_from(SalesOrder).where(SalesOrder.factory_id == factory_id, SalesOrder.is_deleted == False, SalesOrder.status.in_(["confirmed", "in_production", "ready"]))) or 0,
        "suppliers": db.scalar(select(func.count()).select_from(Supplier).where(Supplier.factory_id == factory_id, Supplier.is_deleted == False)) or 0,
        "critical_alerts": len(critical_alerts),
        "pending_decisions": len(pending_decisions),
    }

    return ok({
        "health": health,
        "counts": counts,
        "today_schedule": schedule,
        "critical_alerts": [serialize(a) for a in critical_alerts],
        "pending_decisions": [serialize(d) for d in pending_decisions],
        "critical_materials": critical_materials,
    })


# --------------------------------------------------------------------------
# Calendar
# --------------------------------------------------------------------------
@router.get("/{factory_id}/calendar")
def get_calendar(factory_id: int, month: str = Query(...), db: Session = Depends(get_db)):
    y, m = month.split("-")
    cal = db.scalars(
        select(FactoryCalendar).where(
            FactoryCalendar.factory_id == factory_id,
            func.strftime("%Y-%m", FactoryCalendar.cal_date) == month,
        )
    ).all()
    return ok([{"date": c.cal_date.isoformat(), "is_working_day": c.is_working_day,
                "is_holiday": c.is_holiday, "holiday_name": c.holiday_name} for c in cal])


@router.post("/{factory_id}/calendar")
def update_calendar(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    cal_date = data.get("date")
    if not cal_date:
        return fail("date required")
    d = datetime.fromisoformat(cal_date).date()
    cal = db.scalar(select(FactoryCalendar).where(
        FactoryCalendar.factory_id == factory_id, FactoryCalendar.cal_date == d))
    if not cal:
        cal = FactoryCalendar(factory_id=factory_id, cal_date=d)
        db.add(cal)
        db.flush()
    is_holiday = bool(data.get("is_holiday", False))
    cal.is_holiday = is_holiday
    cal.is_working_day = not is_holiday if "is_working_day" not in data else bool(data["is_working_day"])
    cal.holiday_name = data.get("holiday_name")
    db.commit()
    return ok({"ok": True})


def serialize(obj):
    from app.core.crud import serialize as _s
    return _s(obj)

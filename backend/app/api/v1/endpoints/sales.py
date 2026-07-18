from datetime import timedelta

from fastapi import APIRouter, Depends, Body
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.crud import serialize
from app.core.response import ok, fail
from app.models.sales import SalesOrder, SalesOrderLine, Customer, DemandForecast
from app.models.product import Product, BOMLine, BOMHeader
from app.models.inventory import InventoryRawMaterial, RawMaterial

router = APIRouter()


def _order_view(o: SalesOrder, db: Session) -> dict:
    row = serialize(o)
    cust = db.get(Customer, o.customer_id)
    lines = db.scalars(select(SalesOrderLine).where(SalesOrderLine.order_id == o.id)).all()
    row["customer_name"] = cust.name if cust else "-"
    row["lines_count"] = len(lines)
    row["lines"] = [serialize(l) for l in lines]
    return row


@router.get("/{factory_id}/sales/orders")
def list_orders(factory_id: int, page: int = 1, page_size: int = 20, search: str | None = None,
                status: str | None = None, db: Session = Depends(get_db)):
    from app.core.crud import list_resources
    filters = {"status": status} if status else None
    rows, total = list_resources(db, SalesOrder, factory_id, page=page, page_size=page_size,
                                 search=search, search_fields=["order_number"], filters=filters, order_by="order_date")
    rows = [_order_view(db.get(SalesOrder, r["id"]), db) for r in rows]
    return ok(rows, "OK", total=total, page=page, page_size=page_size)


@router.post("/{factory_id}/sales/orders")
def create_order(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    lines = data.pop("lines", [])
    total = 0.0
    order = SalesOrder(factory_id=factory_id, customer_id=data["customer_id"],
                       order_number=data.get("order_number"), order_date=data.get("order_date"),
                       required_delivery=data.get("required_delivery"), status=data.get("status", "draft"),
                       currency=data.get("currency", "USD"), is_rush_order=data.get("is_rush_order", False),
                       priority=data.get("priority", 3), notes=data.get("notes"))
    db.add(order)
    db.flush()
    for l in lines:
        lt = float(l.get("unit_price", 0))
        qty = float(l.get("quantity", 0))
        disc = float(l.get("discount_pct", 0))
        line_total = qty * lt * (1 - disc / 100)
        total += line_total
        db.add(SalesOrderLine(order_id=order.id, product_id=l["product_id"], quantity=qty,
                              unit_price=lt, discount_pct=disc, line_total=line_total,
                              required_date=l.get("required_date"), status="open"))
    order.total_value = round(total, 2)
    db.commit()
    return ok(_order_view(order, db), "Order created")


@router.get("/{factory_id}/sales/orders/{rid}")
def get_order(factory_id: int, rid: int, db: Session = Depends(get_db)):
    o = db.get(SalesOrder, rid)
    if not o or o.factory_id != factory_id:
        return fail("Not found")
    return ok(_order_view(o, db))


@router.put("/{factory_id}/sales/orders/{rid}")
def update_order(factory_id: int, rid: int, data: dict = Body(...), db: Session = Depends(get_db)):
    o = db.get(SalesOrder, rid)
    if not o or o.factory_id != factory_id:
        return fail("Not found")
    for k, v in data.items():
        if k in ("lines", "id", "factory_id"):
            continue
        setattr(o, k, v)
    if "lines" in data:
        db.query(SalesOrderLine).where(SalesOrderLine.order_id == rid).delete()
        for l in data["lines"]:
            lt = float(l.get("unit_price", 0))
            qty = float(l.get("quantity", 0))
            disc = float(l.get("discount_pct", 0))
            db.add(SalesOrderLine(order_id=rid, product_id=l["product_id"], quantity=qty,
                                  unit_price=lt, discount_pct=disc,
                                  line_total=qty * lt * (1 - disc / 100),
                                  required_date=l.get("required_date"), status="open"))
    db.commit()
    return ok(_order_view(o, db), "Updated")


@router.delete("/{factory_id}/sales/orders/{rid}")
def delete_order(factory_id: int, rid: int, db: Session = Depends(get_db)):
    o = db.get(SalesOrder, rid)
    if not o or o.factory_id != factory_id:
        return fail("Not found")
    o.is_deleted = True
    db.commit()
    return ok(None, "Deleted")


@router.post("/{factory_id}/sales/orders/{rid}/ctp-analysis")
def ctp_analysis(factory_id: int, rid: int, db: Session = Depends(get_db)):
    o = db.get(SalesOrder, rid)
    if not o:
        return fail("Not found")
    lines = db.scalars(select(SalesOrderLine).where(SalesOrderLine.order_id == o.id)).all()
    # explode materials
    required: dict[int, float] = {}
    margin = 0.0
    for l in lines:
        prod = db.get(Product, l.product_id)
        if prod:
            margin += (prod.selling_price - prod.standard_cost) * l.quantity
        bom_lines = db.scalars(select(BOMLine).join(BOMHeader, BOMLine.bom_id == BOMHeader.id).where(BOMHeader.product_id == l.product_id)).all()
        for bl in bom_lines:
            required[bl.material_id] = required.get(bl.material_id, 0) + l.quantity * bl.quantity_required
    bottlenecks = []
    can_commit = True
    committed = o.order_date
    for mid, qty in required.items():
        inv = db.scalars(select(InventoryRawMaterial).where(InventoryRawMaterial.material_id == mid)).first()
        available = inv.qty_available if inv else 0
        rm = db.get(RawMaterial, mid)
        if available < qty:
            can_commit = False
            if rm:
                bottlenecks.append(f"{rm.name}: short {round(qty - available, 1)} {rm.unit_of_measure}")
            # delay by lead time
            if rm:
                committed = max(committed, o.order_date + timedelta(days=rm.lead_time_days))
    risk = "green"
    if not can_commit:
        risk = "red"
    elif bottlenecks:
        risk = "yellow"
    margin_pct = round(margin / max(o.total_value, 1) * 100, 1)
    return ok({
        "can_commit": can_commit,
        "committed_date": committed.isoformat() if hasattr(committed, "isoformat") else str(committed),
        "earliest_date": (o.order_date + timedelta(days=1)).isoformat(),
        "bottlenecks": bottlenecks,
        "margin_pct": margin_pct,
        "risk": risk,
    })


# ---- Forecasts ----
@router.get("/{factory_id}/sales/forecasts")
def list_forecasts(factory_id: int, period_type: str = "monthly", db: Session = Depends(get_db)):
    rows = db.scalars(select(DemandForecast).where(
        DemandForecast.factory_id == factory_id, DemandForecast.period_type == period_type
    ).order_by(DemandForecast.period_label)).all()
    return ok([serialize(r) for r in rows])


@router.post("/{factory_id}/sales/forecasts")
def upsert_forecast(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    prod_id = data["product_id"]
    plabel = data["period_label"]
    existing = db.scalar(select(DemandForecast).where(
        DemandForecast.factory_id == factory_id, DemandForecast.product_id == prod_id,
        DemandForecast.period_label == plabel))
    if existing:
        existing.manual_forecast = data.get("manual_forecast")
        existing.final_forecast = data.get("manual_forecast", existing.final_forecast)
    else:
        db.add(DemandForecast(factory_id=factory_id, product_id=prod_id,
                              period_type=data.get("period_type", "monthly"),
                              period_label=plabel, historical=data.get("historical", 0),
                              system_forecast=data.get("system_forecast", 0),
                              manual_forecast=data.get("manual_forecast"),
                              final_forecast=data.get("manual_forecast", data.get("system_forecast", 0))))
    db.commit()
    return ok(None, "Forecast saved")


@router.get("/{factory_id}/sales/sop")
def sop(factory_id: int, db: Session = Depends(get_db)):
    # Consolidated B2B demand + B2C forecast
    b2b = db.scalars(select(SalesOrderLine).where(
        SalesOrderLine.order_id.in_(
            select(SalesOrder.id).where(SalesOrder.factory_id == factory_id, SalesOrder.is_deleted == False)
        )
    )).all()
    demand: dict[int, float] = {}
    for l in b2b:
        demand[l.product_id] = demand.get(l.product_id, 0) + l.quantity

    b2c = db.scalars(select(DemandForecast).where(
        DemandForecast.factory_id == factory_id)).all()
    fc: dict[int, float] = {}
    for f in b2c:
        fc[f.product_id] = fc.get(f.product_id, 0) + f.final_forecast

    products = db.scalars(select(Product).where(Product.factory_id == factory_id, Product.is_deleted == False)).all()
    rows = []
    for p in products:
        b = demand.get(p.id, 0)
        c = round(fc.get(p.id, 0), 0)
        total = b + c
        # crude capacity check
        rows.append({"product_id": p.id, "sku": p.sku, "name": p.name,
                     "b2b_demand": b, "b2c_forecast": c, "total": total,
                     "status": "BALANCED"})
    return ok(rows)

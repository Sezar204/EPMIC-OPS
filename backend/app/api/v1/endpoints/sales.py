Input
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.schemas.sales import SalesOrderCreate, SalesOrderUpdate
from app.services.operations import SalesService
from app.repositories.modules import SalesOrderRepo, CustomerRepo
from app.models import SalesOrder, SalesOrderLine

router = APIRouter()


@router.get("/orders/{factory_id}")
def list_orders(factory_id: int, db: Session = Depends(get_db)):
    items = db.query(SalesOrder).filter(SalesOrder.factory_id == factory_id).all()
    return ok([{
        "id": i.id, "factory_id": i.factory_id, "customer_id": i.customer_id,
        "order_number": i.order_number, "order_date": i.order_date.isoformat(),
        "required_delivery": i.required_delivery.isoformat(),
        "status": i.status, "total_value": i.total_value, "currency": i.currency,
        "is_rush_order": i.is_rush_order, "priority": i.priority,
    } for i in items], total=len(items))


@router.get("/orders/{factory_id}/{order_id}")
def get_order(factory_id: int, order_id: int, db: Session = Depends(get_db)):
    obj = SalesOrderRepo(db).get_with_lines(order_id)
    if not obj or obj.factory_id != factory_id: raise HTTPException(404, "Order not found")
    return ok({
        "id": obj.id, "factory_id": obj.factory_id, "customer_id": obj.customer_id,
        "order_number": obj.order_number, "order_date": obj.order_date.isoformat(),
        "required_delivery": obj.required_delivery.isoformat(),
        "status": obj.status, "total_value": obj.total_value, "currency": obj.currency,
        "is_rush_order": obj.is_rush_order, "priority": obj.priority,
        "lines": [{
            "id": l.id, "product_id": l.product_id, "quantity": l.quantity,
            "unit_price": l.unit_price, "line_total": l.line_total,
        } for l in (obj.lines or [])],
    })


@router.post("/orders/{factory_id}")
def create_order(factory_id: int, payload: SalesOrderCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    lines = data.pop("lines", [])
    obj = SalesOrder(factory_id=factory_id, total_value=0, **data)
    db.add(obj); db.flush()
    total = 0
    for ln in lines:
        ln_total = ln["quantity"] * ln["unit_price"] * (1 - ln.get("discount_pct", 0) / 100)
        db.add(SalesOrderLine(order_id=obj.id, line_total=ln_total, **ln))
        total += ln_total
    obj.total_value = total
    db.commit()
    return ok({"id": obj.id}, "Order created")


@router.put("/orders/{factory_id}/{order_id}")
def update_order(factory_id: int, order_id: int, payload: SalesOrderUpdate, db: Session = Depends(get_db)):
    obj = SalesOrderRepo(db).get(order_id)
    if not obj or obj.factory_id != factory_id: raise HTTPException(404, "Order not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit()
    return ok(None, "Order updated")


@router.delete("/orders/{factory_id}/{order_id}")
def delete_order(factory_id: int, order_id: int, db: Session = Depends(get_db)):
    ok_flag = SalesOrderRepo(db).delete(order_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Order not found")
    db.commit()
    return ok(None, "Order deleted")


@router.post("/orders/{factory_id}/{order_id}/ctp-analysis")
def ctp(factory_id: int, order_id: int, db: Session = Depends(get_db)):
    return ok(SalesService.run_ctp(db, factory_id, order_id))


@router.get("/forecasts/{factory_id}")
def list_forecasts(factory_id: int, db: Session = Depends(get_db)):
    from app.engines.demand_engine import DemandEngine
    return ok(DemandEngine().forecast(db, factory_id))


@router.post("/forecasts/{factory_id}")
def save_forecasts(factory_id: int, payload: dict, db: Session = Depends(get_db)):
    from app.models import DemandForecast
    from sqlalchemy import select
    for row in payload.get("items", []):
        existing = db.scalars(select(DemandForecast).where(
            DemandForecast.factory_id == factory_id,
            DemandForecast.product_id == row["product_id"],
            DemandForecast.period_date == row["period_date"],
        )).first()
        if existing:
            existing.manual_adjusted_qty = row.get("manual_adjusted_qty")
            existing.final_qty = row.get("manual_adjusted_qty") or existing.system_forecast_qty
    db.commit()
    return ok(None, "Forecasts saved")


@router.get("/sop/{factory_id}")
def sop(factory_id: int, db: Session = Depends(get_db)):
    from app.engines.executive_engine import ExecutiveEngine
    from app.engines.demand_engine import DemandEngine
    DemandEngine().run(db, factory_id)
    forecasts = db.query(__import__('app.models', fromlist=['DemandForecast']).DemandForecast).filter_by(factory_id=factory_id).all()
    products = {p.id: p for p in db.query(__import__('app.models', fromlist=['Product']).Product).filter_by(factory_id=factory_id).all()}
    out = []
    for f in forecasts:
        p = products.get(f.product_id)
        if not p: continue
        out.append({
            "product_id": p.id, "product_sku": p.sku, "product_name": p.name,
            "b2b_demand": 0, "b2c_forecast": f.system_forecast_qty,
            "total": f.final_qty, "capacity": 10000, "gap": 0,
            "status": "BALANCED" if f.final_qty < 10000 else "GAP",
        })
    return ok(out)

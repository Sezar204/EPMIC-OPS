Input
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.engines.alert_engine       import AlertEngine
from app.engines.mrp_engine         import MRPEngine
from app.engines.inventory_engine   import InventoryEngine
from app.engines.demand_engine      import DemandEngine
from app.engines.capacity_engine    import CapacityEngine
from app.engines.procurement_engine import ProcurementEngine
from app.engines.executive_engine   import ExecutiveEngine
from app.engines.what_if_engine     import WhatIfEngine

router = APIRouter()


@router.post("/run/all/{factory_id}")
def run_all(factory_id: int, db: Session = Depends(get_db)):
    r = ExecutiveEngine().run(db, factory_id)
    return ok({"engines": r.data.get("engines", {}),
               "decisions_created": r.decisions_created,
               "alerts_created": r.alerts_created,
               "items": r.items_processed})


@router.post("/run/mrp/{factory_id}")
def run_mrp(factory_id: int, db: Session = Depends(get_db)):
    r = MRPEngine().run(db, factory_id)
    return ok(r.data)


@router.post("/run/alerts/{factory_id}")
def run_alerts(factory_id: int, db: Session = Depends(get_db)):
    r = AlertEngine().run(db, factory_id)
    return ok({"alerts_created": r.alerts_created, "items": r.items_processed})


@router.post("/run/inventory/{factory_id}")
def run_inventory(factory_id: int, db: Session = Depends(get_db)):
    r = InventoryEngine().run(db, factory_id)
    return ok(r.data)


@router.post("/run/demand/{factory_id}")
def run_demand(factory_id: int, db: Session = Depends(get_db)):
    r = DemandEngine().run(db, factory_id)
    return ok({"forecasts": r.data.get("forecasts", []), "items": r.items_processed})


@router.post("/run/capacity/{factory_id}")
def run_capacity(factory_id: int, db: Session = Depends(get_db)):
    r = CapacityEngine().run(db, factory_id)
    return ok(r.data)


@router.post("/simulate/what-if/{factory_id}")
def simulate(factory_id: int, payload: dict, db: Session = Depends(get_db)):
    r = WhatIfEngine().run(
        db, factory_id,
        scenario_type=payload.get("scenario_type", "DEMAND_CHANGE"),
        parameters=payload.get("parameters", {}),
        horizon_days=payload.get("horizon_days", 14),
    )
    return ok(r.data)

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ok
from app.engines.alert_engine import AlertEngine
from app.engines.mrp_engine import MRPEngine
from app.engines.inventory_engine import InventoryEngine
from app.engines.demand_engine import DemandEngine
from app.engines.capacity_engine import CapacityEngine
from app.engines.procurement_engine import ProcurementEngine
from app.engines.production_engine import ProductionEngine
from app.engines.maintenance_engine import MaintenanceEngine
from app.engines.quality_engine import QualityEngine
from app.engines.bottleneck_engine import BottleneckEngine
from app.engines.executive_engine import ExecutiveEngine
from app.engines.what_if_engine import WhatIfEngine

router = APIRouter()


def _run(engine, db: Session, fid: int, body: dict | None = None):
    if isinstance(engine, WhatIfEngine):
        return engine.execute(db, fid, body).to_dict()
    return engine.execute(db, fid).to_dict()


@router.post("/run/all/{factory_id}")
def run_all(factory_id: int, db: Session = Depends(get_db)):
    results = {}
    for name, eng in [
        ("alerts", AlertEngine()), ("mrp", MRPEngine()), ("inventory", InventoryEngine()),
        ("demand", DemandEngine()), ("capacity", CapacityEngine()),
        ("procurement", ProcurementEngine()), ("production", ProductionEngine()),
        ("maintenance", MaintenanceEngine()), ("quality", QualityEngine()),
        ("bottleneck", BottleneckEngine()), ("executive", ExecutiveEngine()),
    ]:
        try:
            results[name] = _run(eng, db, factory_id)
        except Exception as e:  # pragma: no cover
            results[name] = {"engine": name, "success": False, "message": str(e), "data": {}}
    return ok(results, "All engines executed")


@router.post("/run/mrp/{factory_id}")
def run_mrp(factory_id: int, db: Session = Depends(get_db)):
    return ok(_run(MRPEngine(), db, factory_id), "MRP executed")


@router.post("/run/alerts/{factory_id}")
def run_alerts(factory_id: int, db: Session = Depends(get_db)):
    return ok(_run(AlertEngine(), db, factory_id), "Alerts evaluated")


@router.post("/run/inventory/{factory_id}")
def run_inventory(factory_id: int, db: Session = Depends(get_db)):
    return ok(_run(InventoryEngine(), db, factory_id), "Inventory analyzed")


@router.post("/run/demand/{factory_id}")
def run_demand(factory_id: int, db: Session = Depends(get_db)):
    return ok(_run(DemandEngine(), db, factory_id), "Demand forecasted")


@router.post("/run/capacity/{factory_id}")
def run_capacity(factory_id: int, db: Session = Depends(get_db)):
    return ok(_run(CapacityEngine(), db, factory_id), "Capacity analyzed")


@router.post("/simulate/what-if/{factory_id}")
def simulate(factory_id: int, body: dict = Body(...), db: Session = Depends(get_db)):
    return ok(_run(WhatIfEngine(), db, factory_id, body), "Simulation complete")

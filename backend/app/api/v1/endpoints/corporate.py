from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.crud import serialize
from app.core.response import ok
from app.models.factory import Factory
from app.models.alert import Alert, Decision
from app.models.production import ProductionLine, ProductionOrder
from app.models.product import Product
from app.models.inventory import RawMaterial, InventoryRawMaterial

router = APIRouter()


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    factories = db.scalars(select(Factory).where(Factory.is_deleted == False)).all()
    out = []
    for f in factories:
        fid = f.id
        lines = db.scalars(select(ProductionLine).where(ProductionLine.factory_id == fid, ProductionLine.is_deleted == False)).all()
        orders = db.scalars(select(ProductionOrder).where(ProductionOrder.factory_id == fid)).all()
        produced = sum(o.produced_qty for o in orders)
        planned = sum(o.planned_qty for o in orders)
        crit_q = select(func.count()).select_from(Alert).where(
            Alert.factory_id == fid, Alert.is_resolved == False,
            Alert.severity.in_(["critical", "emergency"]))
        crit = db.scalar(crit_q) or 0
        out.append({"id": fid, "name": f.name, "code": f.code, "status": f.status,
                    "lines": len(lines), "produced": round(produced, 0), "planned": round(planned, 0),
                    "critical_alerts": crit})
    return ok(out)


@router.get("/critical-alerts")
def critical_alerts(db: Session = Depends(get_db)):
    rows = db.scalars(select(Alert).where(
        Alert.is_resolved == False, Alert.severity.in_(["critical", "emergency"])
    ).order_by(Alert.created_at.desc())).all()
    return ok([serialize(r) for r in rows])


@router.get("/pending-decisions")
def pending_decisions(db: Session = Depends(get_db)):
    rows = db.scalars(select(Decision).where(Decision.status == "pending").order_by(
        Decision.priority != "urgent", Decision.created_at.desc())).all()
    return ok([serialize(r) for r in rows])


@router.get("/group-kpis")
def group_kpis(db: Session = Depends(get_db)):
    factories = db.scalars(select(Factory).where(Factory.is_deleted == False)).all()
    total_output = 0
    oee_sum = 0
    otif_sum = 0
    qual_sum = 0
    n = 0
    for f in factories:
        orders = db.scalars(select(ProductionOrder).where(ProductionOrder.factory_id == f.id)).all()
        produced = sum(o.produced_qty for o in orders)
        planned = sum(o.planned_qty for o in orders)
        total_output += produced
        oee_sum += (produced / planned * 100) if planned else 0
        n += 1
    return ok({
        "total_output": round(total_output, 0),
        "avg_oee": round(oee_sum / n, 1) if n else 0,
        "avg_otif": round(otif_sum / n, 1) if n else 0,
        "avg_quality": round(qual_sum / n, 1) if n else 0,
        "factory_count": n,
    })

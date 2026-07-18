Input
"""Executive engine — aggregates all engines and produces prioritized decisions."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.engines import BaseEngine, EngineResult
from app.engines.alert_engine    import AlertEngine
from app.engines.mrp_engine      import MRPEngine
from app.engines.inventory_engine import InventoryEngine
from app.engines.demand_engine   import DemandEngine
from app.engines.production_engine import ProductionEngine
from app.engines.capacity_engine  import CapacityEngine
from app.engines.procurement_engine import ProcurementEngine
from app.engines.maintenance_engine import MaintenanceEngine
from app.engines.quality_engine   import QualityEngine
from app.engines.bottleneck_engine import BottleneckEngine
from app.models import Decision, Alert


class ExecutiveEngine(BaseEngine):
    name = "executive"

    def _execute(self, db: Session, factory_id: int, r: EngineResult, **kwargs):
        runs = {
            "alerts":      AlertEngine().run(db, factory_id),
            "mrp":         MRPEngine().run(db, factory_id),
            "inventory":   InventoryEngine().run(db, factory_id),
            "demand":      DemandEngine().run(db, factory_id),
            "production":  ProductionEngine().run(db, factory_id),
            "capacity":    CapacityEngine().run(db, factory_id),
            "procurement": ProcurementEngine().run(db, factory_id),
            "maintenance": MaintenanceEngine().run(db, factory_id),
            "quality":     QualityEngine().run(db, factory_id),
            "bottleneck":  BottleneckEngine().run(db, factory_id),
        }
        r.data["engines"] = {k: {"success": v.success, "items": v.items_processed, "alerts": v.alerts_created} for k, v in runs.items()}

        # Build decision recommendations
        alerts = db.scalars(select(Alert).where(
            Alert.factory_id == factory_id,
            Alert.is_resolved == False,  # noqa: E712
        )).order_by(Alert.severity.desc(), Alert.created_at.desc()).limit(10).all()

        for a in alerts:
            existing = db.scalars(select(Decision).where(
                Decision.factory_id == factory_id,
                Decision.decision_type == a.alert_type,
                Decision.status == "pending",
            )).first()
            if existing: continue
            priority = "urgent" if a.severity == "emergency" else (
                "high" if a.severity == "critical" else "medium"
            )
            db.add(Decision(
                factory_id=factory_id,
                decision_type=a.alert_type,
                title=f"Address: {a.title}",
                description=a.message,
                recommendation=f"Investigate and resolve the {a.alert_type} alert.",
                priority=priority,
                status="pending",
            ))
            r.decisions_created += 1

        r.items_processed = sum(v.items_processed for v in runs.values())
        r.alerts_created   = sum(v.alerts_created for v in runs.values())
        db.commit()

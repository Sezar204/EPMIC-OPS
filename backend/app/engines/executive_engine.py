from datetime import timedelta

from sqlalchemy import select, func

from app.engines.base import BaseEngine
from app.engines.capacity_engine import CapacityEngine
from app.engines.alert_engine import AlertEngine
from app.engines.inventory_engine import InventoryEngine
from app.models.alert import Alert, Decision


class ExecutiveEngine(BaseEngine):
    name = "executive_engine"

    def execute(self, db, factory_id: int):
        decisions = []
        # run supporting engines
        cap = CapacityEngine().execute(db, factory_id)
        inv = InventoryEngine().execute(db, factory_id)
        AlertEngine().execute(db, factory_id)

        # bottleneck -> decision
        bottlenecks = sorted(cap.data.get("lines", []), key=lambda x: x["utilization"], reverse=True)
        if bottlenecks and bottlenecks[0]["utilization"] > 100:
            d = self._make_decision(db, factory_id, "capacity", "Add shift to relieve bottleneck",
                                    f"{bottlenecks[0]['line']} at {bottlenecks[0]['utilization']}% utilization.",
                                    "Schedule night shift.", "high")
            decisions.append(d)
        # critical inventory
        critical = [i for i in inv.data.get("items", []) if i["coverage_days"] < 3]
        if critical:
            d = self._make_decision(db, factory_id, "procurement", "Expedite critical material purchases",
                                    f"{len(critical)} materials below 3 days coverage.",
                                    "Issue emergency POs.", "urgent")
            decisions.append(d)
        # unresolved critical alerts
        crit = db.scalar(select(func.count()).select_from(Alert).where(
            Alert.factory_id == factory_id, Alert.is_resolved == False,
            Alert.severity.in_(["critical", "emergency"]))) or 0
        if crit:
            d = self._make_decision(db, factory_id, "operations", "Resolve critical alerts",
                                    f"{crit} critical alerts open.", "Triage by severity.", "urgent")
            decisions.append(d)
        db.commit()
        return self._ok(f"Generated {len(decisions)} decisions",
                        {"decisions": decisions, "bottlenecks": bottlenecks[:3]})

    def _make_decision(self, db, fid, dtype, title, desc, rec, prio):
        d = Decision(factory_id=fid, decision_type=dtype, title=title, description=desc,
                     recommendation=rec, priority=prio, status="pending")
        db.add(d)
        db.flush()
        return {"id": d.id, "title": title, "priority": prio}

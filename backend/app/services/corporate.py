Input
"""Corporate / multi-factory aggregate view."""
from datetime import date, datetime, timedelta
from typing import List
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models import Factory, Alert, Decision, ProductionOrder
from app.services.core import HealthService


class CorporateService:
    @staticmethod
    def overview(db: Session) -> dict:
        factories = db.scalars(select(Factory).where(Factory.is_deleted == False)).all()  # noqa: E712
        if not factories:
            return {
                "factories": [],
                "summary": {
                    "total_factories": 0,
                    "active_factories": 0,
                    "critical_alerts": 0,
                    "pending_decisions": 0,
                    "avg_health_score": 0,
                },
            }
        factory_summaries = []
        for f in factories:
            health = HealthService.factory_health_score(db, f.id)
            factory_summaries.append({
                "id": f.id,
                "name": f.name,
                "code": f.code,
                "type": f.type,
                "status": f.status,
                "currency": f.currency,
                "health_score": health["total_score"],
                "health_status": health["status"],
            })

        crit_count = db.execute(
            select(func.count(Alert.id))
            .where(Alert.is_resolved == False, Alert.severity.in_(["critical", "emergency"]))  # noqa: E712
        ).scalar() or 0
        pend_count = db.execute(
            select(func.count(Decision.id)).where(Decision.status == "pending")
        ).scalar() or 0

        return {
            "factories": factory_summaries,
            "summary": {
                "total_factories":   len(factories),
                "active_factories":  sum(1 for f in factories if f.status == "active"),
                "critical_alerts":   crit_count,
                "pending_decisions": pend_count,
                "avg_health_score":  round(
                    sum(fs["health_score"] for fs in factory_summaries) / max(1, len(factory_summaries)), 1
                ),
            },
        }

    @staticmethod
    def critical_alerts(db: Session) -> List[dict]:
        rows = db.scalars(
            select(Alert)
            .where(Alert.is_resolved == False, Alert.severity.in_(["critical", "emergency"]))  # noqa: E712
            .order_by(Alert.created_at.desc())
            .limit(100)
        ).all()
        return [_alert_to_dict(db, a) for a in rows]

    @staticmethod
    def pending_decisions(db: Session) -> List[dict]:
        rows = db.scalars(
            select(Decision)
            .where(Decision.status == "pending")
            .order_by(Decision.priority.desc(), Decision.created_at.desc())
            .limit(100)
        ).all()
        return [{
            "id": d.id,
            "factory_id": d.factory_id,
            "title": d.title,
            "description": d.description,
            "recommendation": d.recommendation,
            "priority": d.priority,
            "decision_type": d.decision_type,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        } for d in rows]

    @staticmethod
    def group_kpis(db: Session) -> dict:
        # Average of last 7 days across all KPIs across all factories
        cutoff = date.today() - timedelta(days=7)
        factories = db.scalars(select(Factory).where(Factory.is_deleted == False)).all()  # noqa: E712
        factory_ids = [f.id for f in factories]
        if not factory_ids:
            return {"total_output": 0, "avg_oee": 0, "avg_otif": 0, "avg_quality": 0}
        from app.models import ProductionOrder, KPIValue, KPIDefinition
        orders = db.scalars(select(ProductionOrder).where(
            ProductionOrder.factory_id.in_(factory_ids),
            ProductionOrder.planned_start >= cutoff,
        )).all()
        total_output = sum(o.actual_qty for o in orders)

        def kpi_avg(code: str) -> float:
            defs = db.scalars(select(KPIDefinition).where(KPIDefinition.code == code)).all()
            def_ids = [d.id for d in defs]
            if not def_ids: return 0
            vals = db.scalars(select(KPIValue).where(
                KPIValue.kpi_id.in_(def_ids), KPIValue.period_date >= cutoff
            )).all()
            return round(sum(v.value for v in vals) / max(1, len(vals)), 1)

        return {
            "total_output": round(total_output, 0),
            "avg_oee":     kpi_avg("OEE"),
            "avg_otif":    kpi_avg("OTIF"),
            "avg_quality": kpi_avg("QUALITY_FPY"),
        }


def _alert_to_dict(db: Session, a: Alert) -> dict:
    factory = db.get(Factory, a.factory_id) if a.factory_id else None
    return {
        "id": a.id,
        "factory_id": a.factory_id,
        "factory_name": factory.name if factory else None,
        "alert_type": a.alert_type,
        "severity": a.severity,
        "title": a.title,
        "message": a.message,
        "is_read": a.is_read,
        "is_resolved": a.is_resolved,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }

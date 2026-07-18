Input
"""Core / system services (factory health, dashboard summary, settings, etc.)."""
import platform
import time
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from app.core.config import DB_PATH, settings
from app.repositories.modules import (
    FactoryRepo, AlertRepo, DecisionRepo, ProductionOrderRepo,
    InventoryRawMaterialRepo, RawMaterialRepo, KPIDefinitionRepo, KPIValueRepo,
    ProductionLineRepo, MachineRepo, AppSettingRepo, WorkerRepo, AttendanceRepo,
)
from app.models import (
    SalesOrder, SalesOrderLine, ProductionOrder, InventoryRawMaterial,
    RawMaterial, KPIDefinition, KPIValue, Alert, Decision, Factory,
)
from app.engines.alert_engine import AlertEngine
from app.engines.executive_engine import ExecutiveEngine
from app.utils.backup import BackupService


class HealthService:
    @staticmethod
    def factory_health_score(db: Session, factory_id: int) -> dict:
        """Compute a 0–100 health score by combining six sub-scores."""
        # 1. Plan adherence — last 14 days actual vs planned
        cutoff = date.today() - timedelta(days=14)
        prod_orders = db.scalars(select(ProductionOrder).where(
            ProductionOrder.factory_id == factory_id,
            ProductionOrder.planned_start >= cutoff,
        )).all()
        if prod_orders:
            total_planned = sum(p.planned_qty for p in prod_orders) or 1
            total_actual  = sum(p.actual_qty for p in prod_orders)
            plan_adherence = min(100, (total_actual / total_planned) * 100)
        else:
            plan_adherence = 80.0

        # 2. Machine availability
        machines = MachineRepo(db).list(factory_id=factory_id)
        if machines:
            available = sum(1 for m in machines if m.status == "active")
            machine_availability = (available / len(machines)) * 100
        else:
            machine_availability = 100.0

        # 3. Quality rate
        checks = db.scalars(select(__import__('app.models', fromlist=['QualityCheck']).QualityCheck).where(
            __import__('app.models', fromlist=['QualityCheck']).QualityCheck.factory_id == factory_id,
            __import__('app.models', fromlist=['QualityCheck']).QualityCheck.checked_at >= datetime.utcnow() - timedelta(days=30),
        )).all()
        if checks:
            passed = sum(1 for c in checks if c.status == "passed")
            quality_rate = (passed / len(checks)) * 100
        else:
            quality_rate = 95.0

        # 4. Inventory health
        inv = db.scalars(select(InventoryRawMaterial).where(
            InventoryRawMaterial.factory_id == factory_id
        )).all()
        materials = {m.id: m for m in RawMaterialRepo(db).list(factory_id=factory_id)}
        if inv:
            critical = 0
            for i in inv:
                mat = materials.get(i.material_id)
                if mat and i.qty_on_hand < mat.safety_stock_qty:
                    critical += 1
            inventory_health = max(0, 100 - (critical / len(inv)) * 100)
        else:
            inventory_health = 90.0

        # 5. Order fulfillment
        sos = db.scalars(select(SalesOrder).where(SalesOrder.factory_id == factory_id)).all()
        if sos:
            delivered = sum(1 for s in sos if s.status == "delivered")
            order_fulfillment = (delivered / len(sos)) * 100
        else:
            order_fulfillment = 90.0

        # 6. Workforce stability
        recent_att = db.scalars(select(AttendanceRepo.db.bind, AttendanceRepo.model)).all() if False else []
        from app.models import AttendanceRecord
        recent_att = db.scalars(select(AttendanceRecord).where(
            AttendanceRecord.factory_id == factory_id,
            AttendanceRecord.attendance_date >= date.today() - timedelta(days=7),
        )).all()
        if recent_att:
            present = sum(1 for a in recent_att if a.status == "present")
            workforce_stability = (present / len(recent_att)) * 100
        else:
            workforce_stability = 92.0

        weights = {
            "plan_adherence": 0.20, "machine_availability": 0.15,
            "quality_rate": 0.20, "inventory_health": 0.15,
            "order_fulfillment": 0.20, "workforce_stability": 0.10,
        }
        total = (
            plan_adherence      * weights["plan_adherence"]      +
            machine_availability * weights["machine_availability"] +
            quality_rate        * weights["quality_rate"]        +
            inventory_health    * weights["inventory_health"]    +
            order_fulfillment   * weights["order_fulfillment"]   +
            workforce_stability * weights["workforce_stability"]
        )

        if   total >= 90: status = "excellent"
        elif total >= 75: status = "good"
        elif total >= 60: status = "warning"
        else:             status = "critical"

        return {
            "factory_id": factory_id,
            "total_score": round(total, 1),
            "plan_adherence": round(plan_adherence, 1),
            "machine_availability": round(machine_availability, 1),
            "quality_rate": round(quality_rate, 1),
            "inventory_health": round(inventory_health, 1),
            "order_fulfillment": round(order_fulfillment, 1),
            "workforce_stability": round(workforce_stability, 1),
            "status": status,
        }


class DashboardService:
    @staticmethod
    def summary(db: Session, factory_id: int) -> dict:
        health = HealthService.factory_health_score(db, factory_id)
        critical_alerts = db.scalars(select(Alert).where(
            Alert.factory_id == factory_id,
            Alert.is_resolved == False,  # noqa: E712
            Alert.severity.in_(["critical", "emergency"]),
        )).all()
        pending_decisions = DecisionRepo(db).pending(factory_id)

        # Today's production
        today = date.today()
        today_orders = db.scalars(select(ProductionOrder).where(
            ProductionOrder.factory_id == factory_id,
            ProductionOrder.planned_start <= today,
            ProductionOrder.planned_end >= today,
        )).all()
        planned = sum(p.planned_qty for p in today_orders)
        actual  = sum(p.actual_qty  for p in today_orders)
        lines_today = [
            {"line_id": p.line_id, "product_id": p.product_id,
             "planned": p.planned_qty, "actual": p.actual_qty,
             "status": p.status}
            for p in today_orders if p.line_id is not None
        ]

        # KPIs
        kpi_defs = KPIDefinitionRepo(db).list(factory_id=factory_id)
        kpi_summary = {}
        for d in kpi_defs[:8]:
            trend = KPIValueRepo(db).trend(d.id, factory_id, days=1)
            if trend:
                kpi_summary[d.code] = {
                    "value": trend[-1].value,
                    "status": trend[-1].status,
                    "target": d.target_value,
                    "unit": d.unit,
                }

        return {
            "factory_id": factory_id,
            "health_score": health["total_score"],
            "health_status": health["status"],
            "critical_alerts": len(critical_alerts),
            "pending_decisions": len(pending_decisions),
            "plan_adherence_pct": health["plan_adherence"],
            "production_today": {
                "planned": planned, "actual": actual,
                "adherence_pct": round((actual / planned) * 100, 1) if planned else 0,
            },
            "production_lines_today": lines_today,
            "kpis": kpi_summary,
        }


class SettingsService:
    @staticmethod
    def get_all(db: Session) -> dict:
        return AppSettingRepo(db).all_dict()

    @staticmethod
    def update(db: Session, payload: dict) -> dict:
        repo = AppSettingRepo(db)
        for k, v in (payload or {}).items():
            repo.set_value(str(k), str(v))
        db.commit()
        return repo.all_dict()


class SystemInfoService:
    _start = time.time()

    @classmethod
    def info(cls, db: Session) -> dict:
        backup_count = 0
        try:
            backup_count = len(BackupService().list_backups())
        except Exception:
            pass
        try:
            db_size = Path(DB_PATH).stat().st_size
        except Exception:
            db_size = 0
        return {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "os": platform.platform(),
            "db_path": str(DB_PATH),
            "db_size_bytes": db_size,
            "backup_count": backup_count,
            "uptime_seconds": time.time() - cls._start,
        }

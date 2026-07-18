Input
"""Quality, maintenance, workforce, cost services."""
from datetime import date, datetime, timedelta
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from app.models import (
    QualityCheck, NonConformanceReport, CAPARecord,
    MaintenanceSchedule, MaintenanceWorkOrder, MachineBreakdown, Machine,
    Worker, AttendanceRecord, ShiftAssignment, Shift, ProductCost, Product,
    ProductionOrder,
)
from app.repositories.modules import (
    QualityCheckRepo, NCRRepo, CAPARepo, MaintenanceScheduleRepo,
    WorkOrderRepo, BreakdownRepo, WorkerRepo, AttendanceRepo,
    ShiftAssignmentRepo, ProductCostRepo, ProductRepo,
)


class QualityService:
    @staticmethod
    def create_check(db: Session, factory_id: int, payload) -> QualityCheck:
        sample = max(1, payload.sample_size)
        rate = (payload.defects_found / sample) * 100
        status = "passed" if rate < 2 else ("failed" if rate > 5 else "on_hold")
        qc = QualityCheck(
            factory_id=factory_id,
            check_type=payload.check_type,
            reference_id=payload.reference_id,
            reference_type=payload.reference_type,
            product_id=payload.product_id,
            material_id=payload.material_id,
            sample_size=sample,
            defects_found=payload.defects_found,
            defect_rate_pct=round(rate, 2),
            status=status,
            decision=payload.decision,
            checked_at=datetime.utcnow(),
            notes=payload.notes,
        )
        db.add(qc); db.commit(); db.refresh(qc)
        return qc

    @staticmethod
    def metrics(db: Session, factory_id: int, days: int = 30) -> dict:
        cutoff = datetime.utcnow() - timedelta(days=days)
        checks = db.scalars(select(QualityCheck).where(
            QualityCheck.factory_id == factory_id,
            QualityCheck.checked_at >= cutoff,
        )).all()
        if not checks:
            return {
                "factory_id": factory_id,
                "defect_rate_pct": 0,
                "first_pass_yield_pct": 100,
                "capa_closure_rate_pct": 100,
                "supplier_quality_pct": 100,
                "weekly_defect_trend": [],
                "top_defect_categories": [],
            }
        total = len(checks)
        passed = sum(1 for c in checks if c.status == "passed")
        avg_defect = sum(c.defect_rate_pct for c in checks) / total
        capas = db.scalars(select(CAPARecord).where(CAPARecord.factory_id == factory_id)).all()
        capa_closed = sum(1 for c in capas if c.status == "closed")
        capa_closure = (capa_closed / len(capas) * 100) if capas else 100

        # Weekly trend (last 8 weeks)
        weekly = {}
        for c in checks:
            wk = c.checked_at.strftime("%G-W%V") if c.checked_at else "unknown"
            weekly.setdefault(wk, []).append(c.defect_rate_pct)
        trend = [{"period": k, "value": round(sum(v) / len(v), 2)} for k, v in sorted(weekly.items())]

        return {
            "factory_id": factory_id,
            "defect_rate_pct": round(avg_defect, 2),
            "first_pass_yield_pct": round((passed / total) * 100, 1),
            "capa_closure_rate_pct": round(capa_closure, 1),
            "supplier_quality_pct": 96.5,
            "weekly_defect_trend": trend,
            "top_defect_categories": [
                {"category": "Packaging", "count": 5},
                {"category": "Seal",      "count": 3},
                {"category": "Label",     "count": 2},
            ],
        }


class MaintenanceService:
    @staticmethod
    def metrics(db: Session, factory_id: int) -> dict:
        machines = db.scalars(select(Machine).where(Machine.factory_id == factory_id)).all()
        wos = db.scalars(select(MaintenanceWorkOrder).where(
            MaintenanceWorkOrder.factory_id == factory_id
        )).all()
        total = len(machines) or 1
        avail = sum(1 for m in machines if m.status == "active") / total * 100
        completed = [w for w in wos if w.status == "completed" and w.downtime_hours]
        mttr = (sum(w.downtime_hours for w in completed) / len(completed)) if completed else 2.0
        # Synthetic MTBF
        mtbf = 168.0
        schedules = db.scalars(select(MaintenanceSchedule).where(
            MaintenanceSchedule.factory_id == factory_id,
            MaintenanceSchedule.is_active == 1,
        )).all()
        overdue = sum(1 for s in schedules if s.next_due_date and s.next_due_date < date.today())
        pm_compliance = (1 - overdue / max(1, len(schedules))) * 100 if schedules else 100
        return {
            "factory_id": factory_id,
            "availability_pct": round(avail, 1),
            "avg_mtbf_hours": round(mtbf, 1),
            "avg_mttr_hours": round(mttr, 1),
            "pm_compliance_pct": round(pm_compliance, 1),
            "availability_trend": [
                {"date": (date.today() - timedelta(days=i)).isoformat(),
                 "value": round(avail + (i % 3 - 1) * 1.5, 1)}
                for i in range(14, -1, -1)
            ],
            "breakdown_frequency": [
                {"machine_id": m.id, "count": sum(1 for w in wos if w.machine_id == m.id)}
                for m in machines
            ],
        }

    @staticmethod
    def asset_summary(db: Session, factory_id: int) -> list:
        machines = db.scalars(select(Machine).where(Machine.factory_id == factory_id)).all()
        wos = db.scalars(select(MaintenanceWorkOrder).where(
            MaintenanceWorkOrder.factory_id == factory_id
        )).all()
        schedules = {s.machine_id: s for s in db.scalars(select(MaintenanceSchedule).where(
            MaintenanceSchedule.factory_id == factory_id
        )).all()}
        out = []
        for m in machines:
            m_wos = [w for w in wos if w.machine_id == m.id]
            open_wos = sum(1 for w in m_wos if w.status not in ("completed", "cancelled"))
            downtime = sum(w.downtime_hours for w in m_wos if w.status == "completed")
            mttr = downtime / max(1, sum(1 for w in m_wos if w.status == "completed"))
            sch = schedules.get(m.id)
            out.append({
                "machine_id": m.id,
                "code": m.code,
                "name": m.name,
                "line_name": None,
                "status": m.status,
                "availability_pct": 100 if m.status == "active" else (50 if m.status == "maintenance" else 0),
                "mtbf_hours": 168.0,
                "mttr_hours": round(mttr, 1),
                "next_pm_date": sch.next_due_date.isoformat() if sch and sch.next_due_date else None,
                "open_work_orders": open_wos,
            })
        return out


class WorkforceService:
    @staticmethod
    def metrics(db: Session, factory_id: int) -> dict:
        workers = db.scalars(select(Worker).where(Worker.factory_id == factory_id)).all()
        cutoff = date.today() - timedelta(days=7)
        att = db.scalars(select(AttendanceRecord).where(
            AttendanceRecord.factory_id == factory_id,
            AttendanceRecord.attendance_date >= cutoff,
        )).all()
        present = sum(1 for a in att if a.status == "present")
        total_ot = sum(a.ot_hours for a in att)
        attendance_rate = (present / len(att) * 100) if att else 95
        absenteeism = 100 - attendance_rate

        # OT by worker (top 10)
        ot_by_worker = {}
        for a in att:
            ot_by_worker.setdefault(a.worker_id, 0)
            ot_by_worker[a.worker_id] += a.ot_hours
        top_ot = sorted(ot_by_worker.items(), key=lambda x: -x[1])[:10]
        worker_map = {w.id: w for w in workers}
        ot_rows = [
            {"worker_id": wid, "name": worker_map[wid].name if wid in worker_map else "?",
             "ot_hours": round(hrs, 1)}
            for wid, hrs in top_ot
        ]

        return {
            "factory_id": factory_id,
            "attendance_rate_pct": round(attendance_rate, 1),
            "absenteeism_pct": round(absenteeism, 1),
            "total_ot_hours": round(total_ot, 1),
            "headcount": len([w for w in workers if w.status == "active"]),
            "attendance_trend": [
                {"date": (date.today() - timedelta(days=i)).isoformat(),
                 "value": round(attendance_rate + (i % 3 - 1) * 1.2, 1)}
                for i in range(13, -1, -1)
            ],
            "ot_by_worker": ot_rows,
        }


class CostService:
    @staticmethod
    def save_cost(db: Session, factory_id: int, payload) -> ProductCost:
        std = payload.std_total_cost or (payload.std_material_cost + payload.std_labor_cost + payload.std_overhead_cost)
        act = payload.act_total_cost or (payload.act_material_cost + payload.act_labor_cost + payload.act_overhead_cost)
        cost = ProductCost(
            factory_id=factory_id,
            product_id=payload.product_id,
            period_date=payload.period_date,
            std_material_cost=payload.std_material_cost,
            act_material_cost=payload.act_material_cost,
            std_labor_cost=payload.std_labor_cost,
            act_labor_cost=payload.act_labor_cost,
            std_overhead_cost=payload.std_overhead_cost,
            act_overhead_cost=payload.act_overhead_cost,
            std_total_cost=std,
            act_total_cost=act,
            revenue=payload.revenue,
            notes=payload.notes,
        )
        db.add(cost); db.commit(); db.refresh(cost)
        return cost

    @staticmethod
    def variance_analysis(db: Session, factory_id: int, period_date: Optional[date] = None) -> dict:
        if period_date is None:
            period_date = date.today().replace(day=1)
        costs = db.scalars(select(ProductCost).where(
            ProductCost.factory_id == factory_id,
            ProductCost.period_date == period_date,
        )).all()
        products = {p.id: p for p in ProductRepo(db).list(factory_id=factory_id)}
        rows = []
        total_var = mat_var = lab_var = oh_var = 0
        for c in costs:
            prod = products.get(c.product_id)
            if not prod: continue
            mat_v = c.act_material_cost - c.std_material_cost
            lab_v = c.act_labor_cost    - c.std_labor_cost
            oh_v  = c.act_overhead_cost - c.std_overhead_cost
            tot_v = mat_v + lab_v + oh_v
            total_var += tot_v; mat_var += mat_v; lab_var += lab_v; oh_var += oh_v
            var_pct = (tot_v / c.std_total_cost * 100) if c.std_total_cost else 0
            rows.append({
                "product_id": c.product_id,
                "product_sku": prod.sku,
                "product_name": prod.name,
                "std_total": round(c.std_total_cost, 2),
                "act_total": round(c.act_total_cost, 2),
                "variance": round(tot_v, 2),
                "variance_pct": round(var_pct, 1),
            })
        return {
            "factory_id": factory_id,
            "period": period_date.isoformat(),
            "total_variance": round(total_var, 2),
            "material_variance": round(mat_var, 2),
            "labor_variance": round(lab_var, 2),
            "overhead_variance": round(oh_var, 2),
            "by_product": rows,
        }

    @staticmethod
    def profitability(db: Session, factory_id: int, period_date: Optional[date] = None) -> dict:
        if period_date is None:
            period_date = date.today().replace(day=1)
        va = CostService.variance_analysis(db, factory_id, period_date)
        products = {p.id: p for p in ProductRepo(db).list(factory_id=factory_id)}
        costs = db.scalars(select(ProductCost).where(
            ProductCost.factory_id == factory_id,
            ProductCost.period_date == period_date,
        )).all()
        rows = []
        total_rev = total_cost = 0
        for c in sorted(costs, key=lambda x: -x.revenue):
            prod = products.get(c.product_id)
            if not prod: continue
            margin = c.revenue - c.act_total_cost
            margin_pct = (margin / c.revenue * 100) if c.revenue else 0
            total_rev += c.revenue
            total_cost += c.act_total_cost
            rows.append({
                "product_id": c.product_id,
                "product_sku": prod.sku,
                "product_name": prod.name,
                "revenue": round(c.revenue, 2),
                "cost":    round(c.act_total_cost, 2),
                "margin":  round(margin, 2),
                "margin_pct": round(margin_pct, 1),
                "trend": [round(margin_pct + (i - 3) * 0.5, 1) for i in range(7)],
            })
        gross = total_rev - total_cost
        return {
            "factory_id": factory_id,
            "period": period_date.isoformat(),
            "total_revenue": round(total_rev, 2),
            "total_cost":    round(total_cost, 2),
            "gross_profit":  round(gross, 2),
            "avg_margin_pct": round((gross / total_rev * 100) if total_rev else 0, 1),
            "rows": sorted(rows, key=lambda r: r["margin_pct"], reverse=True),
        }

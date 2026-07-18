from datetime import timedelta

from sqlalchemy import select, func

from app.engines.base import BaseEngine
from app.models.quality import QualityCheck, CAPARecord
from app.models.procurement import PurchaseOrder, PurchaseOrderLine


class QualityEngine(BaseEngine):
    name = "quality_engine"

    def execute(self, db, factory_id: int):
        now = __import__("datetime").datetime.utcnow()
        total = db.scalar(select(func.count()).select_from(QualityCheck).where(QualityCheck.factory_id == factory_id)) or 0
        failed = db.scalar(select(func.count()).select_from(QualityCheck).where(
            QualityCheck.factory_id == factory_id, QualityCheck.status == "failed")) or 0
        fpy = round((total - failed) / total * 100, 1) if total else 100
        # defect trend by day (last 14)
        since = now - timedelta(days=14)
        checks = db.scalars(select(QualityCheck).where(
            QualityCheck.factory_id == factory_id, QualityCheck.checked_at >= since)).all()
        trend = {}
        for c in checks:
            day = c.checked_at.date().isoformat()
            trend.setdefault(day, {"total": 0, "failed": 0})
            trend[day]["total"] += 1
            if c.status == "failed":
                trend[day]["failed"] += 1
        defect_trend = [{"date": k, "defect_rate": round(v["failed"] / v["total"] * 100, 1)}
                        for k, v in sorted(trend.items())]
        # supplier quality
        pos = db.scalars(select(PurchaseOrder).where(PurchaseOrder.factory_id == factory_id)).all()
        lines = db.scalars(select(PurchaseOrderLine).where(
            PurchaseOrderLine.po_id.in_([p.id for p in pos]))).all()
        accepted = sum(1 for l in lines if l.quality_status == "accepted")
        supplier_quality = round(accepted / (len(lines) or 1) * 100, 1)
        overdue_capa = db.scalar(select(func.count()).select_from(CAPARecord).where(
            CAPARecord.factory_id == factory_id, CAPARecord.status != "closed",
            CAPARecord.due_date < now)) or 0
        return self._ok("Quality analysis complete",
                        {"fpy": fpy, "defect_trend": defect_trend,
                         "supplier_quality": supplier_quality, "overdue_capa": overdue_capa})

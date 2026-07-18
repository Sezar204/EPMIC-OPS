Input
"""Bottleneck engine — identifies top constraints by production impact."""
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.engines import BaseEngine, EngineResult
from app.models import (
    ProductionLine, ProductionOrder, Machine, InventoryRawMaterial, RawMaterial,
    Alert,
)


class BottleneckEngine(BaseEngine):
    name = "bottleneck"

    def _execute(self, db: Session, factory_id: int, r: EngineResult, **kwargs):
        candidates = []

        # 1. Lines with high planned load
        lines = db.scalars(select(ProductionLine).where(
            ProductionLine.factory_id == factory_id
        )).all()
        for line in lines:
            orders = db.scalars(select(ProductionOrder).where(
                ProductionOrder.factory_id == factory_id,
                ProductionOrder.line_id == line.id,
                ProductionOrder.status.in_(["planned", "in_progress"]),
            )).all()
            load = sum(o.planned_qty for o in orders)
            cap = line.capacity_per_hour * 8 * 7
            util = (load / cap * 100) if cap else 0
            if util > 80:
                candidates.append({
                    "type": "line",
                    "id": line.id, "name": line.name, "code": line.code,
                    "impact_score": round(util, 1),
                    "detail": f"Planned load {load:.0f} vs capacity {cap:.0f}",
                })

        # 2. Down machines
        for m in db.scalars(select(Machine).where(
            Machine.factory_id == factory_id, Machine.status == "down"
        )).all():
            candidates.append({
                "type": "machine", "id": m.id, "name": m.name, "code": m.code,
                "impact_score": 95, "detail": "Machine currently down",
            })

        # 3. Materials at zero
        mats = {m.id: m for m in db.scalars(select(RawMaterial).where(
            RawMaterial.factory_id == factory_id
        )).all()}
        for inv in db.scalars(select(InventoryRawMaterial).where(
            InventoryRawMaterial.factory_id == factory_id, InventoryRawMaterial.qty_on_hand <= 0
        )).all():
            mat = mats.get(inv.material_id)
            if not mat: continue
            candidates.append({
                "type": "material", "id": mat.id, "name": mat.name, "code": mat.code,
                "impact_score": 90, "detail": "Material at zero stock",
            })

        candidates.sort(key=lambda x: -x["impact_score"])
        r.data["bottlenecks"] = candidates[:10]
        r.items_processed = len(candidates)
        db.commit()

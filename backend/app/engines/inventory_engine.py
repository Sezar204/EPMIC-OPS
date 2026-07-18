Input
"""Inventory engine — ABC/XYZ classification, coverage analysis, dead/excess stock."""
from datetime import date, timedelta
from collections import defaultdict
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.engines import BaseEngine, EngineResult
from app.models import (
    InventoryRawMaterial, RawMaterial, InventoryFinishedGoods, Product,
    PurchaseOrderLine,
)


class InventoryEngine(BaseEngine):
    name = "inventory"

    def _execute(self, db: Session, factory_id: int, r: EngineResult, **kwargs):
        items = self._classify(db, factory_id)
        r.data["matrix"] = items
        r.data["dead_stock"]  = self._dead_stock(db, factory_id)
        r.data["excess_stock"] = self._excess_stock(db, factory_id)
        r.items_processed = len(items.get("matrix", []))
        db.commit()

    def _classify(self, db, factory_id):
        materials = {m.id: m for m in db.scalars(select(RawMaterial).where(
            RawMaterial.factory_id == factory_id
        )).all()}
        invs = db.scalars(select(InventoryRawMaterial).where(
            InventoryRawMaterial.factory_id == factory_id
        )).all()

        # 30-day consumption estimate from received POs
        cutoff = date.today() - timedelta(days=30)
        consumed = defaultdict(float)
        for pol in db.scalars(select(PurchaseOrderLine)).all():
            consumed[pol.material_id] += pol.qty_received or 0

        rows = []
        for inv in invs:
            mat = materials.get(inv.material_id)
            if not mat: continue
            value = inv.qty_on_hand * mat.standard_cost
            cons  = consumed.get(inv.material_id, 0) or 1
            variance = 0.3  # demo
            rows.append({
                "id": inv.material_id, "code": mat.code, "name": mat.name,
                "value": value, "variance": variance,
                "consumption": cons, "qty_on_hand": inv.qty_on_hand,
            })

        rows.sort(key=lambda x: -x["value"])
        n = len(rows) or 1
        for i, x in enumerate(rows):
            x["abc"] = "A" if i < n * 0.2 else ("B" if i < n * 0.5 else "C")
            x["xyz"] = "X" if x["variance"] < 0.2 else ("Y" if x["variance"] < 0.5 else "Z")

        cells = defaultdict(lambda: {"cell": "", "count": 0, "total_value": 0.0, "items": []})
        for x in rows:
            k = f"{x['abc']}{x['xyz']}"
            c = cells[k]
            c["cell"] = k
            c["count"] += 1
            c["total_value"] += x["value"]
            c["items"].append(x["id"])
        matrix = list(cells.values())
        return {
            "matrix": matrix,
            "total_items": len(rows),
            "total_value": round(sum(x["value"] for x in rows), 2),
        }

    def _dead_stock(self, db, factory_id):
        cutoff = date.today() - timedelta(days=180)
        materials = {m.id: m for m in db.scalars(select(RawMaterial).where(
            RawMaterial.factory_id == factory_id
        )).all()}
        out = []
        for inv in db.scalars(select(InventoryRawMaterial).where(
            InventoryRawMaterial.factory_id == factory_id
        )).all():
            if inv.last_movement_date and inv.last_movement_date < cutoff and inv.qty_on_hand > 0:
                mat = materials.get(inv.material_id)
                if not mat: continue
                out.append({
                    "material_id": inv.material_id,
                    "material_code": mat.code,
                    "material_name": mat.name,
                    "qty_on_hand": inv.qty_on_hand,
                    "value": round(inv.qty_on_hand * mat.standard_cost, 2),
                    "days_since_movement": (date.today() - inv.last_movement_date).days,
                })
        return out

    def _excess_stock(self, db, factory_id):
        materials = {m.id: m for m in db.scalars(select(RawMaterial).where(
            RawMaterial.factory_id == factory_id
        )).all()}
        out = []
        for inv in db.scalars(select(InventoryRawMaterial).where(
            InventoryRawMaterial.factory_id == factory_id
        )).all():
            mat = materials.get(inv.material_id)
            if not mat: continue
            recommended_max = (mat.safety_stock_qty or 0) * 4
            if inv.qty_on_hand > recommended_max * 1.5 and recommended_max > 0:
                excess = inv.qty_on_hand - recommended_max
                out.append({
                    "material_id": inv.material_id,
                    "material_code": mat.code,
                    "material_name": mat.name,
                    "qty_on_hand": inv.qty_on_hand,
                    "recommended_max": recommended_max,
                    "excess": round(excess, 2),
                    "cost": round(excess * mat.standard_cost, 2),
                })
        return out

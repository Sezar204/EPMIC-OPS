Input
"""Sales / production / inventory services — operations side."""
from datetime import date, datetime, timedelta
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from app.models import (
    SalesOrder, SalesOrderLine, ProductionOrder, ProductionLine, Product,
    Customer, InventoryRawMaterial, InventoryFinishedGoods, RawMaterial,
    InventoryWIP, BOMHeader, BOMLine, PurchaseOrder, PurchaseOrderLine,
    Supplier, SalesOrder,
)
from app.repositories.modules import (
    SalesOrderRepo, CustomerRepo, ProductionOrderRepo, ProductionLineRepo,
    ProductRepo, RawMaterialRepo, InventoryRawMaterialRepo,
    InventoryFinishedGoodsRepo, InventoryWIPRepo, PurchaseOrderRepo,
    SupplierRepo,
)


class SalesService:
    @staticmethod
    def run_ctp(db: Session, factory_id: int, order_id: int) -> dict:
        """Capable-to-Promise analysis: can we deliver on time?"""
        so = SalesOrderRepo(db).get_with_lines(order_id)
        if not so or so.factory_id != factory_id:
            return {"can_commit": False, "risk": "red", "details": {"reason": "Order not found"}}

        earliest = date.today()
        bottleneck = None
        for line in so.lines or []:
            prod = ProductRepo(db).get(line.product_id)
            if not prod:
                continue
            # Check raw material availability via BOM
            bom = db.scalars(select(BOMHeader).where(
                BOMHeader.product_id == prod.id, BOMHeader.status == "active"
            )).first()
            if not bom:
                continue
            bom_lines = list(bom.lines or [])
            for bl in bom_lines:
                mat = RawMaterialRepo(db).get(bl.material_id)
                inv = db.scalars(select(InventoryRawMaterial).where(
                    InventoryRawMaterial.material_id == bl.material_id,
                    InventoryRawMaterial.factory_id == factory_id,
                )).first()
                need = bl.quantity_required * line.quantity * (1 + bl.loss_factor_pct / 100)
                on_hand = inv.qty_on_hand if inv else 0
                if on_hand < need:
                    shortage = need - on_hand
                    lead = mat.lead_time_days if mat else 7
                    available = today_plus(earliest, lead)
                    if available > earliest:
                        earliest = available
                        bottleneck = f"Material {mat.code if mat else '?'} shortage ({shortage:.0f} {bl.unit})"

        risk = "green"
        if so.required_delivery and earliest > so.required_delivery:
            risk = "red"
        elif earliest >= today_plus(date.today(), 1):
            risk = "yellow"

        return {
            "can_commit": risk in ("green", "yellow"),
            "committed_date": earliest.isoformat(),
            "earliest_date": earliest.isoformat(),
            "bottleneck": bottleneck,
            "margin_pct": _order_margin(db, so),
            "risk": risk,
            "details": {"lines_checked": len(so.lines or [])},
        }

    @staticmethod
    def generate_forecast(db: Session, factory_id: int) -> list:
        """Light moving-average forecast (3-month lookback)."""
        from app.models import DemandForecast
        from app.engines.demand_engine import DemandEngine
        return DemandEngine().forecast(db, factory_id)


def today_plus(d: date, days: int) -> date:
    return d + timedelta(days=days)


def _order_margin(db: Session, so: SalesOrder) -> float:
    if not so.lines or so.total_value == 0:
        return 0
    cost = 0
    rev = 0
    for l in so.lines:
        prod = ProductRepo(db).get(l.product_id)
        if not prod:
            continue
        cost += l.quantity * prod.standard_cost
        rev  += l.line_total
    return round(((rev - cost) / rev) * 100, 1) if rev else 0


class ProductionService:
    @staticmethod
    def daily_schedule(db: Session, factory_id: int, target_date: date) -> list:
        orders = db.scalars(select(ProductionOrder).where(
            ProductionOrder.factory_id == factory_id,
            ProductionOrder.planned_start <= target_date,
            ProductionOrder.planned_end >= target_date,
        )).all()
        lines = {l.id: l for l in ProductionLineRepo(db).list(factory_id=factory_id)}
        out = []
        for line_id, line in lines.items():
            blocks = [
                {
                    "order_id": o.id,
                    "order_number": o.order_number,
                    "product_id": o.product_id,
                    "planned": o.planned_qty,
                    "actual":  o.actual_qty,
                    "status":  o.status,
                }
                for o in orders if o.line_id == line_id
            ]
            capacity_hours = 8
            used_hours = sum(b["planned"] / max(1, line.capacity_per_hour) for b in blocks) if line.capacity_per_hour else 0
            util = (used_hours / capacity_hours) * 100 if capacity_hours else 0
            out.append({
                "line_id": line_id,
                "line_name": line.name,
                "line_code": line.code,
                "date": target_date.isoformat(),
                "blocks": blocks,
                "utilization_pct": round(min(150, util), 1),
            })
        return out

    @staticmethod
    def weekly_schedule(db: Session, factory_id: int, week_start: date) -> list:
        week = []
        for i in range(7):
            week.append(ProductionService.daily_schedule(db, factory_id, week_start + timedelta(days=i)))
        return week

    @staticmethod
    def capacity_analysis(db: Session, factory_id: int) -> list:
        lines = ProductionLineRepo(db).list(factory_id=factory_id)
        out = []
        for line in lines:
            cap = line.capacity_per_hour * 8  # 8h shift
            used = cap * 0.7  # default 70% used for demo
            util = (used / cap) * 100 if cap else 0
            status = "ok" if util < 85 else ("warning" if util < 95 else "overload")
            out.append({
                "line_id": line.id,
                "line_name": line.name,
                "line_code": line.code,
                "total_capacity_hours": cap,
                "used_hours": round(used, 1),
                "utilization_pct": round(util, 1),
                "status": status,
            })
        return out


class InventoryService:
    @staticmethod
    def raw_materials_view(db: Session, factory_id: int) -> list:
        materials = {m.id: m for m in RawMaterialRepo(db).list(factory_id=factory_id)}
        invs = db.scalars(select(InventoryRawMaterial).where(
            InventoryRawMaterial.factory_id == factory_id
        )).all()
        out = []
        for inv in invs:
            mat = materials.get(inv.material_id)
            if not mat:
                continue
            days_cov = _coverage_days(db, inv, mat)
            status = "ok"
            if days_cov < 3:           status = "critical"
            elif days_cov < 7:         status = "warning"
            elif inv.qty_on_hand < mat.safety_stock_qty: status = "warning"
            out.append({
                "id": inv.id,
                "material_id": inv.material_id,
                "material_code": mat.code,
                "material_name": mat.name,
                "warehouse_id": inv.warehouse_id,
                "qty_on_hand": inv.qty_on_hand,
                "qty_reserved": inv.qty_reserved,
                "qty_available": inv.qty_available,
                "safety_stock_qty": mat.safety_stock_qty,
                "reorder_point_qty": mat.reorder_point_qty,
                "days_coverage": round(days_cov, 1),
                "coverage_status": status,
                "last_updated": inv.last_updated.isoformat() if inv.last_updated else None,
            })
        return out

    @staticmethod
    def finished_goods_view(db: Session, factory_id: int) -> list:
        products = {p.id: p for p in ProductRepo(db).list(factory_id=factory_id)}
        invs = db.scalars(select(InventoryFinishedGoods).where(
            InventoryFinishedGoods.factory_id == factory_id
        )).all()
        out = []
        for inv in invs:
            prod = products.get(inv.product_id)
            if not prod:
                continue
            out.append({
                "id": inv.id,
                "product_id": inv.product_id,
                "product_sku": prod.sku,
                "product_name": prod.name,
                "qty_on_hand": inv.qty_on_hand,
                "qty_reserved": inv.qty_reserved,
                "qty_available": inv.qty_available,
                "warehouse_id": inv.warehouse_id,
                "expiry_date": inv.expiry_date.isoformat() if inv.expiry_date else None,
                "last_updated": inv.last_updated.isoformat(),
            })
        return out

    @staticmethod
    def wip_view(db: Session, factory_id: int) -> list:
        orders = db.scalars(select(ProductionOrder).where(
            ProductionOrder.factory_id == factory_id,
            ProductionOrder.status.in_(["planned", "in_progress"]),
        )).all()
        products = {p.id: p for p in ProductRepo(db).list(factory_id=factory_id)}
        out = []
        for o in orders:
            prod = products.get(o.product_id)
            if not prod:
                continue
            out.append({
                "id": o.id,
                "order_id": o.id,
                "order_number": o.order_number,
                "product_id": o.product_id,
                "product_sku": prod.sku,
                "product_name": prod.name,
                "line_id": o.line_id,
                "quantity": o.actual_qty or o.planned_qty,
                "stage": "in_progress" if o.status == "in_progress" else "planned",
                "status": o.status,
            })
        return out

    @staticmethod
    def critical_items(db: Session, factory_id: int) -> list:
        items = InventoryService.raw_materials_view(db, factory_id)
        return [i for i in items if i["coverage_status"] in ("critical", "warning")]

    @staticmethod
    def abc_xyz(db: Session, factory_id: int) -> dict:
        """ABC/XYZ classification based on value and consumption variance."""
        items = InventoryService.raw_materials_view(db, factory_id)
        materials = {m.id: m for m in RawMaterialRepo(db).list(factory_id=factory_id)}
        valued = []
        for it in items:
            mat = materials.get(it["material_id"])
            if not mat: continue
            valued.append({
                "id": it["material_id"],
                "code": it["material_code"],
                "name": it["material_name"],
                "value": it["qty_on_hand"] * mat.standard_cost,
                "variance": 0.3,  # demo placeholder
            })
        valued.sort(key=lambda x: -x["value"])
        n = len(valued) or 1
        for i, v in enumerate(valued):
            v["abc"] = "A" if i < n * 0.2 else ("B" if i < n * 0.5 else "C")
            v["xyz"] = "X" if v["variance"] < 0.2 else ("Y" if v["variance"] < 0.5 else "Z")
        cells: dict = {}
        for v in valued:
            k = f"{v['abc']}{v['xyz']}"
            cells.setdefault(k, {"cell": k, "count": 0, "total_value": 0.0, "items": []})
            cells[k]["count"] += 1
            cells[k]["total_value"] += v["value"]
            cells[k]["items"].append(v["id"])
        return {
            "matrix": list(cells.values()),
            "total_items": len(valued),
            "total_value": round(sum(v["value"] for v in valued), 2),
        }

    @staticmethod
    def coverage_report(db: Session, factory_id: int) -> dict:
        items = InventoryService.raw_materials_view(db, factory_id)
        return {
            "factory_id": factory_id,
            "total_items": len(items),
            "critical": sum(1 for i in items if i["coverage_status"] == "critical"),
            "warning":  sum(1 for i in items if i["coverage_status"] == "warning"),
            "ok":       sum(1 for i in items if i["coverage_status"] == "ok"),
            "items": items,
        }


def _coverage_days(db: Session, inv: InventoryRawMaterial, mat: RawMaterial) -> float:
    """Estimate how many days of stock remain based on recent consumption."""
    cutoff = date.today() - timedelta(days=30)
    used = db.execute(
        select(func.coalesce(func.sum(PurchaseOrderLine.qty_received), 0.0))
        .where(PurchaseOrderLine.material_id == mat.id)
    ).scalar() or 0.0
    daily = max(0.1, used / 30.0)
    return inv.qty_on_hand / daily

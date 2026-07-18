from datetime import timedelta

from sqlalchemy import select, func

from app.engines.base import BaseEngine
from app.engines.mrp_engine import MRPEngine
from app.models.inventory import RawMaterial
from app.models.procurement import PurchaseOrder, PurchaseOrderLine, Supplier


class ProcurementEngine(BaseEngine):
    name = "procurement_engine"

    def execute(self, db, factory_id: int):
        mrp = MRPEngine().execute(db, factory_id)
        reqs = mrp.data.get("requirements", [])
        # group by supplier
        by_supplier: dict[int, list] = {}
        for r in reqs:
            sid = r.get("supplier_id")
            if sid:
                by_supplier.setdefault(sid, []).append(r)
        created = 0
        pos = []
        today = __import__("datetime").datetime.utcnow()
        for sid, items in by_supplier.items():
            sup = db.get(Supplier, sid)
            total = 0.0
            po = PurchaseOrder(factory_id=factory_id, supplier_id=sid,
                               po_number=f"PO-AUTO-{today.strftime('%Y%m%d')}-{sid}",
                               order_date=today, expected_delivery=today + timedelta(days=7),
                               status="planned", currency="USD")
            db.add(po)
            db.flush()
            for r in items:
                rm = db.get(RawMaterial, r["material_id"])
                price = rm.standard_cost if rm else 0
                total += r["net_req"] * price
                db.add(PurchaseOrderLine(po_id=po.id, material_id=r["material_id"],
                                         qty_ordered=r["net_req"], unit_price=price,
                                         quality_status="pending"))
            po.total_value = round(total, 2)
            created += 1
            pos.append({"po_number": po.po_number, "supplier": sup.name if sup else "-",
                        "lines": len(items), "total": po.total_value})
        db.commit()
        return self._ok(f"Created {created} draft purchase orders", {"purchase_orders": pos})

from datetime import timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.engines.base import BaseEngine
from app.models.sales import SalesOrder, SalesOrderLine
from app.models.production import ProductionLine, ProductionOrder

COUNT_OPEN = func.count()


class ProductionEngine(BaseEngine):
    name = "production_engine"

    def execute(self, db: Session, factory_id: int):
        active_line = db.scalars(select(ProductionLine).where(
            ProductionLine.factory_id == factory_id, ProductionLine.is_deleted == False,
            ProductionLine.status == "active")).first()
        orders = db.scalars(select(SalesOrder).where(
            SalesOrder.factory_id == factory_id, SalesOrder.is_deleted == False,
            SalesOrder.status.in_(["confirmed", "in_production"]))).all()
        created = 0
        for so in orders:
            lines_for_so = db.scalars(select(SalesOrderLine).where(SalesOrderLine.order_id == so.id)).all()
            for l in lines_for_so:
                existing = db.scalar(
                    select(COUNT_OPEN).select_from(ProductionOrder).where(
                        ProductionOrder.sales_order_line_id == l.id)
                )
                if existing and existing > 0:
                    continue
                po = ProductionOrder(
                    factory_id=factory_id,
                    line_id=active_line.id if active_line else None,
                    product_id=l.product_id,
                    sales_order_line_id=l.id,
                    order_number=f"PRD-AUTO-{so.order_number}-{l.id}",
                    planned_qty=l.quantity, produced_qty=0, status="planned",
                    planned_start=so.required_delivery, priority=so.priority,
                )
                db.add(po)
                created += 1
        db.commit()
        return self._ok(f"Created {created} production orders", {"created": created})

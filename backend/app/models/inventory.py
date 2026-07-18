Input
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class RawMaterial(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "raw_materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    unit_of_measure: Mapped[str] = mapped_column(String(16), default="kg", nullable=False)
    standard_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    safety_stock_qty: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    reorder_point_qty: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shelf_life_days: Mapped[Optional[int]] = mapped_column(Integer)
    storage_conditions: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class InventoryRawMaterial(Base, TimestampMixin):
    __tablename__ = "inventory_raw_materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    material_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("raw_materials.id", ondelete="CASCADE"), nullable=False, index=True
    )
    warehouse_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("warehouses.id", ondelete="SET NULL")
    )
    qty_on_hand: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    qty_reserved: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    qty_available: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    batch_number: Mapped[Optional[str]] = mapped_column(String(64))
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    last_movement_date: Mapped[Optional[date]] = mapped_column(Date)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class InventoryFinishedGoods(Base, TimestampMixin):
    __tablename__ = "inventory_finished_goods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    warehouse_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("warehouses.id", ondelete="SET NULL")
    )
    qty_on_hand: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    qty_reserved: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    qty_available: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    batch_number: Mapped[Optional[str]] = mapped_column(String(64))
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class InventoryWIP(Base, TimestampMixin):
    __tablename__ = "inventory_wip"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    production_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("production_orders.id", ondelete="SET NULL")
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    line_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("production_lines.id", ondelete="SET NULL")
    )
    quantity: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    stage: Mapped[str] = mapped_column(String(64), default="assembly", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

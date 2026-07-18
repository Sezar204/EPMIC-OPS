import datetime as dt

from sqlalchemy import String, Integer, Float, Boolean, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RawMaterial(Base):
    __tablename__ = "raw_materials"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(150))
    category: Mapped[str | None] = mapped_column(String(80))
    unit_of_measure: Mapped[str] = mapped_column(String(20), default="kg")
    standard_cost: Mapped[float] = mapped_column(Float, default=0)
    safety_stock_qty: Mapped[float] = mapped_column(Float, default=0)
    reorder_point_qty: Mapped[float] = mapped_column(Float, default=0)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=0)
    shelf_life_days: Mapped[int | None] = mapped_column(Integer)
    storage_conditions: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)


class InventoryRawMaterial(Base):
    __tablename__ = "inventory_raw_materials"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("raw_materials.id", ondelete="CASCADE"), index=True)
    warehouse_id: Mapped[int | None] = mapped_column(ForeignKey("warehouses.id", ondelete="SET NULL"))
    qty_on_hand: Mapped[float] = mapped_column(Float, default=0)
    qty_reserved: Mapped[float] = mapped_column(Float, default=0)
    qty_available: Mapped[float] = mapped_column(Float, default=0)
    batch_number: Mapped[str | None] = mapped_column(String(60))
    expiry_date: Mapped[dt.date | None] = mapped_column(Date)
    last_movement: Mapped[dt.date | None] = mapped_column(Date)
    last_updated: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)


class InventoryFinishedGoods(Base):
    __tablename__ = "inventory_finished_goods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    warehouse_id: Mapped[int | None] = mapped_column(ForeignKey("warehouses.id", ondelete="SET NULL"))
    qty_on_hand: Mapped[float] = mapped_column(Float, default=0)
    qty_reserved: Mapped[float] = mapped_column(Float, default=0)
    qty_available: Mapped[float] = mapped_column(Float, default=0)
    batch_number: Mapped[str | None] = mapped_column(String(60))
    expiry_date: Mapped[dt.date | None] = mapped_column(Date)
    last_updated: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)


class InventoryWIP(Base):
    __tablename__ = "inventory_wip"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    production_order_id: Mapped[int | None] = mapped_column(ForeignKey("production_orders.id", ondelete="SET NULL"))
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"))
    line_id: Mapped[int | None] = mapped_column(ForeignKey("production_lines.id", ondelete="SET NULL"))
    qty_in_process: Mapped[float] = mapped_column(Float, default=0)
    stage: Mapped[str | None] = mapped_column(String(60))
    last_updated: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

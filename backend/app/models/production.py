import datetime as dt

from sqlalchemy import String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProductionLine(Base):
    __tablename__ = "production_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(String(150))
    type: Mapped[str] = mapped_column(String(20), default="discrete")
    capacity_per_hour: Mapped[float] = mapped_column(Float, default=0)
    capacity_unit: Mapped[str] = mapped_column(String(20), default="units")
    status: Mapped[str] = mapped_column(String(20), default="active")
    changeover_minutes: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    machines: Mapped[list["Machine"]] = relationship(back_populates="line")


class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    line_id: Mapped[int | None] = mapped_column(ForeignKey("production_lines.id", ondelete="SET NULL"), index=True)
    code: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(String(150))
    type: Mapped[str | None] = mapped_column(String(50))
    capacity: Mapped[float | None] = mapped_column(Float)
    capacity_unit: Mapped[str | None] = mapped_column(String(20))
    criticality: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="active")
    purchase_date: Mapped[dt.date | None] = mapped_column(DateTime)
    warranty_expiry: Mapped[dt.date | None] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    line: Mapped["ProductionLine | None"] = relationship(back_populates="machines")


class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    start_time: Mapped[str] = mapped_column(String(8), default="06:00")
    end_time: Mapped[str] = mapped_column(String(8), default="14:00")
    break_minutes: Mapped[int] = mapped_column(Integer, default=0)
    days_of_week: Mapped[str] = mapped_column(String(40), default="1,2,3,4,5")
    headcount: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    line_id: Mapped[int | None] = mapped_column(ForeignKey("production_lines.id", ondelete="SET NULL"), index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), index=True)
    sales_order_line_id: Mapped[int | None] = mapped_column(ForeignKey("sales_order_lines.id", ondelete="SET NULL"), index=True)
    order_number: Mapped[str] = mapped_column(String(40), index=True)
    planned_qty: Mapped[float] = mapped_column(Float, default=0)
    produced_qty: Mapped[float] = mapped_column(Float, default=0)
    scrap_qty: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="planned")
    planned_start: Mapped[dt.date | None] = mapped_column(DateTime)
    planned_end: Mapped[dt.date | None] = mapped_column(DateTime)
    actual_start: Mapped[dt.date | None] = mapped_column(DateTime)
    actual_end: Mapped[dt.date | None] = mapped_column(DateTime)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

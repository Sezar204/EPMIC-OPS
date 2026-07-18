Input
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Date, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class ProductionLine(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "production_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(16), default="discrete", nullable=False)
    capacity_per_hour: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    capacity_unit: Mapped[str] = mapped_column(String(16), default="pcs", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    changeover_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    machines: Mapped[List["Machine"]] = relationship(back_populates="line")


class Machine(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    line_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("production_lines.id", ondelete="SET NULL"), index=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(64))
    capacity: Mapped[Optional[float]] = mapped_column(Float)
    capacity_unit: Mapped[Optional[str]] = mapped_column(String(16))
    criticality: Mapped[str] = mapped_column(String(16), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    purchase_date: Mapped[Optional[date]] = mapped_column(Date)
    warranty_expiry: Mapped[Optional[date]] = mapped_column(Date)
    next_pm_date: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    line: Mapped[Optional["ProductionLine"]] = relationship(back_populates="machines")


class Shift(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_time: Mapped[str] = mapped_column(String(8), nullable=False)
    end_time: Mapped[str] = mapped_column(String(8), nullable=False)
    break_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    days_of_week: Mapped[str] = mapped_column(String(64), default="1,2,3,4,5", nullable=False)
    headcount: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ProductionOrder(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "production_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    sales_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_orders.id", ondelete="SET NULL")
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    line_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("production_lines.id", ondelete="SET NULL")
    )
    planned_qty: Mapped[float] = mapped_column(Float, nullable=False)
    actual_qty: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    planned_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    planned_end: Mapped[date] = mapped_column(Date, nullable=False)
    actual_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(16), default="planned", nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

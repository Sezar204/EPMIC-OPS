Input
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class MaintenanceSchedule(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "maintenance_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    machine_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(16), default="preventive", nullable=False)
    frequency_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    next_due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    last_done_date: Mapped[Optional[date]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text)
    estimated_hours: Mapped[float] = mapped_column(Float, default=2, nullable=False)
    is_active: Mapped[bool] = mapped_column(Integer, default=1, nullable=False)


class MaintenanceWorkOrder(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "maintenance_work_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    machine_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    wo_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(16), default="preventive", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="created", nullable=False)
    priority: Mapped[str] = mapped_column(String(16), default="medium", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(200))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    downtime_hours: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    root_cause: Mapped[Optional[str]] = mapped_column(Text)
    resolution: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class MachineBreakdown(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "machine_breakdowns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    machine_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    work_order_id: Mapped[Optional[int]] = mapped_column(Integer)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cause_category: Mapped[Optional[str]] = mapped_column(String(64))
    description: Mapped[Optional[str]] = mapped_column(Text)
    impact_on_production: Mapped[Optional[str]] = mapped_column(Text)

import datetime as dt

from sqlalchemy import String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(20), default="preventive")
    frequency_days: Mapped[int] = mapped_column(Integer, default=90)
    last_done: Mapped[dt.datetime | None] = mapped_column(DateTime)
    next_due: Mapped[dt.datetime | None] = mapped_column(DateTime, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class MaintenanceWorkOrder(Base):
    __tablename__ = "maintenance_work_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id", ondelete="CASCADE"), index=True)
    wo_number: Mapped[str] = mapped_column(String(40), index=True)
    type: Mapped[str] = mapped_column(String(20), default="preventive")
    status: Mapped[str] = mapped_column(String(20), default="created")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    description: Mapped[str | None] = mapped_column(Text)
    assigned_to: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[dt.datetime | None] = mapped_column(DateTime)
    downtime_hours: Mapped[float] = mapped_column(Float, default=0)
    root_cause: Mapped[str | None] = mapped_column(Text)
    resolution: Mapped[str | None] = mapped_column(Text)

    machine: Mapped["Machine"] = relationship("Machine")


class MachineBreakdown(Base):
    __tablename__ = "machine_breakdowns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id", ondelete="CASCADE"), index=True)
    occurred_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    resolved_at: Mapped[dt.datetime | None] = mapped_column(DateTime)
    cause_category: Mapped[str | None] = mapped_column(String(60))
    description: Mapped[str | None] = mapped_column(Text)
    impact_on_production: Mapped[str | None] = mapped_column(Text)
    work_order_id: Mapped[int | None] = mapped_column(ForeignKey("maintenance_work_orders.id", ondelete="SET NULL"))

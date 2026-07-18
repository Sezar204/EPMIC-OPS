Input
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Date, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class Worker(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    employee_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100))
    role: Mapped[Optional[str]] = mapped_column(String(100))
    skills: Mapped[Optional[list]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class ShiftAssignment(Base, TimestampMixin):
    __tablename__ = "shift_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    shift_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    assignment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    line_id: Mapped[Optional[int]] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class AttendanceRecord(Base, TimestampMixin):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    scheduled_hours: Mapped[float] = mapped_column(Float, default=8, nullable=False)
    actual_hours: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    ot_hours: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="present", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

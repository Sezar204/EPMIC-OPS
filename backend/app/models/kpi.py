Input
from datetime import date
from typing import Optional
from sqlalchemy import String, Integer, Float, Date, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class KPIDefinition(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "kpi_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    formula: Mapped[Optional[str]] = mapped_column(Text)
    unit: Mapped[Optional[str]] = mapped_column(String(16))
    target_value: Mapped[Optional[float]] = mapped_column(Float)
    warning_threshold: Mapped[Optional[float]] = mapped_column(Float)
    critical_threshold: Mapped[Optional[float]] = mapped_column(Float)
    higher_is_better: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    display_format: Mapped[str] = mapped_column(String(16), default="number", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class KPIValue(Base, TimestampMixin):
    __tablename__ = "kpi_values"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kpi_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    factory_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    period_type: Mapped[str] = mapped_column(String(16), default="daily", nullable=False)
    period_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="good", nullable=False)
    calculated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

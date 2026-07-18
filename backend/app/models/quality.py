Input
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class QualityCheck(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "quality_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    check_type: Mapped[str] = mapped_column(String(8), nullable=False)  # iqc | ipqc | oqc
    reference_id: Mapped[Optional[int]] = mapped_column(Integer)
    reference_type: Mapped[Optional[str]] = mapped_column(String(32))
    product_id: Mapped[Optional[int]] = mapped_column(Integer)
    material_id: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    sample_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defects_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defect_rate_pct: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    decision: Mapped[Optional[str]] = mapped_column(String(32))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class NonConformanceReport(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "non_conformance_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ncr_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(16), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="open", nullable=False)
    quality_check_id: Mapped[Optional[int]] = mapped_column(Integer)
    root_cause: Mapped[Optional[str]] = mapped_column(Text)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class CAPARecord(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "capa_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    capa_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(16), default="corrective", nullable=False)
    ncr_id: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    responsible_person: Mapped[Optional[str]] = mapped_column(String(200))
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(16), default="open", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

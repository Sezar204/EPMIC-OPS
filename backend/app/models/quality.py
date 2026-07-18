import datetime as dt

from sqlalchemy import String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class QualityCheck(Base):
    __tablename__ = "quality_checks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    check_type: Mapped[str] = mapped_column(String(20), default="ipqc")
    reference_id: Mapped[int | None] = mapped_column(Integer)
    reference_type: Mapped[str | None] = mapped_column(String(40))
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"))
    material_id: Mapped[int | None] = mapped_column(ForeignKey("raw_materials.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    checked_at: Mapped[dt.datetime | None] = mapped_column(DateTime)
    sample_size: Mapped[int] = mapped_column(Integer, default=0)
    defects_found: Mapped[int] = mapped_column(Integer, default=0)
    defect_rate_pct: Mapped[float] = mapped_column(Float, default=0)
    decision: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


class NonConformanceReport(Base):
    __tablename__ = "non_conformance_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    ncr_number: Mapped[str] = mapped_column(String(40), index=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default="minor")
    status: Mapped[str] = mapped_column(String(20), default="open")
    quality_check_id: Mapped[int | None] = mapped_column(ForeignKey("quality_checks.id", ondelete="SET NULL"))
    root_cause: Mapped[str | None] = mapped_column(Text)
    opened_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    closed_at: Mapped[dt.datetime | None] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


class CAPARecord(Base):
    __tablename__ = "capa_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    capa_number: Mapped[str] = mapped_column(String(40), index=True)
    type: Mapped[str] = mapped_column(String(20), default="corrective")
    ncr_id: Mapped[int | None] = mapped_column(ForeignKey("non_conformance_reports.id", ondelete="SET NULL"))
    description: Mapped[str] = mapped_column(Text)
    responsible_person: Mapped[str | None] = mapped_column(String(120))
    due_date: Mapped[dt.datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="open")
    closed_at: Mapped[dt.datetime | None] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

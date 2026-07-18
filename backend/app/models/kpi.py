import datetime as dt

from sqlalchemy import String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class KPIDefinition(Base):
    __tablename__ = "kpi_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int | None] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(60), index=True)
    name: Mapped[str] = mapped_column(String(150))
    category: Mapped[str] = mapped_column(String(40), default="production")
    formula: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str | None] = mapped_column(String(20))
    target_value: Mapped[float | None] = mapped_column(Float)
    warning_threshold: Mapped[float | None] = mapped_column(Float)
    critical_threshold: Mapped[float | None] = mapped_column(Float)
    higher_is_better: Mapped[bool] = mapped_column(Boolean, default=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)
    display_format: Mapped[str] = mapped_column(String(20), default="number")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


class KPIValue(Base):
    __tablename__ = "kpi_values"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    kpi_id: Mapped[int] = mapped_column(ForeignKey("kpi_definitions.id", ondelete="CASCADE"), index=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    period_type: Mapped[str] = mapped_column(String(20), default="daily")
    period_date: Mapped[dt.datetime] = mapped_column(DateTime, index=True)
    value: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="good")
    calculated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    kpi: Mapped["KPIDefinition"] = relationship("KPIDefinition")

Input
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class Factory(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "factories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)  # b2b | b2c | hybrid
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    working_start: Mapped[str] = mapped_column(String(8), default="08:00", nullable=False)
    working_end: Mapped[str] = mapped_column(String(8), default="17:00", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    calendars: Mapped[List["FactoryCalendar"]] = relationship(
        back_populates="factory", cascade="all, delete-orphan"
    )


class FactoryCalendar(Base, TimestampMixin):
    __tablename__ = "factory_calendars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    calendar_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_working_day: Mapped[bool] = mapped_column(default=True, nullable=False)
    holiday_name: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    factory: Mapped["Factory"] = relationship(back_populates="calendars")

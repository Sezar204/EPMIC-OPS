import datetime as dt

from sqlalchemy import String, Integer, Boolean, Text, ForeignKey, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Factory(Base):
    __tablename__ = "factories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    type: Mapped[str] = mapped_column(String(20), default="hybrid")
    status: Mapped[str] = mapped_column(String(20), default="active")
    location: Mapped[str | None] = mapped_column(String(150))
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    working_start: Mapped[str] = mapped_column(String(8), default="08:00")
    working_end: Mapped[str] = mapped_column(String(8), default="17:00")
    notes: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)


class FactoryCalendar(Base):
    __tablename__ = "factory_calendar"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    cal_date: Mapped[dt.date] = mapped_column(Date, index=True)
    is_working_day: Mapped[bool] = mapped_column(Boolean, default=True)
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=False)
    holiday_name: Mapped[str | None] = mapped_column(String(100))

import datetime as dt

from sqlalchemy import String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(150))
    type: Mapped[str] = mapped_column(String(20), default="general")
    total_capacity: Mapped[float] = mapped_column(Float, default=0)
    capacity_unit: Mapped[str] = mapped_column(String(20), default="sqm")
    storage_conditions: Mapped[str | None] = mapped_column(String(120))
    location: Mapped[str | None] = mapped_column(String(150))
    notes: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

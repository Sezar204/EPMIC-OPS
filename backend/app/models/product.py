import datetime as dt

from sqlalchemy import String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    sku: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(150))
    category: Mapped[str | None] = mapped_column(String(80))
    unit_of_measure: Mapped[str] = mapped_column(String(20), default="each")
    standard_cost: Mapped[float] = mapped_column(Float, default=0)
    selling_price: Mapped[float] = mapped_column(Float, default=0)
    min_order_qty: Mapped[int] = mapped_column(Integer, default=1)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=0)
    shelf_life_days: Mapped[int | None] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(20), default="finished")
    notes: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)


class BOMHeader(Base):
    __tablename__ = "bom_headers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    name: Mapped[str] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(20), default="active")
    yield_pct: Mapped[float] = mapped_column(Float, default=100)
    effective_date: Mapped[dt.date | None] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    lines: Mapped[list["BOMLine"]] = relationship(back_populates="bom", cascade="all, delete-orphan")


class BOMLine(Base):
    __tablename__ = "bom_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bom_id: Mapped[int] = mapped_column(ForeignKey("bom_headers.id", ondelete="CASCADE"), index=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("raw_materials.id", ondelete="CASCADE"), index=True)
    quantity_required: Mapped[float] = mapped_column(Float, default=0)
    unit: Mapped[str] = mapped_column(String(20), default="kg")
    loss_factor_pct: Mapped[float] = mapped_column(Float, default=0)
    is_alternative: Mapped[bool] = mapped_column(Boolean, default=False)
    alt_material_id: Mapped[int | None] = mapped_column(ForeignKey("raw_materials.id", ondelete="SET NULL"))
    sequence_no: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[str | None] = mapped_column(Text)

    bom: Mapped["BOMHeader"] = relationship(back_populates="lines")

Input
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Date, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class Product(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sku: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    unit_of_measure: Mapped[str] = mapped_column(String(16), default="pcs", nullable=False)
    standard_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    selling_price: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    min_order_qty: Mapped[float] = mapped_column(Float, default=1, nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shelf_life_days: Mapped[Optional[int]] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(16), default="finished", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    boms: Mapped[List["BOMHeader"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class BOMHeader(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "bom_headers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[str] = mapped_column(String(32), default="1.0", nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    yield_pct: Mapped[float] = mapped_column(Float, default=100, nullable=False)
    effective_date: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    product: Mapped["Product"] = relationship(back_populates="boms")
    lines: Mapped[List["BOMLine"]] = relationship(
        back_populates="bom", cascade="all, delete-orphan", order_by="BOMLine.sequence_no"
    )


class BOMLine(Base, TimestampMixin):
    __tablename__ = "bom_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bom_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bom_headers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    material_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("raw_materials.id", ondelete="RESTRICT"), nullable=False
    )
    quantity_required: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(16), default="kg", nullable=False)
    loss_factor_pct: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    is_alternative: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    alt_material_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("raw_materials.id", ondelete="SET NULL")
    )
    sequence_no: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    bom: Mapped["BOMHeader"] = relationship(back_populates="lines")

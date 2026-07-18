Input
from datetime import date
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Date, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class Supplier(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_name: Mapped[Optional[str]] = mapped_column(String(200))
    contact_email: Mapped[Optional[str]] = mapped_column(String(200))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(64))
    payment_terms_days: Mapped[Optional[int]] = mapped_column(Integer)
    rating: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    materials: Mapped[List["SupplierMaterial"]] = relationship(
        back_populates="supplier", cascade="all, delete-orphan"
    )


class SupplierMaterial(Base, TimestampMixin):
    __tablename__ = "supplier_materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    material_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("raw_materials.id", ondelete="CASCADE"), nullable=False, index=True
    )
    supplier_price: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    min_order_qty: Mapped[float] = mapped_column(Float, default=1, nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    supplier: Mapped["Supplier"] = relationship(back_populates="materials")


class PurchaseOrder(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    po_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_delivery: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    actual_delivery: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(16), default="planned", nullable=False)
    total_value: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    lines: Mapped[List["PurchaseOrderLine"]] = relationship(
        back_populates="po", cascade="all, delete-orphan"
    )


class PurchaseOrderLine(Base, TimestampMixin):
    __tablename__ = "purchase_order_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    po_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    material_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("raw_materials.id", ondelete="RESTRICT"), nullable=False
    )
    qty_ordered: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    qty_received: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    quality_status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    po: Mapped["PurchaseOrder"] = relationship(back_populates="lines")

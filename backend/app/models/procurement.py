import datetime as dt

from sqlalchemy import String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(150))
    contact_name: Mapped[str | None] = mapped_column(String(120))
    contact_email: Mapped[str | None] = mapped_column(String(120))
    contact_phone: Mapped[str | None] = mapped_column(String(60))
    payment_terms_days: Mapped[int | None] = mapped_column(Integer)
    rating: Mapped[float] = mapped_column(Float, default=3)
    status: Mapped[str] = mapped_column(String(20), default="active")
    notes: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)


class SupplierMaterial(Base):
    __tablename__ = "supplier_materials"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), index=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("raw_materials.id", ondelete="CASCADE"), index=True)
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=0)
    unit_price: Mapped[float] = mapped_column(Float, default=0)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id", ondelete="CASCADE"), index=True)
    po_number: Mapped[str] = mapped_column(String(40), index=True)
    order_date: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    expected_delivery: Mapped[dt.datetime] = mapped_column(DateTime)
    actual_delivery: Mapped[dt.datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="planned")
    total_value: Mapped[float] = mapped_column(Float, default=0)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    notes: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    lines: Mapped[list["PurchaseOrderLine"]] = relationship(back_populates="po", cascade="all, delete-orphan")


class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    po_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), index=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("raw_materials.id", ondelete="CASCADE"), index=True)
    qty_ordered: Mapped[float] = mapped_column(Float, default=0)
    unit_price: Mapped[float] = mapped_column(Float, default=0)
    qty_received: Mapped[float] = mapped_column(Float, default=0)
    quality_status: Mapped[str] = mapped_column(String(20), default="pending")
    notes: Mapped[str | None] = mapped_column(Text)

    po: Mapped["PurchaseOrder"] = relationship(back_populates="lines")

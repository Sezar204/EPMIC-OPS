import datetime as dt

from sqlalchemy import String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(150))
    type: Mapped[str] = mapped_column(String(20), default="b2b")
    priority: Mapped[int] = mapped_column(Integer, default=3)
    credit_limit: Mapped[float | None] = mapped_column(Float)
    payment_terms_days: Mapped[int | None] = mapped_column(Integer)
    contact_name: Mapped[str | None] = mapped_column(String(120))
    contact_email: Mapped[str | None] = mapped_column(String(120))
    contact_phone: Mapped[str | None] = mapped_column(String(60))
    notes: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    order_number: Mapped[str] = mapped_column(String(40), index=True)
    order_date: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    required_delivery: Mapped[dt.datetime] = mapped_column(DateTime)
    confirmed_delivery: Mapped[dt.datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    total_value: Mapped[float] = mapped_column(Float, default=0)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    is_rush_order: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    notes: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    lines: Mapped[list["SalesOrderLine"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class SalesOrderLine(Base):
    __tablename__ = "sales_order_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    quantity: Mapped[float] = mapped_column(Float, default=0)
    unit_price: Mapped[float] = mapped_column(Float, default=0)
    discount_pct: Mapped[float] = mapped_column(Float, default=0)
    line_total: Mapped[float] = mapped_column(Float, default=0)
    required_date: Mapped[dt.datetime | None] = mapped_column(DateTime)
    committed_date: Mapped[dt.datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="open")
    fulfilled_qty: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str | None] = mapped_column(Text)

    order: Mapped["SalesOrder"] = relationship(back_populates="lines")


class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    period_type: Mapped[str] = mapped_column(String(20), default="monthly")
    period_label: Mapped[str] = mapped_column(String(20), index=True)
    historical: Mapped[float] = mapped_column(Float, default=0)
    system_forecast: Mapped[float] = mapped_column(Float, default=0)
    manual_forecast: Mapped[float | None] = mapped_column(Float)
    final_forecast: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

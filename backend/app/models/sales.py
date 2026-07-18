Input
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Date, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class Customer(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(16), default="b2b", nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    credit_limit: Mapped[Optional[float]] = mapped_column(Float)
    payment_terms_days: Mapped[Optional[int]] = mapped_column(Integer)
    contact_name: Mapped[Optional[str]] = mapped_column(String(200))
    contact_email: Mapped[Optional[str]] = mapped_column(String(200))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(64))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class SalesOrder(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sales_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    order_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    required_delivery: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    confirmed_delivery: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(16), default="draft", nullable=False)
    total_value: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    is_rush_order: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    ctp_result: Mapped[Optional[dict]] = mapped_column(JSON)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    lines: Mapped[List["SalesOrderLine"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class SalesOrderLine(Base, TimestampMixin):
    __tablename__ = "sales_order_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    discount_pct: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    line_total: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    required_date: Mapped[Optional[date]] = mapped_column(Date)
    committed_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(16), default="open", nullable=False)
    fulfilled_qty: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    order: Mapped["SalesOrder"] = relationship(back_populates="lines")


class DemandForecast(Base, TimestampMixin):
    __tablename__ = "demand_forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_type: Mapped[str] = mapped_column(String(16), default="monthly", nullable=False)
    forecast_type: Mapped[str] = mapped_column(String(16), default="b2c", nullable=False)  # b2b | b2c
    historical_qty: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    system_forecast_qty: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    manual_adjusted_qty: Mapped[Optional[float]] = mapped_column(Float)
    final_qty: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

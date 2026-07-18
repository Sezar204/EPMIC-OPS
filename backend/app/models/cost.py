Input
from datetime import date
from typing import Optional
from sqlalchemy import String, Integer, Float, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, SoftDeleteMixin


class ProductCost(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "product_costs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    period_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    std_material_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    act_material_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    std_labor_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    act_labor_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    std_overhead_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    act_overhead_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    std_total_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    act_total_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    revenue: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

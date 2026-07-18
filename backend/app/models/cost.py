import datetime as dt

from sqlalchemy import String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProductCost(Base):
    __tablename__ = "product_costs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    period_label: Mapped[str] = mapped_column(String(20), index=True)
    std_material_cost: Mapped[float] = mapped_column(Float, default=0)
    act_material_cost: Mapped[float] = mapped_column(Float, default=0)
    std_labor_cost: Mapped[float] = mapped_column(Float, default=0)
    act_labor_cost: Mapped[float] = mapped_column(Float, default=0)
    std_overhead_cost: Mapped[float] = mapped_column(Float, default=0)
    act_overhead_cost: Mapped[float] = mapped_column(Float, default=0)
    std_total: Mapped[float] = mapped_column(Float, default=0)
    act_total: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

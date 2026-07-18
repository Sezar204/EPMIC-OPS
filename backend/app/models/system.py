import datetime as dt

from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BackupLog(Base):
    __tablename__ = "backup_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(200), index=True)
    backup_type: Mapped[str] = mapped_column(String(20), default="manual")
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    file_path: Mapped[str] = mapped_column(String(400))
    status: Mapped[str] = mapped_column(String(20), default="success")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


class AppSetting(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    value: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(String(200))

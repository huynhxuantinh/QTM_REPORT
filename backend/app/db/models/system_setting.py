from __future__ import annotations

from sqlalchemy import Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    cpu_warning_percent: Mapped[float] = mapped_column(Float, default=70.0)
    cpu_critical_percent: Mapped[float] = mapped_column(Float, default=90.0)
    ram_warning_percent: Mapped[float] = mapped_column(Float, default=75.0)
    ram_critical_percent: Mapped[float] = mapped_column(Float, default=90.0)
    packet_loss_warning_percent: Mapped[float] = mapped_column(Float, default=10.0)
    packet_loss_critical_percent: Mapped[float] = mapped_column(Float, default=30.0)
    latency_warning_ms: Mapped[float] = mapped_column(Float, default=50.0)
    latency_critical_ms: Mapped[float] = mapped_column(Float, default=150.0)
    scheduler_interval_minutes: Mapped[int] = mapped_column(Integer, default=15)
    scheduler_cooldown_seconds: Mapped[int] = mapped_column(Integer, default=5)
    max_concurrent_checks: Mapped[int] = mapped_column(Integer, default=3)

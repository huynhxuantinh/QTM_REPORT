from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.health_check import HealthCheck


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ScanRun(Base):
    __tablename__ = "scan_runs"
    __table_args__ = (
        Index("ix_scan_runs_started_at", "started_at"),
        Index(
            "uq_scan_runs_single_running",
            "execution_status",
            unique=True,
            postgresql_where=text("execution_status = 'running'"),
            sqlite_where=text("execution_status = 'running'"),
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    trigger: Mapped[str] = mapped_column(String(20), nullable=False)
    execution_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="running"
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    total_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_checks: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    failed_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    checks: Mapped[list[HealthCheck]] = relationship(
        back_populates="scan_run",
        lazy="selectin",
    )

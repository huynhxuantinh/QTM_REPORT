from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HealthCheck(Base):
    __tablename__ = "health_checks"
    __table_args__ = (
        Index("ix_health_checks_device_started", "device_id", "started_at"),
        Index("ix_health_checks_overall_status", "overall_status"),
        Index(
            "uq_health_checks_running_device",
            "device_id",
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
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False
    )
    execution_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="running"
    )
    overall_status: Mapped[str | None] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ssh_ok: Mapped[bool | None] = mapped_column(Boolean)
    uptime_seconds: Mapped[int | None] = mapped_column(BigInteger)
    cpu_percent: Mapped[float | None] = mapped_column(Float)
    ram_percent: Mapped[float | None] = mapped_column(Float)
    memory_total_bytes: Mapped[int | None] = mapped_column(BigInteger)
    memory_used_bytes: Mapped[int | None] = mapped_column(BigInteger)
    memory_free_bytes: Mapped[int | None] = mapped_column(BigInteger)
    error: Mapped[str | None] = mapped_column(Text)

    interfaces: Mapped[list[InterfaceResult]] = relationship(
        back_populates="health_check",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    pings: Mapped[list[PingResult]] = relationship(
        back_populates="health_check",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    findings: Mapped[list[HealthFindingResult]] = relationship(
        back_populates="health_check",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class InterfaceResult(Base):
    __tablename__ = "interface_results"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    health_check_id: Mapped[int] = mapped_column(
        ForeignKey("health_checks.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    protocol: Mapped[str] = mapped_column(String(30), nullable=False)
    input_errors: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    crc_errors: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    output_errors: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    output_drops: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    health_check: Mapped[HealthCheck] = relationship(back_populates="interfaces")


class PingResult(Base):
    __tablename__ = "ping_results"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    health_check_id: Mapped[int] = mapped_column(
        ForeignKey("health_checks.id", ondelete="CASCADE"), nullable=False
    )
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    packet_loss_percent: Mapped[float] = mapped_column(Float, nullable=False)
    latency_min_ms: Mapped[float | None] = mapped_column(Float)
    latency_avg_ms: Mapped[float | None] = mapped_column(Float)
    latency_max_ms: Mapped[float | None] = mapped_column(Float)

    health_check: Mapped[HealthCheck] = relationship(back_populates="pings")


class HealthFindingResult(Base):
    __tablename__ = "health_findings"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    health_check_id: Mapped[int] = mapped_column(
        ForeignKey("health_checks.id", ondelete="CASCADE"), nullable=False
    )
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    metric: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    health_check: Mapped[HealthCheck] = relationship(back_populates="findings")

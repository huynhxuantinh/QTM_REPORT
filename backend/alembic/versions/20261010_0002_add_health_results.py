"""Add persisted health check results.

Revision ID: 20261010_0002
Revises: 20261010_0001
Create Date: 2026-10-10
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261010_0002"
down_revision: str | None = "20261010_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "health_checks",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.BigInteger(), nullable=False),
        sa.Column("execution_status", sa.String(length=20), nullable=False),
        sa.Column("overall_status", sa.String(length=20), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ssh_ok", sa.Boolean(), nullable=True),
        sa.Column("uptime_seconds", sa.BigInteger(), nullable=True),
        sa.Column("cpu_percent", sa.Float(), nullable=True),
        sa.Column("ram_percent", sa.Float(), nullable=True),
        sa.Column("memory_total_bytes", sa.BigInteger(), nullable=True),
        sa.Column("memory_used_bytes", sa.BigInteger(), nullable=True),
        sa.Column("memory_free_bytes", sa.BigInteger(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_health_checks_device_started",
        "health_checks",
        ["device_id", "started_at"],
    )
    op.create_index(
        "ix_health_checks_overall_status",
        "health_checks",
        ["overall_status"],
    )
    dialect = op.get_bind().dialect.name
    where_options: dict[str, sa.ClauseElement] = {}
    if dialect == "postgresql":
        where_options["postgresql_where"] = sa.text(
            "execution_status = 'running'"
        )
    elif dialect == "sqlite":
        where_options["sqlite_where"] = sa.text(
            "execution_status = 'running'"
        )
    op.create_index(
        "uq_health_checks_running_device",
        "health_checks",
        ["device_id"],
        unique=True,
        **where_options,
    )

    op.create_table(
        "interface_results",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("health_check_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("protocol", sa.String(length=30), nullable=False),
        sa.Column("input_errors", sa.BigInteger(), nullable=False),
        sa.Column("crc_errors", sa.BigInteger(), nullable=False),
        sa.Column("output_errors", sa.BigInteger(), nullable=False),
        sa.Column("output_drops", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["health_check_id"], ["health_checks.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_interface_results_health_check_id",
        "interface_results",
        ["health_check_id"],
    )

    op.create_table(
        "ping_results",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("health_check_id", sa.BigInteger(), nullable=False),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("target", sa.String(length=255), nullable=False),
        sa.Column("packet_loss_percent", sa.Float(), nullable=False),
        sa.Column("latency_min_ms", sa.Float(), nullable=True),
        sa.Column("latency_avg_ms", sa.Float(), nullable=True),
        sa.Column("latency_max_ms", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["health_check_id"], ["health_checks.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_ping_results_health_check_id", "ping_results", ["health_check_id"]
    )

    op.create_table(
        "health_findings",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("health_check_id", sa.BigInteger(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("metric", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["health_check_id"], ["health_checks.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_health_findings_health_check_id",
        "health_findings",
        ["health_check_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_health_findings_health_check_id", table_name="health_findings")
    op.drop_table("health_findings")
    op.drop_index("ix_ping_results_health_check_id", table_name="ping_results")
    op.drop_table("ping_results")
    op.drop_index(
        "ix_interface_results_health_check_id", table_name="interface_results"
    )
    op.drop_table("interface_results")
    op.drop_index("uq_health_checks_running_device", table_name="health_checks")
    op.drop_index("ix_health_checks_overall_status", table_name="health_checks")
    op.drop_index("ix_health_checks_device_started", table_name="health_checks")
    op.drop_table("health_checks")

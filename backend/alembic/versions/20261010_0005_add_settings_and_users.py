"""Add configurable thresholds and admin users.

Revision ID: 20261010_0005
Revises: 20261010_0004
Create Date: 2026-10-10
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261010_0005"
down_revision: str | None = "20261010_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cpu_warning_percent", sa.Float(), nullable=False),
        sa.Column("cpu_critical_percent", sa.Float(), nullable=False),
        sa.Column("ram_warning_percent", sa.Float(), nullable=False),
        sa.Column("ram_critical_percent", sa.Float(), nullable=False),
        sa.Column("packet_loss_warning_percent", sa.Float(), nullable=False),
        sa.Column("packet_loss_critical_percent", sa.Float(), nullable=False),
        sa.Column("latency_warning_ms", sa.Float(), nullable=False),
        sa.Column("latency_critical_ms", sa.Float(), nullable=False),
        sa.Column("scheduler_interval_minutes", sa.Integer(), nullable=False),
        sa.Column("max_concurrent_checks", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("system_settings")

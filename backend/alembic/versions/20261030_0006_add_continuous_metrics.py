"""Add continuous scan configuration and interface traffic metrics.

Revision ID: 20261030_0006
Revises: 20261010_0005
Create Date: 2026-10-30
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261030_0006"
down_revision: str | None = "20261010_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "system_settings",
        sa.Column(
            "scheduler_cooldown_seconds",
            sa.Integer(),
            nullable=False,
            server_default="5",
        ),
    )
    for name in (
        "input_packets",
        "output_packets",
        "input_bytes",
        "output_bytes",
    ):
        op.add_column(
            "interface_results",
            sa.Column(
                name,
                sa.BigInteger(),
                nullable=False,
                server_default="0",
            ),
        )
    for name in (
        "input_packets_per_second",
        "output_packets_per_second",
        "input_bytes_per_second",
        "output_bytes_per_second",
    ):
        op.add_column(
            "interface_results",
            sa.Column(name, sa.Float(), nullable=True),
        )


def downgrade() -> None:
    for name in (
        "output_bytes_per_second",
        "input_bytes_per_second",
        "output_packets_per_second",
        "input_packets_per_second",
        "output_bytes",
        "input_bytes",
        "output_packets",
        "input_packets",
    ):
        op.drop_column("interface_results", name)
    op.drop_column("system_settings", "scheduler_cooldown_seconds")

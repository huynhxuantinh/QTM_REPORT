"""Add path ping target to managed devices.

Revision ID: 20261010_0003
Revises: 20261010_0002
Create Date: 2026-10-10
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261010_0003"
down_revision: str | None = "20261010_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "devices",
        sa.Column("path_ping_target", sa.String(length=45), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("devices", "path_ping_target")

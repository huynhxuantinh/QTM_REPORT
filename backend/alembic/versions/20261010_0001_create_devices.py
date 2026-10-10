"""Create managed devices table.

Revision ID: 20261010_0001
Revises:
Create Date: 2026-10-10
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261010_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("host", sa.String(length=45), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("device_type", sa.String(length=50), nullable=False),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("encrypted_password", sa.Text(), nullable=False),
        sa.Column("encrypted_secret", sa.Text(), nullable=True),
        sa.Column("site", sa.String(length=120), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_devices_site", "devices", ["site"], unique=False)
    op.create_index(
        "ix_devices_site_deleted",
        "devices",
        ["site", "deleted_at"],
        unique=False,
    )

    dialect = op.get_bind().dialect.name
    where_options: dict[str, sa.ClauseElement] = {}
    if dialect == "postgresql":
        where_options["postgresql_where"] = sa.text("deleted_at IS NULL")
    elif dialect == "sqlite":
        where_options["sqlite_where"] = sa.text("deleted_at IS NULL")
    op.create_index(
        "uq_devices_active_host_port",
        "devices",
        ["host", "port"],
        unique=True,
        **where_options,
    )


def downgrade() -> None:
    op.drop_index("uq_devices_active_host_port", table_name="devices")
    op.drop_index("ix_devices_site_deleted", table_name="devices")
    op.drop_index("ix_devices_site", table_name="devices")
    op.drop_table("devices")

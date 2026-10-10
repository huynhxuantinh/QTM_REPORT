"""Add scan runs for manual and scheduled checks.

Revision ID: 20261010_0004
Revises: 20261010_0003
Create Date: 2026-10-10
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261010_0004"
down_revision: str | None = "20261010_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "scan_runs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("trigger", sa.String(length=20), nullable=False),
        sa.Column("execution_status", sa.String(length=20), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_checks", sa.Integer(), nullable=False),
        sa.Column("completed_checks", sa.Integer(), nullable=False),
        sa.Column("failed_checks", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scan_runs_started_at", "scan_runs", ["started_at"])
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
        "uq_scan_runs_single_running",
        "scan_runs",
        ["execution_status"],
        unique=True,
        **where_options,
    )
    with op.batch_alter_table("health_checks") as batch_op:
        batch_op.add_column(sa.Column("scan_run_id", sa.BigInteger()))
        batch_op.create_foreign_key(
            "fk_health_checks_scan_run_id",
            "scan_runs",
            ["scan_run_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(
            "ix_health_checks_scan_run_id", ["scan_run_id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("health_checks") as batch_op:
        batch_op.drop_index("ix_health_checks_scan_run_id")
        batch_op.drop_constraint(
            "fk_health_checks_scan_run_id", type_="foreignkey"
        )
        batch_op.drop_column("scan_run_id")
    op.drop_index("uq_scan_runs_single_running", table_name="scan_runs")
    op.drop_index("ix_scan_runs_started_at", table_name="scan_runs")
    op.drop_table("scan_runs")

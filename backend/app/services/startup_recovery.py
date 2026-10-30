from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.health_check import HealthCheck
from app.db.models.scan_run import ScanRun


INTERRUPTED_CHECK_ERROR = "Backend restarted during health check"


def recover_interrupted_work(session: Session) -> tuple[int, int]:
    """Release database locks left by a backend crash or restart."""
    recovered_at = datetime.now(timezone.utc)
    checks = list(
        session.scalars(
            select(HealthCheck).where(
                HealthCheck.execution_status == "running"
            )
        )
    )
    for check in checks:
        check.execution_status = "failed"
        check.finished_at = recovered_at
        check.checked_at = recovered_at
        check.error = INTERRUPTED_CHECK_ERROR

    scans = list(
        session.scalars(
            select(ScanRun).where(ScanRun.execution_status == "running")
        )
    )
    for scan in scans:
        scan.execution_status = "failed"
        scan.finished_at = recovered_at
        scan.completed_checks = sum(
            check.execution_status in {"succeeded", "failed"}
            for check in scan.checks
        )
        scan.failed_checks = sum(
            check.execution_status == "failed" for check in scan.checks
        )

    session.commit()
    return len(scans), len(checks)

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session, sessionmaker

from app.db.models.device import Device
from app.services.scan_runs import ScanRunService


def test_failing_scan_closes_running_children_and_releases_device_locks(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        session.add_all(
            [
                Device(
                    name="R1",
                    host="192.168.141.11",
                    username="admin",
                    encrypted_password="encrypted",
                ),
                Device(
                    name="R2",
                    host="192.168.141.12",
                    username="admin",
                    encrypted_password="encrypted",
                ),
            ]
        )
        session.commit()
        service = ScanRunService(session)
        scan = service.start("scheduled")
        scan.checks[0].execution_status = "succeeded"
        scan.checks[0].finished_at = datetime.now(timezone.utc)
        session.commit()

        failed = service.fail(scan.id)

        assert failed.execution_status == "failed"
        assert failed.finished_at is not None
        assert failed.completed_checks == 2
        assert failed.failed_checks == 1
        assert [check.execution_status for check in failed.checks] == [
            "succeeded",
            "failed",
        ]
        assert failed.checks[1].finished_at is not None
        assert failed.checks[1].error == "Scan runner stopped before completion"

        next_scan = service.start("scheduled")
        assert next_scan.execution_status == "running"
        assert len(next_scan.checks) == 2


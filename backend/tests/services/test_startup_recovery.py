from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.db.models.device import Device
from app.db.models.health_check import HealthCheck
from app.main import create_app
from app.services.scan_runs import ScanRunService


def test_startup_recovers_interrupted_scan_and_standalone_check(
    session_factory: sessionmaker[Session],
    settings,
) -> None:
    with session_factory() as session:
        first = Device(
            name="R1",
            host="192.168.141.11",
            username="admin",
            encrypted_password="encrypted",
        )
        second = Device(
            name="R2",
            host="192.168.141.12",
            username="admin",
            encrypted_password="encrypted",
        )
        session.add_all([first, second])
        session.commit()
        first.is_active = True
        second.is_active = False
        session.commit()

        interrupted_scan = ScanRunService(session).start("scheduled")
        interrupted_check_id = interrupted_scan.checks[0].id
        standalone = HealthCheck(
            device_id=second.id,
            execution_status="running",
        )
        session.add(standalone)
        session.commit()
        standalone_check_id = standalone.id
        interrupted_scan_id = interrupted_scan.id

    application = create_app(
        settings.model_copy(
            update={"scheduler_enabled": False, "auth_enabled": False}
        ),
        session_factory=session_factory,
    )
    with TestClient(application):
        pass

    with session_factory() as session:
        recovered_scan = ScanRunService(session).get(interrupted_scan_id)
        assert recovered_scan.execution_status == "failed"
        assert recovered_scan.finished_at is not None
        assert recovered_scan.completed_checks == 1
        assert recovered_scan.failed_checks == 1

        recovered_child = session.get(HealthCheck, interrupted_check_id)
        recovered_standalone = session.get(HealthCheck, standalone_check_id)
        for recovered in (recovered_child, recovered_standalone):
            assert recovered is not None
            assert recovered.execution_status == "failed"
            assert recovered.finished_at is not None
            assert recovered.checked_at is not None
            assert recovered.error == "Backend restarted during health check"

        next_scan = ScanRunService(session).start("scheduled")
        assert next_scan.execution_status == "running"


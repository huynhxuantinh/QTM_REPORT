from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.models.device import Device
from app.db.models.health_check import (
    HealthCheck,
    HealthFindingResult,
    InterfaceResult,
    PingResult,
)
from app.db.models.scan_run import ScanRun
from app.services.retention import HistoryRetentionService, run_retention_loop


def test_retention_prunes_only_completed_history_older_than_cutoff(
    session_factory: sessionmaker[Session],
) -> None:
    now = datetime.now(timezone.utc)
    old = now - timedelta(days=31)
    recent = now - timedelta(days=2)
    with session_factory() as session:
        device = Device(
            name="R1",
            host="192.168.141.11",
            username="admin",
            encrypted_password="encrypted",
        )
        session.add(device)
        session.commit()
        old_scan = ScanRun(
            trigger="scheduled",
            execution_status="succeeded",
            started_at=old,
            finished_at=old,
            total_checks=1,
            completed_checks=1,
        )
        old_check = HealthCheck(
            device_id=device.id,
            execution_status="succeeded",
            started_at=old,
            finished_at=old,
            checked_at=old,
        )
        old_check.interfaces = [
            InterfaceResult(
                name="FastEthernet0/0",
                ip_address="192.168.141.11",
                status="up",
                protocol="up",
            )
        ]
        old_check.pings = [
            PingResult(
                source_type="backend",
                target="192.168.141.11",
                packet_loss_percent=0,
            )
        ]
        old_check.findings = [
            HealthFindingResult(
                severity="Warning",
                metric="cpu",
                message="old",
            )
        ]
        old_scan.checks = [old_check]
        recent_check = HealthCheck(
            device_id=device.id,
            execution_status="succeeded",
            started_at=recent,
            finished_at=recent,
            checked_at=recent,
        )
        running_check = HealthCheck(
            device_id=device.id,
            execution_status="running",
            started_at=old,
        )
        session.add_all([old_scan, recent_check, running_check])
        session.commit()

        result = HistoryRetentionService(session).prune(
            retention_days=30,
            now=now,
        )

        assert result.deleted_checks == 1
        assert result.deleted_scans == 1
        assert session.scalar(select(func.count()).select_from(HealthCheck)) == 2
        assert session.scalar(select(func.count()).select_from(InterfaceResult)) == 0
        assert session.scalar(select(func.count()).select_from(PingResult)) == 0
        assert session.scalar(select(func.count()).select_from(HealthFindingResult)) == 0
        assert session.get(HealthCheck, running_check.id) is not None


def test_daily_retention_loop_survives_one_cleanup_failure() -> None:
    from threading import Event

    stopped = Event()
    attempts = 0
    waits: list[float] = []

    def cleanup_once() -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("database unavailable")
        stopped.set()

    def wait(seconds: float) -> bool:
        waits.append(seconds)
        return stopped.is_set()

    run_retention_loop(
        stopped=stopped,
        cleanup_once=cleanup_once,
        wait=wait,
    )

    assert attempts == 2
    assert waits == [86_400.0, 86_400.0]


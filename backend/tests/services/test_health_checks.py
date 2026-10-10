from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import CredentialCipher
from app.db.models.device import Device
from app.domain.models import (
    HealthFinding,
    InterfaceMetrics,
    MemoryMetrics,
    NetworkHealthReport,
    PingMetrics,
)
from app.services.health_checks import (
    CheckAlreadyRunningError,
    HealthCheckService,
)


class FakeCollector:
    def collect(self, config) -> NetworkHealthReport:
        assert config.password == "qtm"
        assert config.path_ping_target == "192.168.141.128"
        return sample_report()


class FailingCollector:
    def collect(self, config) -> NetworkHealthReport:
        raise RuntimeError("collector crashed")


def sample_report() -> NetworkHealthReport:
    return NetworkHealthReport(
        device_name="R1",
        host="192.168.141.11",
        checked_at=datetime(2026, 10, 10, tzinfo=timezone.utc),
        status="Warning",
        ssh_ok=True,
        uptime_seconds=3600,
        cpu_percent=37.0,
        memory=MemoryMetrics(
            total_bytes=1_000_000,
            used_bytes=650_000,
            free_bytes=350_000,
            utilization_percent=65.0,
        ),
        interfaces=[
            InterfaceMetrics(
                name="FastEthernet0/0",
                ip_address="192.168.141.11",
                status="up",
                protocol="up",
                input_errors=1,
                crc_errors=2,
                output_errors=3,
                output_drops=4,
            )
        ],
        management_ping=PingMetrics(0.0, 1.0, 1.5, 2.0),
        path_ping=PingMetrics(0.0, 2.0, 2.5, 3.0),
        findings=[HealthFinding("Warning", "cpu", "CPU is elevated")],
    )


def create_device(session: Session, cipher: CredentialCipher) -> Device:
    device = Device(
        name="R1",
        host="192.168.141.11",
        port=22,
        device_type="cisco_ios",
        username="admin",
        encrypted_password=cipher.encrypt("qtm"),
        encrypted_secret=None,
        site="GNS3",
        is_active=True,
    )
    device.path_ping_target = "192.168.141.128"
    session.add(device)
    session.commit()
    session.refresh(device)
    return device


def test_execute_persists_complete_health_report(
    session_factory: sessionmaker[Session], settings
) -> None:
    with session_factory() as session:
        cipher = CredentialCipher(settings.credential_key)
        device = create_device(session, cipher)
        service = HealthCheckService(session, cipher, FakeCollector())

        check = service.start(device.id)
        completed = service.execute(check.id)

        assert completed.execution_status == "succeeded"
        assert completed.overall_status == "Warning"
        assert completed.cpu_percent == 37.0
        assert completed.ram_percent == 65.0
        assert completed.memory_total_bytes == 1_000_000
        assert completed.interfaces[0].name == "FastEthernet0/0"
        assert completed.interfaces[0].crc_errors == 2
        assert completed.pings[0].source_type == "backend"
        assert completed.pings[0].packet_loss_percent == 0.0
        assert completed.pings[0].latency_avg_ms == 1.5
        assert completed.pings[1].source_type == "device"
        assert completed.pings[1].target == "192.168.141.128"
        assert completed.pings[1].latency_avg_ms == 2.5
        assert completed.findings[0].severity == "Warning"
        assert completed.finished_at is not None


def test_prevents_two_running_checks_for_same_device(
    session_factory: sessionmaker[Session], settings
) -> None:
    with session_factory() as session:
        cipher = CredentialCipher(settings.credential_key)
        device = create_device(session, cipher)
        service = HealthCheckService(session, cipher, FakeCollector())

        service.start(device.id)

        with pytest.raises(CheckAlreadyRunningError):
            service.start(device.id)


def test_unexpected_collector_error_marks_execution_failed(
    session_factory: sessionmaker[Session], settings
) -> None:
    with session_factory() as session:
        cipher = CredentialCipher(settings.credential_key)
        device = create_device(session, cipher)
        service = HealthCheckService(session, cipher, FailingCollector())
        check = service.start(device.id)

        failed = service.execute(check.id)

        assert failed.execution_status == "failed"
        assert failed.overall_status is None
        assert failed.error == "RuntimeError: collector crashed"
        assert failed.finished_at is not None

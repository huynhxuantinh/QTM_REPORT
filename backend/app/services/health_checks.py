from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol

from sqlalchemy.orm import Session

from app.core.security import CredentialCipher
from app.db.models.health_check import (
    HealthCheck,
    HealthFindingResult,
    InterfaceResult,
    PingResult,
)
from app.domain.models import DeviceConfig, NetworkHealthReport
from app.repositories.devices import DeviceRepository
from app.repositories.health_checks import HealthCheckRepository
from app.services.devices import DeviceNotFoundError
from app.repositories.settings import SystemSettingRepository
from app.services.settings import thresholds_from_setting


class Collector(Protocol):
    def collect(self, config: DeviceConfig) -> NetworkHealthReport: ...


class CheckNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("Health check not found")


class CheckAlreadyRunningError(Exception):
    def __init__(self) -> None:
        super().__init__("A health check is already running for this device")


class DeviceInactiveError(Exception):
    def __init__(self) -> None:
        super().__init__("Device is inactive")


class HealthCheckService:
    def __init__(
        self,
        session: Session,
        cipher: CredentialCipher,
        collector: Collector,
    ) -> None:
        self._devices = DeviceRepository(session)
        self._checks = HealthCheckRepository(session)
        self._cipher = cipher
        self._collector = collector
        self._settings = SystemSettingRepository(session)

    def start(self, device_id: int) -> HealthCheck:
        device = self._devices.get(device_id)
        if device is None:
            raise DeviceNotFoundError
        if not device.is_active:
            raise DeviceInactiveError
        if self._checks.find_running(device_id) is not None:
            raise CheckAlreadyRunningError
        return self._checks.create(
            HealthCheck(device_id=device_id, execution_status="running")
        )

    def execute(self, check_id: int) -> HealthCheck:
        health_check = self._checks.get(check_id)
        if health_check is None:
            raise CheckNotFoundError
        if health_check.execution_status != "running":
            return health_check

        try:
            device = self._devices.get(health_check.device_id)
            if device is None:
                raise DeviceNotFoundError
            config = self._device_config(device)
            report = self._collector.collect(config)
            previous = self._checks.latest_succeeded(
                device.id,
                before_check_id=health_check.id,
            )
            self._apply_report(health_check, report, config, previous)
            return self._checks.save(health_check)
        except Exception as error:
            self._checks.rollback()
            failed = self._checks.get(check_id)
            if failed is None:
                raise CheckNotFoundError from error
            failed.execution_status = "failed"
            failed.finished_at = datetime.now(timezone.utc)
            failed.error = f"{type(error).__name__}: {error}"
            return self._checks.save(failed)

    def test_connection(self, device_id: int) -> dict[str, object]:
        device = self._devices.get(device_id)
        if device is None:
            raise DeviceNotFoundError
        report = self._collector.collect(self._device_config(device))
        return {
            "device_id": device_id,
            "reachable": report.ssh_ok,
            "message": (
                "SSH connection successful"
                if report.ssh_ok
                else report.error or "SSH connection failed"
            ),
        }

    def _device_config(self, device) -> DeviceConfig:
        setting = self._settings.get_or_create()
        return DeviceConfig(
            name=device.name,
            host=device.host,
            port=device.port,
            device_type=device.device_type,
            username=device.username,
            password=self._cipher.decrypt(device.encrypted_password),
            secret=(
                self._cipher.decrypt(device.encrypted_secret)
                if device.encrypted_secret
                else None
            ),
            path_ping_target=device.path_ping_target,
            thresholds=thresholds_from_setting(setting),
        )

    def get(self, check_id: int) -> HealthCheck:
        health_check = self._checks.get(check_id)
        if health_check is None:
            raise CheckNotFoundError
        return health_check

    def history(
        self,
        device_id: int,
        *,
        offset: int,
        limit: int,
    ) -> tuple[list[HealthCheck], int]:
        if self._devices.get(device_id) is None:
            raise DeviceNotFoundError
        return self._checks.list_for_device(
            device_id, offset=offset, limit=limit
        )

    @staticmethod
    def _apply_report(
        health_check: HealthCheck,
        report: NetworkHealthReport,
        config: DeviceConfig,
        previous: HealthCheck | None,
    ) -> None:
        health_check.execution_status = "succeeded"
        health_check.overall_status = report.status
        health_check.checked_at = report.checked_at
        health_check.finished_at = datetime.now(timezone.utc)
        health_check.ssh_ok = report.ssh_ok
        health_check.uptime_seconds = report.uptime_seconds
        health_check.cpu_percent = report.cpu_percent
        health_check.error = report.error

        if report.memory is not None:
            health_check.ram_percent = report.memory.utilization_percent
            health_check.memory_total_bytes = report.memory.total_bytes
            health_check.memory_used_bytes = report.memory.used_bytes
            health_check.memory_free_bytes = report.memory.free_bytes

        previous_interfaces = {
            item.name: item for item in previous.interfaces
        } if previous is not None else {}
        elapsed_seconds = (
            (report.checked_at - previous.checked_at).total_seconds()
            if previous is not None and previous.checked_at is not None
            else None
        )
        health_check.interfaces = []
        for item in report.interfaces:
            old = previous_interfaces.get(item.name)
            health_check.interfaces.append(
                InterfaceResult(
                    name=item.name,
                    ip_address=item.ip_address,
                    status=item.status,
                    protocol=item.protocol,
                    input_packets=item.input_packets,
                    output_packets=item.output_packets,
                    input_bytes=item.input_bytes,
                    output_bytes=item.output_bytes,
                    input_packets_per_second=HealthCheckService._counter_rate(
                        item.input_packets,
                        old.input_packets if old is not None else None,
                        elapsed_seconds,
                    ),
                    output_packets_per_second=HealthCheckService._counter_rate(
                        item.output_packets,
                        old.output_packets if old is not None else None,
                        elapsed_seconds,
                    ),
                    input_bytes_per_second=HealthCheckService._counter_rate(
                        item.input_bytes,
                        old.input_bytes if old is not None else None,
                        elapsed_seconds,
                    ),
                    output_bytes_per_second=HealthCheckService._counter_rate(
                        item.output_bytes,
                        old.output_bytes if old is not None else None,
                        elapsed_seconds,
                    ),
                    input_errors=item.input_errors,
                    crc_errors=item.crc_errors,
                    output_errors=item.output_errors,
                    output_drops=item.output_drops,
                )
            )

        pings: list[PingResult] = []
        if report.management_ping is not None:
            pings.append(
                HealthCheckService._ping_result(
                    "backend", config.host, report.management_ping
                )
            )
        if report.path_ping is not None and config.path_ping_target is not None:
            pings.append(
                HealthCheckService._ping_result(
                    "device", config.path_ping_target, report.path_ping
                )
            )
        health_check.pings = pings
        health_check.findings = [
            HealthFindingResult(
                severity=item.severity,
                metric=item.metric,
                message=item.message,
            )
            for item in report.findings
        ]

    @staticmethod
    def _counter_rate(
        current: int,
        previous: int | None,
        elapsed_seconds: float | None,
    ) -> float | None:
        if (
            previous is None
            or elapsed_seconds is None
            or elapsed_seconds <= 0
            or current < previous
        ):
            return None
        return (current - previous) / elapsed_seconds

    @staticmethod
    def _ping_result(source_type: str, target: str, metrics) -> PingResult:
        return PingResult(
            source_type=source_type,
            target=target,
            packet_loss_percent=metrics.packet_loss_percent,
            latency_min_ms=metrics.latency_min_ms,
            latency_avg_ms=metrics.latency_avg_ms,
            latency_max_ms=metrics.latency_max_ms,
        )

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Literal

HealthStatus = Literal["Healthy", "Warning", "Critical"]


@dataclass(frozen=True, slots=True)
class HealthThresholds:
    cpu_warning_percent: float = 70.0
    cpu_critical_percent: float = 90.0
    ram_warning_percent: float = 75.0
    ram_critical_percent: float = 90.0
    packet_loss_warning_percent: float = 10.0
    packet_loss_critical_percent: float = 30.0
    latency_warning_ms: float = 50.0
    latency_critical_ms: float = 150.0


@dataclass(frozen=True, slots=True)
class DeviceConfig:
    name: str
    host: str
    username: str
    password: str
    port: int = 22
    device_type: str = "cisco_ios"
    secret: str | None = None
    monitored_interfaces: tuple[str, ...] = ()
    path_ping_target: str | None = None
    thresholds: HealthThresholds = field(default_factory=HealthThresholds)


@dataclass(frozen=True, slots=True)
class MemoryMetrics:
    total_bytes: int
    used_bytes: int
    free_bytes: int
    utilization_percent: float


@dataclass(frozen=True, slots=True)
class InterfaceMetrics:
    name: str
    ip_address: str
    status: str
    protocol: str
    input_packets: int = 0
    output_packets: int = 0
    input_bytes: int = 0
    output_bytes: int = 0
    input_errors: int = 0
    crc_errors: int = 0
    output_errors: int = 0
    output_drops: int = 0


@dataclass(frozen=True, slots=True)
class InterfaceCounters:
    input_packets: int = 0
    output_packets: int = 0
    input_bytes: int = 0
    output_bytes: int = 0
    input_errors: int = 0
    crc_errors: int = 0
    output_errors: int = 0
    output_drops: int = 0


@dataclass(frozen=True, slots=True)
class PingMetrics:
    packet_loss_percent: float
    latency_min_ms: float | None
    latency_avg_ms: float | None
    latency_max_ms: float | None


@dataclass(frozen=True, slots=True)
class HealthFinding:
    severity: HealthStatus
    metric: str
    message: str


@dataclass(frozen=True, slots=True)
class HealthEvaluation:
    status: HealthStatus
    findings: list[HealthFinding] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class NetworkHealthReport:
    device_name: str
    host: str
    checked_at: datetime
    status: HealthStatus
    ssh_ok: bool
    uptime_seconds: int | None
    cpu_percent: float | None
    memory: MemoryMetrics | None
    interfaces: list[InterfaceMetrics]
    management_ping: PingMetrics | None
    path_ping: PingMetrics | None
    findings: list[HealthFinding]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["checked_at"] = self.checked_at.isoformat()
        return payload


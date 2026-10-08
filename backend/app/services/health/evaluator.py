from __future__ import annotations

from collections.abc import Callable, Iterable

from app.domain.models import (
    HealthEvaluation,
    HealthFinding,
    HealthStatus,
    InterfaceMetrics,
    PingMetrics,
)


def evaluate_health(
    *,
    ssh_ok: bool,
    cpu_percent: float | None,
    ram_percent: float | None,
    management_ping: PingMetrics | None,
    path_ping: PingMetrics | None,
    interfaces: list[InterfaceMetrics],
) -> HealthEvaluation:
    findings: list[HealthFinding] = []

    def add(severity: HealthStatus, metric: str, message: str) -> None:
        findings.append(HealthFinding(severity, metric, message))

    if not ssh_ok:
        add("Critical", "ssh", "SSH connection failed")

    _evaluate_percentage(
        value=cpu_percent,
        metric="CPU",
        warning_at=70.0,
        critical_at=90.0,
        add=add,
    )
    _evaluate_percentage(
        value=ram_percent,
        metric="RAM",
        warning_at=75.0,
        critical_at=90.0,
        add=add,
    )

    if management_ping is None:
        add("Warning", "management_ping", "Management ping data is unavailable")
    elif management_ping.packet_loss_percent > 0:
        add(
            "Warning",
            "management_ping",
            f"Management packet loss is {management_ping.packet_loss_percent:g}%",
        )

    if path_ping is None:
        add("Warning", "path_ping", "Path ping data is unavailable")
    else:
        if path_ping.packet_loss_percent >= 30:
            add(
                "Critical",
                "packet_loss",
                f"Path packet loss is {path_ping.packet_loss_percent:g}%",
            )
        elif path_ping.packet_loss_percent > 0:
            add(
                "Warning",
                "packet_loss",
                f"Path packet loss is {path_ping.packet_loss_percent:g}%",
            )

        latency = path_ping.latency_avg_ms
        if latency is None:
            add("Warning", "latency", "Path latency data is unavailable")
        elif latency > 150:
            add("Critical", "latency", f"Average latency is {latency:g} ms")
        elif latency >= 50:
            add("Warning", "latency", f"Average latency is {latency:g} ms")

    for interface in interfaces:
        if interface.status != "up" or interface.protocol != "up":
            add(
                "Critical",
                "interface",
                f"{interface.name} is {interface.status}/{interface.protocol}",
            )
        elif any(
            (
                interface.input_errors,
                interface.crc_errors,
                interface.output_errors,
                interface.output_drops,
            )
        ):
            add(
                "Warning",
                "interface_errors",
                f"{interface.name} has non-zero error counters",
            )

    status = _worst_status(finding.severity for finding in findings)
    return HealthEvaluation(status=status, findings=findings)


def _evaluate_percentage(
    *,
    value: float | None,
    metric: str,
    warning_at: float,
    critical_at: float,
    add: Callable[[HealthStatus, str, str], None],
) -> None:
    if value is None:
        add("Warning", metric.lower(), f"{metric} data is unavailable")
    elif value >= critical_at:
        add("Critical", metric.lower(), f"{metric} usage is {value:g}%")
    elif value >= warning_at:
        add("Warning", metric.lower(), f"{metric} usage is {value:g}%")


def _worst_status(statuses: Iterable[HealthStatus]) -> HealthStatus:
    rank: dict[HealthStatus, int] = {
        "Healthy": 0,
        "Warning": 1,
        "Critical": 2,
    }
    worst: HealthStatus = "Healthy"
    for status in statuses:
        if rank[status] > rank[worst]:
            worst = status
    return worst


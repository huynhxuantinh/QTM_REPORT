from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping

from app.domain.models import (
    HealthEvaluation,
    HealthFinding,
    HealthStatus,
    HealthThresholds,
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
    path_ping_required: bool = True,
    thresholds: HealthThresholds | Mapping[str, float] | None = None,
) -> HealthEvaluation:
    findings: list[HealthFinding] = []
    configured = thresholds or HealthThresholds()

    def threshold(name: str) -> float:
        if isinstance(configured, Mapping):
            return float(
                configured.get(name, getattr(HealthThresholds(), name))
            )
        return float(getattr(configured, name))

    def add(severity: HealthStatus, metric: str, message: str) -> None:
        findings.append(HealthFinding(severity, metric, message))

    if not ssh_ok:
        add("Critical", "ssh", "SSH connection failed")

    _evaluate_percentage(
        value=cpu_percent,
        metric="CPU",
        warning_at=threshold("cpu_warning_percent"),
        critical_at=threshold("cpu_critical_percent"),
        add=add,
    )
    _evaluate_percentage(
        value=ram_percent,
        metric="RAM",
        warning_at=threshold("ram_warning_percent"),
        critical_at=threshold("ram_critical_percent"),
        add=add,
    )

    if management_ping is None:
        add("Warning", "management_ping", "Management ping data is unavailable")
    else:
        _evaluate_packet_loss(
            ping=management_ping,
            metric="management_ping",
            label="Management",
            warning_at=threshold("packet_loss_warning_percent"),
            critical_at=threshold("packet_loss_critical_percent"),
            add=add,
        )

    if path_ping is None:
        if path_ping_required:
            add("Warning", "path_ping", "Path ping data is unavailable")
    else:
        _evaluate_packet_loss(
            ping=path_ping,
            metric="packet_loss",
            label="Path",
            warning_at=threshold("packet_loss_warning_percent"),
            critical_at=threshold("packet_loss_critical_percent"),
            add=add,
        )

        latency = path_ping.latency_avg_ms
        if latency is None:
            add("Warning", "latency", "Path latency data is unavailable")
        elif latency >= threshold("latency_critical_ms"):
            add("Critical", "latency", f"Average latency is {latency:g} ms")
        elif latency >= threshold("latency_warning_ms"):
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


def _evaluate_packet_loss(
    *,
    ping: PingMetrics,
    metric: str,
    label: str,
    warning_at: float,
    critical_at: float,
    add: Callable[[HealthStatus, str, str], None],
) -> None:
    loss = ping.packet_loss_percent
    if loss >= critical_at:
        add("Critical", metric, f"{label} packet loss is {loss:g}%")
    elif loss >= warning_at:
        add("Warning", metric, f"{label} packet loss is {loss:g}%")


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


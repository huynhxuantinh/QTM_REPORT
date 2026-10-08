from __future__ import annotations

import re

from app.domain.models import (
    InterfaceCounters,
    InterfaceMetrics,
    MemoryMetrics,
    PingMetrics,
)


def parse_cpu_percent(output: str) -> float | None:
    match = re.search(r"five minutes:\s*(\d+(?:\.\d+)?)%", output)
    return float(match.group(1)) if match else None


def parse_memory(output: str) -> MemoryMetrics | None:
    match = re.search(
        r"^Processor\s+\S+\s+(\d+)\s+(\d+)\s+(\d+)",
        output,
        re.MULTILINE,
    )
    if not match:
        return None

    total, used, free = (int(value) for value in match.groups())
    denominator = used + free
    utilization = (used / denominator * 100) if denominator else 0.0
    return MemoryMetrics(
        total_bytes=total,
        used_bytes=used,
        free_bytes=free,
        utilization_percent=utilization,
    )


def parse_uptime_seconds(output: str) -> int | None:
    match = re.search(r"uptime is\s+(.+)", output, re.IGNORECASE)
    if not match:
        return None

    unit_seconds = {
        "year": 365 * 24 * 60 * 60,
        "week": 7 * 24 * 60 * 60,
        "day": 24 * 60 * 60,
        "hour": 60 * 60,
        "minute": 60,
        "second": 1,
    }
    total = 0
    for value, unit in re.findall(
        r"(\d+)\s+(year|week|day|hour|minute|second)s?",
        match.group(1),
        re.IGNORECASE,
    ):
        total += int(value) * unit_seconds[unit.lower()]
    return total or None


def parse_interfaces(output: str) -> list[InterfaceMetrics]:
    interfaces: list[InterfaceMetrics] = []
    pattern = re.compile(
        r"^(\S+)\s+(\S+)\s+\S+\s+\S+\s+(.+?)\s+(up|down)$",
        re.IGNORECASE,
    )
    for line in output.splitlines():
        match = pattern.match(line.strip())
        if not match or match.group(1).lower() == "interface":
            continue
        name, ip_address, status, protocol = match.groups()
        interfaces.append(
            InterfaceMetrics(
                name=name,
                ip_address=ip_address,
                status=status.lower(),
                protocol=protocol.lower(),
            )
        )
    return interfaces


def parse_interface_counters(output: str) -> InterfaceCounters:
    def counter(pattern: str) -> int:
        match = re.search(pattern, output, re.IGNORECASE)
        return int(match.group(1)) if match else 0

    return InterfaceCounters(
        input_errors=counter(r"(\d+)\s+input errors"),
        crc_errors=counter(r"(\d+)\s+CRC"),
        output_errors=counter(r"(\d+)\s+output errors"),
        output_drops=counter(r"Total output drops:\s*(\d+)"),
    )


def parse_ping(output: str) -> PingMetrics | None:
    success_match = re.search(
        r"Success rate is\s+(\d+(?:\.\d+)?)\s+percent",
        output,
        re.IGNORECASE,
    )
    if not success_match:
        return None

    success_percent = float(success_match.group(1))
    latency_match = re.search(
        r"min/avg/max\s*=\s*([\d.]+)/([\d.]+)/([\d.]+)\s*ms",
        output,
        re.IGNORECASE,
    )
    latencies = (
        tuple(float(value) for value in latency_match.groups())
        if latency_match
        else (None, None, None)
    )
    return PingMetrics(
        packet_loss_percent=100.0 - success_percent,
        latency_min_ms=latencies[0],
        latency_avg_ms=latencies[1],
        latency_max_ms=latencies[2],
    )


def parse_linux_ping(output: str) -> PingMetrics | None:
    loss_match = re.search(r"([\d.]+)%\s+packet loss", output)
    if not loss_match:
        return None

    latency_match = re.search(
        r"(?:rtt|round-trip) min/avg/max/(?:mdev|stddev)\s*=\s*"
        r"([\d.]+)/([\d.]+)/([\d.]+)/[\d.]+\s*ms",
        output,
    )
    latencies = (
        tuple(float(value) for value in latency_match.groups())
        if latency_match
        else (None, None, None)
    )
    return PingMetrics(
        packet_loss_percent=float(loss_match.group(1)),
        latency_min_ms=latencies[0],
        latency_avg_ms=latencies[1],
        latency_max_ms=latencies[2],
    )


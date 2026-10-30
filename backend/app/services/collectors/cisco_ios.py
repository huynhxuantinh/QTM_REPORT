from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any, Protocol

from app.domain.models import (
    DeviceConfig,
    HealthFinding,
    InterfaceMetrics,
    NetworkHealthReport,
    PingMetrics,
)
from app.services.health.evaluator import evaluate_health
from app.services.parsers.cisco_ios import (
    parse_cpu_percent,
    parse_interface_counters,
    parse_interfaces,
    parse_linux_ping,
    parse_memory,
    parse_ping,
    parse_uptime_seconds,
)


class Connection(Protocol):
    def send_command(self, command: str, **kwargs: Any) -> str: ...

    def disconnect(self) -> None: ...


Connector = Callable[..., Connection]
ManagementPing = Callable[[str, int, int], PingMetrics | None]


def netmiko_connector(**kwargs: Any) -> Connection:
    from netmiko import ConnectHandler

    return ConnectHandler(**kwargs)


def run_management_ping(
    host: str,
    count: int = 5,
    timeout_seconds: int = 2,
) -> PingMetrics | None:
    command = [
        "ping",
        "-c",
        str(count),
        "-W",
        str(timeout_seconds),
        host,
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=count * (timeout_seconds + 1) + 2,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return parse_linux_ping(f"{completed.stdout}\n{completed.stderr}")


class CiscoIosCollector:
    def __init__(
        self,
        *,
        connector: Connector = netmiko_connector,
        management_ping: ManagementPing = run_management_ping,
    ) -> None:
        self._connector = connector
        self._management_ping = management_ping

    def collect(self, config: DeviceConfig) -> NetworkHealthReport:
        checked_at = datetime.now(timezone.utc)
        management_ping = self._management_ping(config.host, 5, 2)
        connection: Connection | None = None

        try:
            connection = self._connector(
                device_type=config.device_type,
                host=config.host,
                port=config.port,
                username=config.username,
                password=config.password,
                secret=config.secret or config.password,
                conn_timeout=10,
                auth_timeout=10,
                banner_timeout=15,
                timeout=20,
                fast_cli=False,
            )
            uptime = parse_uptime_seconds(
                connection.send_command("show version | include uptime")
            )
            cpu = parse_cpu_percent(
                connection.send_command(
                    "show processes cpu | include CPU utilization"
                )
            )
            memory = parse_memory(
                connection.send_command(
                    "show memory statistics | include Processor"
                )
            )
            parsed_interfaces = parse_interfaces(
                connection.send_command("show ip interface brief")
            )
            interfaces = self._select_interfaces(
                parsed_interfaces,
                config.monitored_interfaces,
            )
            interfaces = [
                self._add_counters(connection, interface)
                for interface in interfaces
            ]
            path_ping = self._collect_path_ping(
                connection,
                config.path_ping_target,
            )
            evaluation = evaluate_health(
                ssh_ok=True,
                cpu_percent=cpu,
                ram_percent=(memory.utilization_percent if memory else None),
                management_ping=management_ping,
                path_ping=path_ping,
                interfaces=interfaces,
                path_ping_required=config.path_ping_target is not None,
                thresholds=config.thresholds,
            )
            return NetworkHealthReport(
                device_name=config.name,
                host=config.host,
                checked_at=checked_at,
                status=evaluation.status,
                ssh_ok=True,
                uptime_seconds=uptime,
                cpu_percent=cpu,
                memory=memory,
                interfaces=interfaces,
                management_ping=management_ping,
                path_ping=path_ping,
                findings=evaluation.findings,
            )
        except Exception as exc:
            return NetworkHealthReport(
                device_name=config.name,
                host=config.host,
                checked_at=checked_at,
                status="Critical",
                ssh_ok=False,
                uptime_seconds=None,
                cpu_percent=None,
                memory=None,
                interfaces=[],
                management_ping=management_ping,
                path_ping=None,
                findings=[
                    HealthFinding(
                        "Critical",
                        "collector",
                        f"Collection failed: {type(exc).__name__}",
                    )
                ],
                error=str(exc),
            )
        finally:
            if connection is not None:
                connection.disconnect()

    @staticmethod
    def _select_interfaces(
        interfaces: list[InterfaceMetrics],
        monitored: tuple[str, ...],
    ) -> list[InterfaceMetrics]:
        if monitored:
            wanted = set(monitored)
            return [item for item in interfaces if item.name in wanted]
        return [item for item in interfaces if item.ip_address != "unassigned"]

    @staticmethod
    def _add_counters(
        connection: Connection,
        interface: InterfaceMetrics,
    ) -> InterfaceMetrics:
        counters = parse_interface_counters(
            connection.send_command(f"show interfaces {interface.name}")
        )
        return replace(
            interface,
            input_packets=counters.input_packets,
            output_packets=counters.output_packets,
            input_bytes=counters.input_bytes,
            output_bytes=counters.output_bytes,
            input_errors=counters.input_errors,
            crc_errors=counters.crc_errors,
            output_errors=counters.output_errors,
            output_drops=counters.output_drops,
        )

    @staticmethod
    def _collect_path_ping(
        connection: Connection,
        target: str | None,
    ) -> PingMetrics | None:
        if target is None:
            return None
        output = connection.send_command(
            f"ping {target} repeat 10 timeout 1",
            read_timeout=20,
        )
        return parse_ping(output)


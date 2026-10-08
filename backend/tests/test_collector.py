from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.models import DeviceConfig, PingMetrics  # noqa: E402
from app.services.collectors.cisco_ios import CiscoIosCollector  # noqa: E402


FIXTURES = Path(__file__).parent / "fixtures" / "cisco_ios"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class FakeConnection:
    def __init__(self) -> None:
        self.disconnected = False
        self.commands: list[str] = []

    def send_command(self, command: str, **_: Any) -> str:
        self.commands.append(command)
        outputs = {
            "show version | include uptime": fixture("show_version_uptime.txt"),
            "show processes cpu | include CPU utilization": fixture(
                "show_processes_cpu.txt"
            ),
            "show memory statistics | include Processor": fixture(
                "show_memory_statistics.txt"
            ),
            "show ip interface brief": fixture("show_ip_interface_brief.txt"),
            "show interfaces FastEthernet0/0": fixture(
                "show_interface_fa00.txt"
            ),
            "ping 192.168.141.128 repeat 10 timeout 1": fixture(
                "ping_success.txt"
            ),
        }
        return outputs[command]

    def disconnect(self) -> None:
        self.disconnected = True


class CiscoIosCollectorTests(unittest.TestCase):
    def test_collects_and_normalizes_live_metrics(self) -> None:
        connection = FakeConnection()
        config = DeviceConfig(
            name="R1",
            host="192.168.141.11",
            username="admin",
            password="qtm",
            monitored_interfaces=("FastEthernet0/0",),
            path_ping_target="192.168.141.128",
        )
        management_ping = PingMetrics(
            packet_loss_percent=0.0,
            latency_min_ms=2.0,
            latency_avg_ms=7.0,
            latency_max_ms=14.0,
        )
        collector = CiscoIosCollector(
            connector=lambda **_: connection,
            management_ping=lambda *_: management_ping,
        )

        report = collector.collect(config)

        self.assertEqual(report.status, "Healthy")
        self.assertTrue(report.ssh_ok)
        self.assertEqual(report.cpu_percent, 4.0)
        self.assertAlmostEqual(
            report.memory.utilization_percent if report.memory else 0.0,
            21.0952,
            places=3,
        )
        self.assertEqual(len(report.interfaces), 1)
        self.assertEqual(report.path_ping.packet_loss_percent, 0.0)
        self.assertTrue(connection.disconnected)

    def test_disconnects_when_command_collection_fails(self) -> None:
        connection = FakeConnection()

        def fail(_: str, **__: Any) -> str:
            raise TimeoutError("command timeout")

        connection.send_command = fail  # type: ignore[method-assign]
        collector = CiscoIosCollector(
            connector=lambda **_: connection,
            management_ping=lambda *_: None,
        )

        report = collector.collect(
            DeviceConfig(
                name="R1",
                host="192.168.141.11",
                username="admin",
                password="qtm",
            )
        )

        self.assertEqual(report.status, "Critical")
        self.assertFalse(report.ssh_ok)
        self.assertTrue(connection.disconnected)


if __name__ == "__main__":
    unittest.main()

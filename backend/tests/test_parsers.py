from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.parsers.cisco_ios import (  # noqa: E402
    parse_cpu_percent,
    parse_interface_counters,
    parse_interfaces,
    parse_linux_ping,
    parse_memory,
    parse_ping,
    parse_uptime_seconds,
)


FIXTURES = Path(__file__).parent / "fixtures" / "cisco_ios"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class CiscoIosParserTests(unittest.TestCase):
    def test_parses_five_minute_cpu(self) -> None:
        self.assertEqual(
            parse_cpu_percent(fixture("show_processes_cpu.txt")),
            4.0,
        )

    def test_returns_none_when_cpu_output_is_unknown(self) -> None:
        self.assertIsNone(parse_cpu_percent("unexpected output"))

    def test_parses_processor_memory_pool(self) -> None:
        memory = parse_memory(fixture("show_memory_statistics.txt"))

        self.assertIsNotNone(memory)
        assert memory is not None
        self.assertEqual(memory.total_bytes, 98_890_848)
        self.assertEqual(memory.used_bytes, 20_861_236)
        self.assertEqual(memory.free_bytes, 78_029_612)
        self.assertAlmostEqual(memory.utilization_percent, 21.0952, places=3)

    def test_parses_uptime_to_seconds(self) -> None:
        self.assertEqual(
            parse_uptime_seconds(fixture("show_version_uptime.txt")),
            4_080,
        )

    def test_parses_interface_status_including_administratively_down(self) -> None:
        interfaces = parse_interfaces(fixture("show_ip_interface_brief.txt"))

        self.assertEqual(len(interfaces), 4)
        self.assertEqual(interfaces[0].name, "FastEthernet0/0")
        self.assertEqual(interfaces[0].ip_address, "192.168.141.11")
        self.assertEqual(interfaces[0].status, "up")
        self.assertEqual(interfaces[0].protocol, "up")
        self.assertEqual(interfaces[1].status, "administratively down")

    def test_parses_interface_error_counters(self) -> None:
        counters = parse_interface_counters(
            fixture("show_interface_fa00.txt")
        )

        self.assertEqual(counters.input_errors, 0)
        self.assertEqual(counters.crc_errors, 0)
        self.assertEqual(counters.output_errors, 0)
        self.assertEqual(counters.output_drops, 0)

    def test_parses_ios_ping_success_and_latency(self) -> None:
        ping = parse_ping(fixture("ping_success.txt"))

        self.assertIsNotNone(ping)
        assert ping is not None
        self.assertEqual(ping.packet_loss_percent, 0.0)
        self.assertEqual(ping.latency_min_ms, 1.0)
        self.assertEqual(ping.latency_avg_ms, 18.0)
        self.assertEqual(ping.latency_max_ms, 52.0)

    def test_parses_ios_ping_total_loss(self) -> None:
        ping = parse_ping("Success rate is 0 percent (0/10)")

        self.assertIsNotNone(ping)
        assert ping is not None
        self.assertEqual(ping.packet_loss_percent, 100.0)
        self.assertIsNone(ping.latency_avg_ms)

    def test_parses_linux_management_ping(self) -> None:
        output = """
5 packets transmitted, 5 received, 0% packet loss, time 4009ms
rtt min/avg/max/mdev = 3.655/12.384/24.448/7.082 ms
"""

        ping = parse_linux_ping(output)

        self.assertIsNotNone(ping)
        assert ping is not None
        self.assertEqual(ping.packet_loss_percent, 0.0)
        self.assertAlmostEqual(ping.latency_avg_ms or 0.0, 12.384)


if __name__ == "__main__":
    unittest.main()


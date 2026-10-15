from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.models import InterfaceMetrics, PingMetrics  # noqa: E402
from app.services.health.evaluator import evaluate_health  # noqa: E402


class HealthEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.interface = InterfaceMetrics(
            name="FastEthernet0/0",
            ip_address="192.168.141.11",
            status="up",
            protocol="up",
        )
        self.ping = PingMetrics(
            packet_loss_percent=0.0,
            latency_min_ms=1.0,
            latency_avg_ms=18.0,
            latency_max_ms=52.0,
        )

    def test_healthy_when_all_metrics_are_below_thresholds(self) -> None:
        result = evaluate_health(
            ssh_ok=True,
            cpu_percent=69.0,
            ram_percent=74.0,
            management_ping=self.ping,
            path_ping=self.ping,
            interfaces=[self.interface],
        )

        self.assertEqual(result.status, "Healthy")
        self.assertEqual(result.findings, [])

    def test_warning_at_cpu_boundary(self) -> None:
        result = evaluate_health(
            ssh_ok=True,
            cpu_percent=70.0,
            ram_percent=20.0,
            management_ping=self.ping,
            path_ping=self.ping,
            interfaces=[self.interface],
        )

        self.assertEqual(result.status, "Warning")

    def test_critical_at_cpu_boundary(self) -> None:
        result = evaluate_health(
            ssh_ok=True,
            cpu_percent=90.0,
            ram_percent=20.0,
            management_ping=self.ping,
            path_ping=self.ping,
            interfaces=[self.interface],
        )

        self.assertEqual(result.status, "Critical")

    def test_critical_when_monitored_interface_is_down(self) -> None:
        down = InterfaceMetrics(
            name="FastEthernet0/0",
            ip_address="192.168.141.11",
            status="up",
            protocol="down",
        )

        result = evaluate_health(
            ssh_ok=True,
            cpu_percent=4.0,
            ram_percent=21.0,
            management_ping=self.ping,
            path_ping=self.ping,
            interfaces=[down],
        )

        self.assertEqual(result.status, "Critical")

    def test_missing_metric_creates_warning(self) -> None:
        result = evaluate_health(
            ssh_ok=True,
            cpu_percent=None,
            ram_percent=21.0,
            management_ping=self.ping,
            path_ping=self.ping,
            interfaces=[self.interface],
        )

        self.assertEqual(result.status, "Warning")
        self.assertTrue(any("CPU" in item.message for item in result.findings))

    def test_ssh_failure_is_critical(self) -> None:
        result = evaluate_health(
            ssh_ok=False,
            cpu_percent=None,
            ram_percent=None,
            management_ping=None,
            path_ping=None,
            interfaces=[],
        )

        self.assertEqual(result.status, "Critical")

    def test_management_ping_below_configured_loss_threshold_is_healthy(
        self,
    ) -> None:
        management_ping = PingMetrics(
            packet_loss_percent=5.0,
            latency_min_ms=1.0,
            latency_avg_ms=18.0,
            latency_max_ms=52.0,
        )

        result = evaluate_health(
            ssh_ok=True,
            cpu_percent=4.0,
            ram_percent=21.0,
            management_ping=management_ping,
            path_ping=self.ping,
            interfaces=[self.interface],
        )

        self.assertEqual(result.status, "Healthy")

    def test_management_ping_at_critical_loss_threshold_is_critical(
        self,
    ) -> None:
        management_ping = PingMetrics(
            packet_loss_percent=30.0,
            latency_min_ms=1.0,
            latency_avg_ms=18.0,
            latency_max_ms=52.0,
        )

        result = evaluate_health(
            ssh_ok=True,
            cpu_percent=4.0,
            ram_percent=21.0,
            management_ping=management_ping,
            path_ping=self.ping,
            interfaces=[self.interface],
        )

        self.assertEqual(result.status, "Critical")

    def test_missing_optional_path_ping_does_not_create_warning(self) -> None:
        result = evaluate_health(
            ssh_ok=True,
            cpu_percent=4.0,
            ram_percent=21.0,
            management_ping=self.ping,
            path_ping=None,
            path_ping_required=False,
            interfaces=[self.interface],
        )

        self.assertEqual(result.status, "Healthy")
        self.assertEqual(result.findings, [])


if __name__ == "__main__":
    unittest.main()


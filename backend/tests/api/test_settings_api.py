from __future__ import annotations

from fastapi.testclient import TestClient

from app.domain.models import InterfaceMetrics, PingMetrics
from app.services.health.evaluator import evaluate_health


def test_settings_can_be_read_and_updated(client: TestClient) -> None:
    current = client.get("/api/v1/settings")

    assert current.status_code == 200
    assert current.json()["cpu_warning_percent"] == 70.0
    assert current.json()["scheduler_interval_minutes"] == 15
    assert current.json()["scheduler_cooldown_seconds"] == 5

    payload = {
        **current.json(),
        "cpu_warning_percent": 50.0,
        "cpu_critical_percent": 80.0,
        "scheduler_interval_minutes": 10,
        "scheduler_cooldown_seconds": 2,
        "max_concurrent_checks": 4,
    }
    updated = client.put("/api/v1/settings", json=payload)

    assert updated.status_code == 200
    assert updated.json()["cpu_warning_percent"] == 50.0
    assert updated.json()["scheduler_cooldown_seconds"] == 2
    assert client.get("/api/v1/settings").json() == updated.json()


def test_settings_reject_invalid_threshold_order(client: TestClient) -> None:
    payload = client.get("/api/v1/settings").json()
    payload.update(
        cpu_warning_percent=90.0,
        cpu_critical_percent=80.0,
    )

    response = client.put("/api/v1/settings", json=payload)

    assert response.status_code == 422


def test_evaluator_accepts_configurable_thresholds() -> None:
    ping = PingMetrics(0.0, 1.0, 10.0, 15.0)
    interface = InterfaceMetrics(
        name="FastEthernet0/0",
        ip_address="192.168.141.11",
        status="up",
        protocol="up",
    )

    result = evaluate_health(
        ssh_ok=True,
        cpu_percent=55.0,
        ram_percent=20.0,
        management_ping=ping,
        path_ping=ping,
        interfaces=[interface],
        thresholds={"cpu_warning_percent": 50.0},
    )

    assert result.status == "Warning"


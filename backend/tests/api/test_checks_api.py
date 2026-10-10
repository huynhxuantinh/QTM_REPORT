from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_health_check_runner
from app.core.security import CredentialCipher
from app.services.health_checks import HealthCheckService

from tests.api.test_devices_api import DEVICE_PAYLOAD
from tests.services.test_health_checks import FakeCollector


def test_run_check_and_read_persisted_result(
    client: TestClient,
    session_factory: sessionmaker[Session],
    settings,
) -> None:
    created_device = client.post("/api/v1/devices", json=DEVICE_PAYLOAD).json()

    def run_check(check_id: int) -> None:
        with session_factory() as session:
            service = HealthCheckService(
                session,
                CredentialCipher(settings.credential_key),
                FakeCollector(),
            )
            service.execute(check_id)

    client.app.dependency_overrides[get_health_check_runner] = lambda: run_check

    accepted = client.post(
        f"/api/v1/devices/{created_device['id']}/checks"
    )

    assert accepted.status_code == 202
    assert accepted.json()["execution_status"] == "running"
    check_id = accepted.json()["id"]

    result = client.get(f"/api/v1/checks/{check_id}")
    assert result.status_code == 200
    body = result.json()
    assert body["overall_status"] == "Warning"
    assert body["cpu_percent"] == 37.0
    assert body["ram_percent"] == 65.0
    assert body["interfaces"][0]["name"] == "FastEthernet0/0"
    assert body["pings"][0]["latency_avg_ms"] == 1.5

    history = client.get(
        f"/api/v1/devices/{created_device['id']}/history"
    )
    assert history.status_code == 200
    assert history.json()["total"] == 1
    assert history.json()["items"][0]["id"] == check_id


def test_check_endpoints_return_not_found(client: TestClient) -> None:
    assert client.post("/api/v1/devices/999/checks").status_code == 404
    assert client.get("/api/v1/checks/999").status_code == 404

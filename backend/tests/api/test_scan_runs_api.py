from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_scan_run_runner
from app.core.security import CredentialCipher
from app.services.health_checks import HealthCheckService
from app.services.scan_runs import ScanRunService

from tests.api.test_devices_api import DEVICE_PAYLOAD
from tests.services.test_health_checks import FakeCollector


def test_run_all_checks_only_active_devices_and_persists_scan(
    client: TestClient,
    session_factory: sessionmaker[Session],
    settings,
) -> None:
    active = client.post("/api/v1/devices", json=DEVICE_PAYLOAD).json()
    inactive_payload = {
        **DEVICE_PAYLOAD,
        "name": "R2",
        "host": "192.168.141.12",
        "is_active": False,
    }
    assert client.post("/api/v1/devices", json=inactive_payload).status_code == 201

    def run_scan(scan_id: int) -> None:
        with session_factory() as session:
            check_ids = ScanRunService(session).check_ids(scan_id)
        for check_id in check_ids:
            with session_factory() as session:
                HealthCheckService(
                    session,
                    CredentialCipher(settings.credential_key),
                    FakeCollector(),
                ).execute(check_id)
        with session_factory() as session:
            ScanRunService(session).finish(scan_id)

    client.app.dependency_overrides[get_scan_run_runner] = lambda: run_scan

    accepted = client.post("/api/v1/checks/run-all")

    assert accepted.status_code == 202
    scan_id = accepted.json()["id"]
    result = client.get(f"/api/v1/scan-runs/{scan_id}")
    assert result.status_code == 200
    body = result.json()
    assert body["trigger"] == "manual"
    assert body["execution_status"] == "succeeded"
    assert body["total_checks"] == 1
    assert body["completed_checks"] == 1
    assert body["failed_checks"] == 0
    assert [item["device_id"] for item in body["checks"]] == [active["id"]]


def test_run_all_rejects_overlapping_scan(
    client: TestClient,
) -> None:
    assert client.post("/api/v1/devices", json=DEVICE_PAYLOAD).status_code == 201
    client.app.dependency_overrides[get_scan_run_runner] = lambda: lambda _: None

    assert client.post("/api/v1/checks/run-all").status_code == 202
    duplicate = client.post("/api/v1/checks/run-all")

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "A scan is already running"


def test_scan_run_not_found(client: TestClient) -> None:
    assert client.get("/api/v1/scan-runs/999").status_code == 404

from __future__ import annotations

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.db.models.device import Device


DEVICE_PAYLOAD = {
    "name": "R1",
    "host": "192.168.141.11",
    "port": 22,
    "device_type": "cisco_ios",
    "username": "admin",
    "password": "qtm",
    "secret": "enable-secret",
    "site": "GNS3-LAB",
}


def test_health_endpoint_checks_database(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_device_crud_masks_and_encrypts_credentials(
    client: TestClient,
    session_factory: sessionmaker[Session],
    settings,
) -> None:
    created = client.post("/api/v1/devices", json=DEVICE_PAYLOAD)

    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "R1"
    assert body["host"] == "192.168.141.11"
    assert "password" not in body
    assert "secret" not in body
    device_id = body["id"]

    listed = client.get("/api/v1/devices")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == device_id

    fetched = client.get(f"/api/v1/devices/{device_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "R1"

    updated = client.patch(
        f"/api/v1/devices/{device_id}",
        json={"name": "R1-CORE", "password": "new-password"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "R1-CORE"

    with session_factory() as session:
        row = session.scalar(select(Device).where(Device.id == device_id))
        assert row is not None
        assert row.encrypted_password != "new-password"
        assert (
            Fernet(settings.credential_key.encode("ascii"))
            .decrypt(row.encrypted_password.encode("ascii"))
            .decode("utf-8")
            == "new-password"
        )

    deleted = client.delete(f"/api/v1/devices/{device_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/devices/{device_id}").status_code == 404


def test_rejects_host_outside_configured_lab_network(
    client: TestClient,
) -> None:
    payload = {**DEVICE_PAYLOAD, "host": "8.8.8.8"}

    response = client.post("/api/v1/devices", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == "Host is outside configured lab CIDRs"


def test_rejects_duplicate_active_device(client: TestClient) -> None:
    assert client.post("/api/v1/devices", json=DEVICE_PAYLOAD).status_code == 201

    duplicate = client.post("/api/v1/devices", json=DEVICE_PAYLOAD)

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "An active device already uses this host and port"


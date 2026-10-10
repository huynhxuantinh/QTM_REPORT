from __future__ import annotations

import base64
import hashlib
import os

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_settings
from app.core.config import Settings
from app.db.models.user import User


def _password_hash(password: str) -> str:
    iterations = 210_000
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, iterations
    )
    return "$".join(
        (
            "pbkdf2_sha256",
            str(iterations),
            base64.urlsafe_b64encode(salt).decode(),
            base64.urlsafe_b64encode(digest).decode(),
        )
    )


def test_admin_login_protects_management_routes(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    secured = Settings(
        database_url="sqlite+pysqlite://",
        credential_key=Fernet.generate_key().decode(),
        auth_enabled=True,
        jwt_secret="test-jwt-secret-that-is-long-enough",
    )
    client.app.dependency_overrides[get_settings] = lambda: secured
    with session_factory() as session:
        session.add(
            User(
                username="admin",
                password_hash=_password_hash("qtm"),
                is_active=True,
            )
        )
        session.commit()

    assert client.get("/api/v1/devices").status_code == 401
    assert client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong"},
    ).status_code == 401

    login = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "qtm"},
    )

    assert login.status_code == 200
    token = login.json()["access_token"]
    authorized = client.get(
        "/api/v1/devices",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert authorized.status_code == 200


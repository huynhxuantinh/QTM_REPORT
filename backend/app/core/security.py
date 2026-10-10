from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any

from cryptography.fernet import Fernet


class CredentialCipher:
    """Encrypt device credentials before database persistence."""

    def __init__(self, key: str) -> None:
        if not key:
            raise ValueError("CREDENTIAL_KEY must be configured")
        self._fernet = Fernet(key.encode("ascii"))

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode("utf-8")).decode("ascii")

    def decrypt(self, value: str) -> str:
        return self._fernet.decrypt(value.encode("ascii")).decode("utf-8")


def hash_password(password: str, *, iterations: int = 210_000) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return "$".join(
        (
            "pbkdf2_sha256",
            str(iterations),
            _b64encode(salt),
            _b64encode(digest),
        )
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            _b64decode(salt),
            int(iterations),
        )
        return hmac.compare_digest(digest, _b64decode(expected))
    except (ValueError, TypeError):
        return False


def create_access_token(
    username: str,
    secret: str,
    expires_minutes: int,
) -> str:
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + expires_minutes * 60,
    }
    unsigned = ".".join(
        (_json_segment(header), _json_segment(payload))
    )
    signature = hmac.new(
        secret.encode("utf-8"), unsigned.encode("ascii"), hashlib.sha256
    ).digest()
    return f"{unsigned}.{_b64encode(signature)}"


def decode_access_token(token: str, secret: str) -> dict[str, Any]:
    try:
        header_part, payload_part, signature_part = token.split(".")
        unsigned = f"{header_part}.{payload_part}"
        expected = hmac.new(
            secret.encode("utf-8"), unsigned.encode("ascii"), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(expected, _b64decode(signature_part)):
            raise ValueError("Invalid token signature")
        payload = json.loads(_b64decode(payload_part))
        if int(payload["exp"]) <= int(time.time()):
            raise ValueError("Token has expired")
        if not payload.get("sub"):
            raise ValueError("Token subject is missing")
        return payload
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("Invalid access token") from error


def _json_segment(value: dict[str, Any]) -> str:
    return _b64encode(
        json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)

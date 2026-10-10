from __future__ import annotations

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

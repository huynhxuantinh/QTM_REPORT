from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import CredentialCipher
from app.db.session import get_db
from app.repositories.devices import DeviceRepository
from app.services.devices import DeviceService


@lru_cache
def get_settings() -> Settings:
    """Return process-wide application settings."""
    return Settings()


def get_device_service(
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DeviceService:
    """Build the device service for one request."""
    return DeviceService(
        repository=DeviceRepository(db),
        cipher=CredentialCipher(settings.credential_key),
        lab_networks=settings.lab_networks,
    )

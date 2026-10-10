from __future__ import annotations

from functools import lru_cache
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import CredentialCipher
from app.db.session import get_db
from app.repositories.devices import DeviceRepository
from app.services.devices import DeviceService
from app.services.collectors.cisco_ios import CiscoIosCollector
from app.services.health_checks import HealthCheckService
from app.services.scan_runner import ThreadedScanRunner
from app.services.scan_runs import ScanRunService


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


def get_health_check_service(
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthCheckService:
    return HealthCheckService(
        db,
        CredentialCipher(settings.credential_key),
        CiscoIosCollector(),
    )


HealthCheckRunner = Callable[[int], None]


def get_health_check_runner(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthCheckRunner:
    def run(check_id: int) -> None:
        from app.db.session import SessionLocal

        with SessionLocal() as session:
            service = HealthCheckService(
                session,
                CredentialCipher(settings.credential_key),
                CiscoIosCollector(),
            )
            service.execute(check_id)

    return run


def get_scan_run_service(
    db: Annotated[Session, Depends(get_db)],
) -> ScanRunService:
    return ScanRunService(db)


ScanRunRunner = Callable[[int], None]


def get_scan_run_runner(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ScanRunRunner:
    return ThreadedScanRunner(settings)

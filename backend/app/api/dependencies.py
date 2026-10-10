from __future__ import annotations

from functools import lru_cache
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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
from app.core.security import decode_access_token
from app.db.models.user import User
from app.repositories.settings import SystemSettingRepository
from app.repositories.users import UserRepository
from app.services.settings import SystemSettingService


@lru_cache
def get_settings() -> Settings:
    """Return process-wide application settings."""
    return Settings()


bearer_scheme = HTTPBearer(auto_error=False)


def require_admin(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User | None:
    if not settings.auth_enabled:
        return None
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = decode_access_token(credentials.credentials, settings.jwt_secret)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    user = UserRepository(db).find_by_username(str(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid access token")
    return user


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


def get_system_setting_service(
    db: Annotated[Session, Depends(get_db)],
) -> SystemSettingService:
    return SystemSettingService(SystemSettingRepository(db))


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
ConnectionTester = Callable[[int], dict[str, object]]


def get_connection_tester(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ConnectionTester:
    def test(device_id: int) -> dict[str, object]:
        from app.db.session import SessionLocal

        with SessionLocal() as session:
            service = HealthCheckService(
                session,
                CredentialCipher(settings.credential_key),
                CiscoIosCollector(),
            )
            return service.test_connection(device_id)

    return test


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

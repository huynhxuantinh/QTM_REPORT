from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from app.core.config import Settings
from app.core.security import CredentialCipher
from app.db.session import SessionLocal
from app.services.collectors.cisco_ios import CiscoIosCollector
from app.services.health_checks import HealthCheckService
from app.services.scan_runs import ScanRunService
from app.repositories.settings import SystemSettingRepository


logger = logging.getLogger(__name__)


class ThreadedScanRunner:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def __call__(self, scan_id: int) -> None:
        Thread(
            target=self._run,
            args=(scan_id,),
            name=f"scan-run-{scan_id}",
            daemon=True,
        ).start()

    def _run(self, scan_id: int) -> None:
        try:
            with SessionLocal() as session:
                check_ids = ScanRunService(session).check_ids(scan_id)
                max_workers = (
                    SystemSettingRepository(session)
                    .get_or_create()
                    .max_concurrent_checks
                )
            with ThreadPoolExecutor(
                max_workers=max_workers,
                thread_name_prefix=f"scan-{scan_id}",
            ) as executor:
                list(executor.map(self._run_check, check_ids))
            with SessionLocal() as session:
                ScanRunService(session).finish(scan_id)
        except Exception:
            logger.exception("Scan run failed", extra={"scan_id": scan_id})
            with SessionLocal() as session:
                ScanRunService(session).fail(scan_id)

    def _run_check(self, check_id: int) -> None:
        with SessionLocal() as session:
            HealthCheckService(
                session,
                CredentialCipher(self._settings.credential_key),
                CiscoIosCollector(),
            ).execute(check_id)

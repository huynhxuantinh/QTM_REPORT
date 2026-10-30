from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.health_check import HealthCheck
from app.db.models.scan_run import ScanRun
from app.repositories.devices import DeviceRepository
from app.repositories.scan_runs import ScanRunRepository


class ScanRunNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("Scan run not found")


class ScanAlreadyRunningError(Exception):
    def __init__(self) -> None:
        super().__init__("A scan is already running")


class ScanRunService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._devices = DeviceRepository(session)
        self._scans = ScanRunRepository(session)

    def start(self, trigger: str) -> ScanRun:
        if self._scans.find_running() is not None:
            raise ScanAlreadyRunningError

        device_ids = self._devices.list_active_ids()
        scan = ScanRun(trigger=trigger, total_checks=len(device_ids))
        scan.checks = [
            HealthCheck(device_id=device_id, execution_status="running")
            for device_id in device_ids
        ]
        if not device_ids:
            scan.execution_status = "succeeded"
            scan.finished_at = datetime.now(timezone.utc)

        try:
            return self._scans.save(scan)
        except IntegrityError as error:
            self._scans.rollback()
            raise ScanAlreadyRunningError from error

    def get(self, scan_id: int) -> ScanRun:
        scan = self._scans.get(scan_id)
        if scan is None:
            raise ScanRunNotFoundError
        return scan

    def check_ids(self, scan_id: int) -> list[int]:
        return [check.id for check in self.get(scan_id).checks]

    def finish(self, scan_id: int) -> ScanRun:
        scan = self.get(scan_id)
        self._session.expire_all()
        scan = self.get(scan_id)
        scan.completed_checks = sum(
            item.execution_status in {"succeeded", "failed"}
            for item in scan.checks
        )
        scan.failed_checks = sum(
            item.execution_status == "failed" for item in scan.checks
        )
        scan.execution_status = "succeeded"
        scan.finished_at = datetime.now(timezone.utc)
        return self._scans.save(scan)

    def fail(self, scan_id: int) -> ScanRun:
        scan = self.get(scan_id)
        self._session.expire_all()
        scan = self.get(scan_id)
        failed_at = datetime.now(timezone.utc)
        for check in scan.checks:
            if check.execution_status != "running":
                continue
            check.execution_status = "failed"
            check.finished_at = failed_at
            check.checked_at = failed_at
            check.error = "Scan runner stopped before completion"

        scan.completed_checks = sum(
            check.execution_status in {"succeeded", "failed"}
            for check in scan.checks
        )
        scan.failed_checks = sum(
            check.execution_status == "failed" for check in scan.checks
        )
        scan.execution_status = "failed"
        scan.finished_at = failed_at
        return self._scans.save(scan)

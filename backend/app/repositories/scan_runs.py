from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.scan_run import ScanRun


class ScanRunRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, scan_id: int) -> ScanRun | None:
        return self._session.scalar(
            select(ScanRun)
            .where(ScanRun.id == scan_id)
            .options(selectinload(ScanRun.checks))
        )

    def find_running(self) -> ScanRun | None:
        return self._session.scalar(
            select(ScanRun).where(ScanRun.execution_status == "running")
        )

    def save(self, scan: ScanRun) -> ScanRun:
        self._session.add(scan)
        self._session.commit()
        return self.get(scan.id) or scan

    def rollback(self) -> None:
        self._session.rollback()

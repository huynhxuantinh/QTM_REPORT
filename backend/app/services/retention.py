from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Event, Thread

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models.health_check import (
    HealthCheck,
    HealthFindingResult,
    InterfaceResult,
    PingResult,
)
from app.db.models.scan_run import ScanRun


logger = logging.getLogger(__name__)
DAILY_CLEANUP_SECONDS = 86_400.0


@dataclass(frozen=True, slots=True)
class RetentionResult:
    deleted_checks: int
    deleted_scans: int


class HistoryRetentionService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def prune(
        self,
        *,
        retention_days: int,
        now: datetime | None = None,
    ) -> RetentionResult:
        cutoff = (now or datetime.now(timezone.utc)) - timedelta(
            days=retention_days
        )
        old_check_ids = select(HealthCheck.id).where(
            HealthCheck.execution_status != "running",
            HealthCheck.finished_at.is_not(None),
            HealthCheck.finished_at < cutoff,
        )
        for model in (InterfaceResult, PingResult, HealthFindingResult):
            self._session.execute(
                delete(model).where(
                    model.health_check_id.in_(old_check_ids)
                )
            )
        deleted_checks = self._session.execute(
            delete(HealthCheck).where(HealthCheck.id.in_(old_check_ids))
        ).rowcount
        deleted_scans = self._session.execute(
            delete(ScanRun).where(
                ScanRun.execution_status != "running",
                ScanRun.finished_at.is_not(None),
                ScanRun.finished_at < cutoff,
            )
        ).rowcount
        self._session.commit()
        return RetentionResult(
            deleted_checks=int(deleted_checks or 0),
            deleted_scans=int(deleted_scans or 0),
        )


def run_retention_loop(
    *,
    stopped: Event,
    cleanup_once: Callable[[], None],
    wait: Callable[[float], bool],
) -> None:
    while not stopped.is_set():
        try:
            cleanup_once()
        except Exception:
            logger.exception("Daily history retention cleanup failed")
        if wait(DAILY_CLEANUP_SECONDS):
            break


class HistoryRetentionScheduler:
    def __init__(self, cleanup_once: Callable[[], None]) -> None:
        self._cleanup_once = cleanup_once
        self._stopped = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stopped.clear()
        self._thread = Thread(
            target=run_retention_loop,
            kwargs={
                "stopped": self._stopped,
                "cleanup_once": self._cleanup_once,
                "wait": self._stopped.wait,
            },
            name="history-retention-cleaner",
            daemon=True,
        )
        self._thread.start()

    def shutdown(self, wait: bool = False) -> None:
        self._stopped.set()
        if wait and self._thread is not None:
            self._thread.join()

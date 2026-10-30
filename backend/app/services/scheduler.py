from __future__ import annotations

import logging
from collections.abc import Callable
from threading import Event, Thread

from app.core.config import Settings
from app.db.session import SessionLocal
from app.repositories.settings import SystemSettingRepository
from app.services.scan_runner import ThreadedScanRunner
from app.services.scan_runs import ScanAlreadyRunningError, ScanRunService


logger = logging.getLogger(__name__)
DEFAULT_COOLDOWN_SECONDS = 5.0


def run_scheduled_scan(settings: Settings) -> None:
    """Run one complete scan synchronously so cycles never overlap."""
    try:
        with SessionLocal() as session:
            scan = ScanRunService(session).start("scheduled")
        ThreadedScanRunner(settings).run_sync(scan.id)
    except ScanAlreadyRunningError:
        logger.info("Continuous scan skipped because another scan is running")


def run_continuous_scan_loop(
    *,
    stopped: Event,
    scan_once: Callable[[], None],
    cooldown_seconds: Callable[[], float],
    wait: Callable[[float], bool],
) -> None:
    """Run scans serially with backpressure and a configurable cooldown."""
    while not stopped.is_set():
        try:
            scan_once()
        except Exception:
            logger.exception("Continuous network scan failed")
        try:
            delay = max(1.0, float(cooldown_seconds()))
        except Exception:
            logger.exception(
                "Could not load scheduler cooldown; using fallback",
                extra={"fallback_seconds": DEFAULT_COOLDOWN_SECONDS},
            )
            delay = DEFAULT_COOLDOWN_SECONDS
        if wait(delay):
            break


class ContinuousScanScheduler:
    def __init__(
        self,
        settings: Settings,
        scan_once: Callable[[], None] | None = None,
        cooldown_seconds: Callable[[], float] | None = None,
    ) -> None:
        self._settings = settings
        self._scan_once = scan_once or (lambda: run_scheduled_scan(settings))
        self._cooldown_seconds = cooldown_seconds or self._saved_cooldown
        self._stopped = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stopped.clear()
        self._thread = Thread(
            target=run_continuous_scan_loop,
            kwargs={
                "stopped": self._stopped,
                "scan_once": self._scan_once,
                "cooldown_seconds": self._cooldown_seconds,
                "wait": self._stopped.wait,
            },
            name="continuous-network-monitor",
            daemon=True,
        )
        self._thread.start()

    def shutdown(self, wait: bool = False) -> None:
        self._stopped.set()
        if wait and self._thread is not None:
            self._thread.join()

    def _saved_cooldown(self) -> float:
        with SessionLocal() as session:
            return float(
                SystemSettingRepository(session)
                .get_or_create()
                .scheduler_cooldown_seconds
            )


def build_scheduler(
    settings: Settings,
    scheduled_scan: Callable[[], None] | None = None,
) -> ContinuousScanScheduler:
    return ContinuousScanScheduler(
        settings,
        scan_once=scheduled_scan,
    )

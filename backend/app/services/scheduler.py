from __future__ import annotations

import logging
from collections.abc import Callable

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import Settings
from app.db.session import SessionLocal
from app.services.scan_runner import ThreadedScanRunner
from app.services.scan_runs import ScanAlreadyRunningError, ScanRunService


logger = logging.getLogger(__name__)


def run_scheduled_scan(settings: Settings) -> None:
    try:
        with SessionLocal() as session:
            scan = ScanRunService(session).start("scheduled")
        ThreadedScanRunner(settings)(scan.id)
    except ScanAlreadyRunningError:
        logger.info("Scheduled scan skipped because another scan is running")


def build_scheduler(
    settings: Settings,
    scheduled_scan: Callable[[], None] | None = None,
) -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        scheduled_scan or (lambda: run_scheduled_scan(settings)),
        trigger="interval",
        minutes=settings.scheduler_interval_minutes,
        id="network-health-scan",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    return scheduler

from __future__ import annotations

from datetime import timedelta

from app.services.scheduler import build_scheduler


def test_scheduler_registers_one_coalesced_scan_job(settings) -> None:
    configured = settings.model_copy(
        update={"scheduler_interval_minutes": 5}
    )

    scheduler = build_scheduler(configured, lambda: None)

    job = scheduler.get_job("network-health-scan")
    assert job is not None
    assert job.trigger.interval == timedelta(minutes=5)
    assert job.coalesce is True
    assert job.max_instances == 1

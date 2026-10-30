from __future__ import annotations

from threading import Event

from sqlalchemy.exc import OperationalError

from app.services.scan_runner import calculate_worker_count
from app.services.scheduler import run_continuous_scan_loop


def test_worker_count_adapts_to_device_count_and_limit() -> None:
    assert calculate_worker_count(device_count=3, configured_limit=3) == 3
    assert calculate_worker_count(device_count=4, configured_limit=3) == 3
    assert calculate_worker_count(device_count=9, configured_limit=3) == 3
    assert calculate_worker_count(device_count=2, configured_limit=10) == 2
    assert calculate_worker_count(device_count=0, configured_limit=3) == 1


def test_continuous_loop_finishes_each_scan_before_starting_next() -> None:
    stopped = Event()
    events: list[str] = []
    cooldowns: list[float] = []
    cycle = 0

    def scan_once() -> None:
        nonlocal cycle
        cycle += 1
        events.extend([f"start-{cycle}", f"end-{cycle}"])
        if cycle == 3:
            stopped.set()

    def wait(seconds: float) -> bool:
        cooldowns.append(seconds)
        return stopped.is_set()

    run_continuous_scan_loop(
        stopped=stopped,
        scan_once=scan_once,
        cooldown_seconds=lambda: 5.0,
        wait=wait,
    )

    assert events == [
        "start-1",
        "end-1",
        "start-2",
        "end-2",
        "start-3",
        "end-3",
    ]
    assert cooldowns == [5.0, 5.0, 5.0]


def test_continuous_loop_survives_cooldown_database_failure() -> None:
    stopped = Event()
    scans = 0
    cooldown_reads = 0
    waits: list[float] = []

    def scan_once() -> None:
        nonlocal scans
        scans += 1
        if scans == 2:
            stopped.set()

    def cooldown_seconds() -> float:
        nonlocal cooldown_reads
        cooldown_reads += 1
        if cooldown_reads == 1:
            raise OperationalError("SELECT cooldown", {}, Exception("reset"))
        return 9.0

    def wait(seconds: float) -> bool:
        waits.append(seconds)
        return stopped.is_set()

    run_continuous_scan_loop(
        stopped=stopped,
        scan_once=scan_once,
        cooldown_seconds=cooldown_seconds,
        wait=wait,
    )

    assert scans == 2
    assert waits == [5.0, 9.0]

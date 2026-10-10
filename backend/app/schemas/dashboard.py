from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class RecentCheckRead(BaseModel):
    check_id: int
    device_id: int
    device_name: str
    overall_status: str | None
    checked_at: datetime | None
    cpu_percent: float | None
    ram_percent: float | None


class DashboardSummaryRead(BaseModel):
    total_devices: int
    healthy_devices: int
    warning_devices: int
    critical_devices: int
    unknown_devices: int
    last_scan_at: datetime | None
    recent_checks: list[RecentCheckRead]

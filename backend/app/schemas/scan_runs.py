from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.health_checks import CheckAccepted


class ScanRunAccepted(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trigger: str
    execution_status: str
    started_at: datetime
    total_checks: int


class ScanRunRead(ScanRunAccepted):
    finished_at: datetime | None
    completed_checks: int
    failed_checks: int
    checks: list[CheckAccepted]

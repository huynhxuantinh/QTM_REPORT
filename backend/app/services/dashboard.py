from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.device import Device
from app.db.models.health_check import HealthCheck
from app.db.models.scan_run import ScanRun


class DashboardService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def summary(self) -> dict[str, object]:
        latest_ids = (
            select(
                HealthCheck.device_id,
                func.max(HealthCheck.id).label("check_id"),
            )
            .where(HealthCheck.execution_status == "succeeded")
            .group_by(HealthCheck.device_id)
            .subquery()
        )
        rows = self._session.execute(
            select(Device, HealthCheck)
            .outerjoin(latest_ids, latest_ids.c.device_id == Device.id)
            .outerjoin(HealthCheck, HealthCheck.id == latest_ids.c.check_id)
            .where(
                Device.deleted_at.is_(None),
                Device.is_active.is_(True),
            )
            .order_by(Device.id)
        ).all()
        counts = {"Healthy": 0, "Warning": 0, "Critical": 0}
        unknown = 0
        for _, check in rows:
            if check is None or check.overall_status not in counts:
                unknown += 1
            else:
                counts[check.overall_status] += 1

        recent = self._session.execute(
            select(HealthCheck, Device.name)
            .join(Device, Device.id == HealthCheck.device_id)
            .where(
                Device.deleted_at.is_(None),
                HealthCheck.execution_status == "succeeded",
            )
            .order_by(HealthCheck.started_at.desc(), HealthCheck.id.desc())
            .limit(10)
        ).all()
        last_scan_at = self._session.scalar(
            select(func.max(ScanRun.started_at))
        )
        return {
            "total_devices": len(rows),
            "healthy_devices": counts["Healthy"],
            "warning_devices": counts["Warning"],
            "critical_devices": counts["Critical"],
            "unknown_devices": unknown,
            "last_scan_at": last_scan_at,
            "recent_checks": [
                {
                    "check_id": check.id,
                    "device_id": check.device_id,
                    "device_name": device_name,
                    "overall_status": check.overall_status,
                    "checked_at": check.checked_at,
                    "cpu_percent": check.cpu_percent,
                    "ram_percent": check.ram_percent,
                }
                for check, device_name in recent
            ],
        }

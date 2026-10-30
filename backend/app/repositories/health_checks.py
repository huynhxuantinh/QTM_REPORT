from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.models.health_check import HealthCheck


class HealthCheckRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, health_check: HealthCheck) -> HealthCheck:
        self._session.add(health_check)
        self._session.commit()
        self._session.refresh(health_check)
        return health_check

    def get(self, check_id: int) -> HealthCheck | None:
        return self._session.scalar(
            select(HealthCheck)
            .where(HealthCheck.id == check_id)
            .options(
                selectinload(HealthCheck.interfaces),
                selectinload(HealthCheck.pings),
                selectinload(HealthCheck.findings),
            )
        )

    def find_running(self, device_id: int) -> HealthCheck | None:
        return self._session.scalar(
            select(HealthCheck).where(
                HealthCheck.device_id == device_id,
                HealthCheck.execution_status == "running",
            )
        )

    def latest_succeeded(
        self,
        device_id: int,
        *,
        before_check_id: int,
    ) -> HealthCheck | None:
        return self._session.scalar(
            select(HealthCheck)
            .where(
                HealthCheck.device_id == device_id,
                HealthCheck.execution_status == "succeeded",
                HealthCheck.checked_at.is_not(None),
                HealthCheck.id != before_check_id,
            )
            .options(selectinload(HealthCheck.interfaces))
            .order_by(HealthCheck.checked_at.desc(), HealthCheck.id.desc())
            .limit(1)
        )

    def save(self, health_check: HealthCheck) -> HealthCheck:
        self._session.add(health_check)
        self._session.commit()
        return self.get(health_check.id) or health_check

    def list_for_device(
        self,
        device_id: int,
        *,
        offset: int,
        limit: int,
    ) -> tuple[list[HealthCheck], int]:
        filters = [HealthCheck.device_id == device_id]
        items = list(
            self._session.scalars(
                select(HealthCheck)
                .where(*filters)
                .options(
                    selectinload(HealthCheck.interfaces),
                    selectinload(HealthCheck.pings),
                    selectinload(HealthCheck.findings),
                )
                .order_by(HealthCheck.started_at.desc(), HealthCheck.id.desc())
                .offset(offset)
                .limit(limit)
            )
        )
        total = self._session.scalar(
            select(func.count()).select_from(HealthCheck).where(*filters)
        )
        return items, int(total or 0)

    def rollback(self) -> None:
        self._session.rollback()

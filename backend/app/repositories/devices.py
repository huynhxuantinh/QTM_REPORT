from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.device import Device


class DeviceRepository:
    """Database operations for active devices."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, device: Device) -> Device:
        self._session.add(device)
        self._session.commit()
        self._session.refresh(device)
        return device

    def get(self, device_id: int) -> Device | None:
        return self._session.scalar(
            select(Device).where(
                Device.id == device_id,
                Device.deleted_at.is_(None),
            )
        )

    def find_by_host_port(self, host: str, port: int) -> Device | None:
        return self._session.scalar(
            select(Device).where(
                Device.host == host,
                Device.port == port,
                Device.deleted_at.is_(None),
            )
        )

    def list(
        self,
        *,
        offset: int,
        limit: int,
        site: str | None,
    ) -> tuple[list[Device], int]:
        filters = [Device.deleted_at.is_(None)]
        if site is not None:
            filters.append(Device.site == site)
        items = list(
            self._session.scalars(
                select(Device)
                .where(*filters)
                .order_by(Device.id)
                .offset(offset)
                .limit(limit)
            )
        )
        total = self._session.scalar(
            select(func.count()).select_from(Device).where(*filters)
        )
        return items, int(total or 0)

    def save(self, device: Device) -> Device:
        self._session.add(device)
        self._session.commit()
        self._session.refresh(device)
        return device

    def soft_delete(self, device: Device) -> None:
        device.deleted_at = datetime.now(timezone.utc)
        device.is_active = False
        self._session.add(device)
        self._session.commit()

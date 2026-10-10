from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.system_setting import SystemSetting


class SystemSettingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_or_create(self) -> SystemSetting:
        setting = self._session.get(SystemSetting, 1)
        if setting is None:
            setting = SystemSetting(id=1)
            self._session.add(setting)
            self._session.commit()
            self._session.refresh(setting)
        return setting

    def save(self, setting: SystemSetting) -> SystemSetting:
        self._session.add(setting)
        self._session.commit()
        self._session.refresh(setting)
        return setting

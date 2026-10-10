from __future__ import annotations

from app.db.models.system_setting import SystemSetting
from app.domain.models import HealthThresholds
from app.repositories.settings import SystemSettingRepository
from app.schemas.settings import SystemSettingPayload


class SystemSettingService:
    def __init__(self, repository: SystemSettingRepository) -> None:
        self._repository = repository

    def get(self) -> SystemSetting:
        return self._repository.get_or_create()

    def update(self, payload: SystemSettingPayload) -> SystemSetting:
        setting = self.get()
        for name, value in payload.model_dump().items():
            setattr(setting, name, value)
        return self._repository.save(setting)


def thresholds_from_setting(setting: SystemSetting) -> HealthThresholds:
    return HealthThresholds(
        cpu_warning_percent=setting.cpu_warning_percent,
        cpu_critical_percent=setting.cpu_critical_percent,
        ram_warning_percent=setting.ram_warning_percent,
        ram_critical_percent=setting.ram_critical_percent,
        packet_loss_warning_percent=setting.packet_loss_warning_percent,
        packet_loss_critical_percent=setting.packet_loss_critical_percent,
        latency_warning_ms=setting.latency_warning_ms,
        latency_critical_ms=setting.latency_critical_ms,
    )

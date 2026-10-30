from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_system_setting_service
from app.schemas.settings import SystemSettingPayload, SystemSettingRead
from app.services.settings import SystemSettingService


router = APIRouter(prefix="/settings", tags=["settings"])
ServiceDependency = Annotated[
    SystemSettingService, Depends(get_system_setting_service)
]


@router.get("", response_model=SystemSettingRead)
def get_settings(service: ServiceDependency) -> SystemSettingRead:
    return SystemSettingRead.model_validate(service.get())


@router.put("", response_model=SystemSettingRead)
def update_settings(
    payload: SystemSettingPayload,
    service: ServiceDependency,
) -> SystemSettingRead:
    setting = service.update(payload)
    return SystemSettingRead.model_validate(setting)

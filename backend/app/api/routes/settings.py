from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request

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
    request: Request,
    service: ServiceDependency,
) -> SystemSettingRead:
    setting = service.update(payload)
    scheduler = getattr(request.app.state, "scheduler", None)
    if scheduler is not None and scheduler.get_job("network-health-scan"):
        scheduler.reschedule_job(
            "network-health-scan",
            trigger="interval",
            minutes=setting.scheduler_interval_minutes,
        )
    return SystemSettingRead.model_validate(setting)

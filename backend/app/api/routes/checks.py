from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from app.api.dependencies import (
    HealthCheckRunner,
    get_health_check_runner,
    get_health_check_service,
    get_scan_run_runner,
    get_scan_run_service,
)
from app.schemas.health_checks import (
    CheckAccepted,
    HealthCheckPage,
    HealthCheckRead,
)
from app.services.devices import DeviceNotFoundError
from app.services.health_checks import (
    CheckAlreadyRunningError,
    CheckNotFoundError,
    DeviceInactiveError,
    HealthCheckService,
)
from app.schemas.scan_runs import ScanRunAccepted, ScanRunRead
from app.services.scan_runs import (
    ScanAlreadyRunningError,
    ScanRunNotFoundError,
    ScanRunService,
)


router = APIRouter(tags=["health-checks"])
ServiceDependency = Annotated[
    HealthCheckService, Depends(get_health_check_service)
]
RunnerDependency = Annotated[
    HealthCheckRunner, Depends(get_health_check_runner)
]
ScanServiceDependency = Annotated[ScanRunService, Depends(get_scan_run_service)]
ScanRunnerDependency = Annotated[HealthCheckRunner, Depends(get_scan_run_runner)]


def translate_error(error: Exception) -> HTTPException:
    if isinstance(error, (DeviceNotFoundError, CheckNotFoundError)):
        return HTTPException(status_code=404, detail=str(error))
    if isinstance(error, (CheckAlreadyRunningError, DeviceInactiveError)):
        return HTTPException(status_code=409, detail=str(error))
    if isinstance(error, ScanRunNotFoundError):
        return HTTPException(status_code=404, detail=str(error))
    if isinstance(error, ScanAlreadyRunningError):
        return HTTPException(status_code=409, detail=str(error))
    raise error


@router.post(
    "/checks/run-all",
    response_model=ScanRunAccepted,
    status_code=202,
)
def run_all_checks(
    service: ScanServiceDependency,
    runner: ScanRunnerDependency,
) -> ScanRunAccepted:
    try:
        scan = service.start("manual")
    except ScanAlreadyRunningError as error:
        raise translate_error(error) from error
    runner(scan.id)
    return ScanRunAccepted.model_validate(scan)


@router.get("/scan-runs/{scan_id}", response_model=ScanRunRead)
def get_scan_run(
    scan_id: int,
    service: ScanServiceDependency,
) -> ScanRunRead:
    try:
        return ScanRunRead.model_validate(service.get(scan_id))
    except ScanRunNotFoundError as error:
        raise translate_error(error) from error


@router.post(
    "/devices/{device_id}/checks",
    response_model=CheckAccepted,
    status_code=202,
)
def start_check(
    device_id: int,
    background_tasks: BackgroundTasks,
    service: ServiceDependency,
    runner: RunnerDependency,
) -> CheckAccepted:
    try:
        health_check = service.start(device_id)
    except (
        DeviceNotFoundError,
        CheckAlreadyRunningError,
        DeviceInactiveError,
    ) as error:
        raise translate_error(error) from error
    background_tasks.add_task(runner, health_check.id)
    return CheckAccepted.model_validate(health_check)


@router.get("/checks/{check_id}", response_model=HealthCheckRead)
def get_check(
    check_id: int,
    service: ServiceDependency,
) -> HealthCheckRead:
    try:
        return HealthCheckRead.model_validate(service.get(check_id))
    except CheckNotFoundError as error:
        raise translate_error(error) from error


@router.get(
    "/devices/{device_id}/history",
    response_model=HealthCheckPage,
)
def get_device_history(
    device_id: int,
    service: ServiceDependency,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> HealthCheckPage:
    try:
        items, total = service.history(
            device_id, offset=offset, limit=limit
        )
    except DeviceNotFoundError as error:
        raise translate_error(error) from error
    return HealthCheckPage(
        items=[HealthCheckRead.model_validate(item) for item in items],
        total=total,
        offset=offset,
        limit=limit,
    )

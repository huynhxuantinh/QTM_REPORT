from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.dependencies import get_device_service
from app.schemas.devices import (
    DeviceCreate,
    DevicePage,
    DeviceRead,
    DeviceUpdate,
)
from app.services.devices import (
    DeviceNotFoundError,
    DeviceService,
    DuplicateDeviceError,
    HostOutsideLabError,
)


router = APIRouter(prefix="/devices", tags=["devices"])
ServiceDependency = Annotated[DeviceService, Depends(get_device_service)]


def translate_service_error(error: Exception) -> HTTPException:
    """Map expected domain failures to stable HTTP responses."""
    if isinstance(error, DeviceNotFoundError):
        return HTTPException(status_code=404, detail=str(error))
    if isinstance(error, DuplicateDeviceError):
        return HTTPException(status_code=409, detail=str(error))
    if isinstance(error, HostOutsideLabError):
        return HTTPException(status_code=422, detail=str(error))
    raise error


@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def create_device(payload: DeviceCreate, service: ServiceDependency) -> DeviceRead:
    try:
        return DeviceRead.model_validate(service.create(payload))
    except (DuplicateDeviceError, HostOutsideLabError) as error:
        raise translate_service_error(error) from error


@router.get("", response_model=DevicePage)
def list_devices(
    service: ServiceDependency,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    site: str | None = None,
) -> DevicePage:
    items, total = service.list(offset=offset, limit=limit, site=site)
    return DevicePage(
        items=[DeviceRead.model_validate(item) for item in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{device_id}", response_model=DeviceRead)
def get_device(device_id: int, service: ServiceDependency) -> DeviceRead:
    try:
        return DeviceRead.model_validate(service.get(device_id))
    except DeviceNotFoundError as error:
        raise translate_service_error(error) from error


@router.patch("/{device_id}", response_model=DeviceRead)
def update_device(
    device_id: int,
    payload: DeviceUpdate,
    service: ServiceDependency,
) -> DeviceRead:
    try:
        return DeviceRead.model_validate(service.update(device_id, payload))
    except (
        DeviceNotFoundError,
        DuplicateDeviceError,
        HostOutsideLabError,
    ) as error:
        raise translate_service_error(error) from error


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: int, service: ServiceDependency) -> Response:
    try:
        service.delete(device_id)
    except DeviceNotFoundError as error:
        raise translate_service_error(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)

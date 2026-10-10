from __future__ import annotations

from datetime import datetime
from ipaddress import ip_address
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeviceFields(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    host: str
    port: int = Field(default=22, ge=1, le=65535)
    device_type: Literal["cisco_ios"] = "cisco_ios"
    username: str = Field(min_length=1, max_length=120)
    site: str | None = Field(default=None, max_length=120)
    is_active: bool = True

    @field_validator("host")
    @classmethod
    def normalize_host(cls, value: str) -> str:
        return str(ip_address(value))


class DeviceCreate(DeviceFields):
    password: str = Field(min_length=1, max_length=512)
    secret: str | None = Field(default=None, max_length=512)


class DeviceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    host: str | None = None
    port: int | None = Field(default=None, ge=1, le=65535)
    device_type: Literal["cisco_ios"] | None = None
    username: str | None = Field(default=None, min_length=1, max_length=120)
    password: str | None = Field(default=None, min_length=1, max_length=512)
    secret: str | None = Field(default=None, max_length=512)
    site: str | None = Field(default=None, max_length=120)
    is_active: bool | None = None

    @field_validator("host")
    @classmethod
    def normalize_host(cls, value: str | None) -> str | None:
        return str(ip_address(value)) if value is not None else None


class DeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    host: str
    port: int
    device_type: str
    username: str
    site: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DevicePage(BaseModel):
    items: list[DeviceRead]
    total: int
    offset: int
    limit: int

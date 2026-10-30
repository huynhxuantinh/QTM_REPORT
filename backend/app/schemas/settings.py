from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SystemSettingPayload(BaseModel):
    cpu_warning_percent: float = Field(ge=0, le=100)
    cpu_critical_percent: float = Field(ge=0, le=100)
    ram_warning_percent: float = Field(ge=0, le=100)
    ram_critical_percent: float = Field(ge=0, le=100)
    packet_loss_warning_percent: float = Field(ge=0, le=100)
    packet_loss_critical_percent: float = Field(ge=0, le=100)
    latency_warning_ms: float = Field(ge=0)
    latency_critical_ms: float = Field(ge=0)
    scheduler_interval_minutes: int = Field(ge=1, le=1440)
    scheduler_cooldown_seconds: int = Field(ge=1, le=300)
    max_concurrent_checks: int = Field(ge=1, le=10)

    @model_validator(mode="after")
    def validate_threshold_order(self) -> "SystemSettingPayload":
        pairs = (
            (self.cpu_warning_percent, self.cpu_critical_percent, "CPU"),
            (self.ram_warning_percent, self.ram_critical_percent, "RAM"),
            (
                self.packet_loss_warning_percent,
                self.packet_loss_critical_percent,
                "packet loss",
            ),
            (self.latency_warning_ms, self.latency_critical_ms, "latency"),
        )
        for warning, critical, name in pairs:
            if warning >= critical:
                raise ValueError(f"{name} warning threshold must be below critical")
        return self


class SystemSettingRead(SystemSettingPayload):
    model_config = ConfigDict(from_attributes=True)

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CheckAccepted(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    execution_status: str
    started_at: datetime


class InterfaceResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    ip_address: str
    status: str
    protocol: str
    input_packets: int
    output_packets: int
    input_bytes: int
    output_bytes: int
    input_packets_per_second: float | None
    output_packets_per_second: float | None
    input_bytes_per_second: float | None
    output_bytes_per_second: float | None
    input_errors: int
    crc_errors: int
    output_errors: int
    output_drops: int


class PingResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_type: str
    target: str
    packet_loss_percent: float
    latency_min_ms: float | None
    latency_avg_ms: float | None
    latency_max_ms: float | None


class FindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    severity: str
    metric: str
    message: str


class HealthCheckRead(CheckAccepted):
    execution_status: str
    overall_status: str | None
    finished_at: datetime | None
    checked_at: datetime | None
    ssh_ok: bool | None
    uptime_seconds: int | None
    cpu_percent: float | None
    ram_percent: float | None
    memory_total_bytes: int | None
    memory_used_bytes: int | None
    memory_free_bytes: int | None
    error: str | None
    interfaces: list[InterfaceResultRead]
    pings: list[PingResultRead]
    findings: list[FindingRead]


class HealthCheckPage(BaseModel):
    items: list[HealthCheckRead]
    total: int
    offset: int
    limit: int

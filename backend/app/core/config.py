from __future__ import annotations

from functools import cached_property
from ipaddress import IPv4Network, IPv6Network, ip_network

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables or a local .env file."""

    app_name: str = "Network Health Check API"
    database_url: str = "sqlite+pysqlite:///./network_health.db"
    credential_key: str = ""
    lab_cidrs: str = "192.168.141.0/24,192.168.91.0/24"
    cors_origins: str = "http://localhost:3000"
    scheduler_enabled: bool = False
    scheduler_interval_minutes: int = Field(default=15, ge=1)
    scheduler_cooldown_seconds: int = Field(default=5, ge=1, le=300)
    max_concurrent_checks: int = Field(default=3, ge=1, le=10)
    auth_enabled: bool = False
    jwt_secret: str = "development-only-change-me"
    access_token_minutes: int = Field(default=480, ge=5, le=1440)
    admin_username: str = "admin"
    admin_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @cached_property
    def lab_networks(self) -> tuple[IPv4Network | IPv6Network, ...]:
        return tuple(
            ip_network(value.strip(), strict=False)
            for value in self.lab_cidrs.split(",")
            if value.strip()
        )

    @property
    def allowed_origins(self) -> list[str]:
        return [
            value.strip()
            for value in self.cors_origins.split(",")
            if value.strip()
        ]

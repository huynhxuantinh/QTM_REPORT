from __future__ import annotations

from ipaddress import IPv4Network, IPv6Network, ip_address

from app.core.security import CredentialCipher
from app.db.models.device import Device
from app.repositories.devices import DeviceRepository
from app.schemas.devices import DeviceCreate, DeviceUpdate


class DeviceNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("Device not found")


class DuplicateDeviceError(Exception):
    def __init__(self) -> None:
        super().__init__("An active device already uses this host and port")


class HostOutsideLabError(Exception):
    def __init__(self) -> None:
        super().__init__("Host is outside configured lab CIDRs")


class DeviceService:
    """Validate device rules and protect credentials around persistence."""

    def __init__(
        self,
        *,
        repository: DeviceRepository,
        cipher: CredentialCipher,
        lab_networks: tuple[IPv4Network | IPv6Network, ...],
    ) -> None:
        self._repository = repository
        self._cipher = cipher
        self._lab_networks = lab_networks

    def create(self, payload: DeviceCreate) -> Device:
        self._validate_host(payload.host)
        self._ensure_unique(payload.host, payload.port)
        device = Device(
            name=payload.name,
            host=payload.host,
            port=payload.port,
            device_type=payload.device_type,
            username=payload.username,
            encrypted_password=self._cipher.encrypt(payload.password),
            encrypted_secret=(
                self._cipher.encrypt(payload.secret) if payload.secret else None
            ),
            site=payload.site,
            is_active=payload.is_active,
        )
        return self._repository.create(device)

    def get(self, device_id: int) -> Device:
        device = self._repository.get(device_id)
        if device is None:
            raise DeviceNotFoundError
        return device

    def list(
        self,
        *,
        offset: int,
        limit: int,
        site: str | None,
    ) -> tuple[list[Device], int]:
        return self._repository.list(offset=offset, limit=limit, site=site)

    def update(self, device_id: int, payload: DeviceUpdate) -> Device:
        device = self.get(device_id)
        changes = payload.model_dump(exclude_unset=True)
        candidate_host = changes.get("host", device.host)
        candidate_port = changes.get("port", device.port)
        self._validate_host(candidate_host)
        duplicate = self._repository.find_by_host_port(
            candidate_host, candidate_port
        )
        if duplicate is not None and duplicate.id != device.id:
            raise DuplicateDeviceError

        password = changes.pop("password", None)
        secret_supplied = "secret" in changes
        secret = changes.pop("secret", None)
        for field_name, value in changes.items():
            setattr(device, field_name, value)
        if password is not None:
            device.encrypted_password = self._cipher.encrypt(password)
        if secret_supplied:
            device.encrypted_secret = (
                self._cipher.encrypt(secret) if secret else None
            )
        return self._repository.save(device)

    def delete(self, device_id: int) -> None:
        self._repository.soft_delete(self.get(device_id))

    def _validate_host(self, host: str) -> None:
        address = ip_address(host)
        if not any(address in network for network in self._lab_networks):
            raise HostOutsideLabError

    def _ensure_unique(self, host: str, port: int) -> None:
        if self._repository.find_by_host_port(host, port) is not None:
            raise DuplicateDeviceError

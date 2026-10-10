from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.models.user import User
from app.repositories.users import UserRepository


class InvalidCredentialsError(Exception):
    pass


def authenticate(
    session: Session,
    settings: Settings,
    username: str,
    password: str,
) -> str:
    user = UserRepository(session).find_by_username(username)
    if (
        user is None
        or not user.is_active
        or not verify_password(password, user.password_hash)
    ):
        raise InvalidCredentialsError("Invalid username or password")
    return create_access_token(
        user.username,
        settings.jwt_secret,
        settings.access_token_minutes,
    )


def ensure_admin_account(session: Session, settings: Settings) -> None:
    if not settings.auth_enabled:
        return
    if not settings.admin_password:
        raise RuntimeError("ADMIN_PASSWORD must be configured when auth is enabled")
    if settings.jwt_secret == "development-only-change-me":
        raise RuntimeError("JWT_SECRET must be changed when auth is enabled")
    repository = UserRepository(session)
    if repository.find_by_username(settings.admin_username) is None:
        repository.create(
            User(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
                is_active=True,
            )
        )

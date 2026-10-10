from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_username(self, username: str) -> User | None:
        return self._session.scalar(
            select(User).where(User.username == username)
        )

    def create(self, user: User) -> User:
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

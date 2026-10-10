from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db


router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    """Confirm that the API and its database connection are healthy."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}

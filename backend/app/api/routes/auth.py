from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_settings
from app.core.config import Settings
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import InvalidCredentialsError, authenticate


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    try:
        token = authenticate(
            db, settings, payload.username, payload.password
        )
    except InvalidCredentialsError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_minutes * 60,
    )

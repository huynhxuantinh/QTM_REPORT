from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import DashboardSummaryRead
from app.services.dashboard import DashboardService


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryRead)
def get_dashboard_summary(
    db: Annotated[Session, Depends(get_db)],
) -> DashboardSummaryRead:
    return DashboardSummaryRead.model_validate(
        DashboardService(db).summary()
    )

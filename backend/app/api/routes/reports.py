from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.reports import ReportService


router = APIRouter(prefix="/reports", tags=["reports"])


def report_filters(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    device_id: Annotated[int | None, Query(ge=1)] = None,
    site: str | None = None,
    status: Literal["Healthy", "Warning", "Critical"] | None = None,
) -> dict[str, object]:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="date_from must be before date_to")
    return {
        "date_from": date_from,
        "date_to": date_to,
        "device_id": device_id,
        "site": site,
        "status": status,
    }


FilterDependency = Annotated[dict[str, object], Depends(report_filters)]


@router.get("/csv")
def download_csv(
    filters: FilterDependency,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    service = ReportService(db)
    content = service.build_csv(service.rows(**filters))
    return _download(content, "text/csv; charset=utf-8", "csv")


@router.get("/pdf")
def download_pdf(
    filters: FilterDependency,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    service = ReportService(db)
    content = service.build_pdf(service.rows(**filters))
    return _download(content, "application/pdf", "pdf")


def _download(content: bytes, media_type: str, extension: str) -> Response:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="network-health-{stamp}.{extension}"'
            )
        },
    )

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.reports import ReportService, ReportTooLargeError


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
    content = service.build_csv(_report_rows(service, filters))
    return _download(content, "text/csv; charset=utf-8", "csv")


@router.get("/pdf")
def download_pdf(
    filters: FilterDependency,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    service = ReportService(db)
    content = service.build_pdf(
        _report_rows(service, filters),
        date_from=filters.get("date_from"),
        date_to=filters.get("date_to"),
    )
    return _download(content, "application/pdf", "pdf")


@router.get("/xlsx")
def download_xlsx(
    filters: FilterDependency,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    service = ReportService(db)
    content = service.build_xlsx(
        _report_rows(service, filters),
        date_from=filters.get("date_from"),
        date_to=filters.get("date_to"),
    )
    return _download(
        content,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xlsx",
    )


def _report_rows(
    service: ReportService,
    filters: dict[str, object],
):
    try:
        return service.rows(**filters)
    except ReportTooLargeError as error:
        raise HTTPException(
            status_code=413,
            detail=(
                f"Báo cáo có {error.count} lần kiểm tra, vượt giới hạn "
                f"{error.limit}; hãy thu hẹp khoảng thời gian hoặc chọn "
                "một thiết bị."
            ),
        ) from error
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

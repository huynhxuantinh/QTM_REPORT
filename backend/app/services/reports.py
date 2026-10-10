from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.device import Device
from app.db.models.health_check import HealthCheck


@dataclass(slots=True)
class ReportRow:
    device_id: int
    device_name: str
    site: str
    latest_status: str
    checks_count: int
    cpu_avg: float | None
    cpu_max: float | None
    ram_avg: float | None
    ram_max: float | None
    loss_avg: float | None
    loss_max: float | None
    latency_avg: float | None
    latency_max: float | None
    warning_findings: int
    critical_findings: int


class ReportService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def rows(
        self,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        device_id: int | None = None,
        site: str | None = None,
        status: str | None = None,
    ) -> list[ReportRow]:
        filters = [
            Device.deleted_at.is_(None),
            HealthCheck.execution_status == "succeeded",
        ]
        if date_from is not None:
            filters.append(HealthCheck.started_at >= date_from)
        if date_to is not None:
            filters.append(HealthCheck.started_at <= date_to)
        if device_id is not None:
            filters.append(Device.id == device_id)
        if site is not None:
            filters.append(Device.site == site)
        if status is not None:
            filters.append(HealthCheck.overall_status == status)

        records = self._session.execute(
            select(Device, HealthCheck)
            .join(HealthCheck, HealthCheck.device_id == Device.id)
            .where(*filters)
            .options(
                selectinload(HealthCheck.pings),
                selectinload(HealthCheck.findings),
            )
            .order_by(Device.id, HealthCheck.started_at, HealthCheck.id)
        ).all()
        grouped: dict[int, tuple[Device, list[HealthCheck]]] = {}
        for device, check in records:
            grouped.setdefault(device.id, (device, []))[1].append(check)

        result: list[ReportRow] = []
        for device, checks in grouped.values():
            cpu_values = [x.cpu_percent for x in checks if x.cpu_percent is not None]
            ram_values = [x.ram_percent for x in checks if x.ram_percent is not None]
            path_pings = [
                ping
                for check in checks
                for ping in check.pings
                if ping.source_type == "device"
            ]
            losses = [ping.packet_loss_percent for ping in path_pings]
            latencies = [
                ping.latency_avg_ms
                for ping in path_pings
                if ping.latency_avg_ms is not None
            ]
            findings = [item for check in checks for item in check.findings]
            result.append(
                ReportRow(
                    device_id=device.id,
                    device_name=device.name,
                    site=device.site or "",
                    latest_status=checks[-1].overall_status or "Unknown",
                    checks_count=len(checks),
                    cpu_avg=_average(cpu_values),
                    cpu_max=max(cpu_values, default=None),
                    ram_avg=_average(ram_values),
                    ram_max=max(ram_values, default=None),
                    loss_avg=_average(losses),
                    loss_max=max(losses, default=None),
                    latency_avg=_average(latencies),
                    latency_max=max(latencies, default=None),
                    warning_findings=sum(
                        item.severity == "Warning" for item in findings
                    ),
                    critical_findings=sum(
                        item.severity == "Critical" for item in findings
                    ),
                )
            )
        return result

    @staticmethod
    def build_csv(rows: list[ReportRow]) -> bytes:
        stream = io.StringIO(newline="")
        writer = csv.writer(stream)
        writer.writerow(
            [
                "Device ID",
                "Device Name",
                "Site",
                "Latest Status",
                "Checks",
                "CPU Avg (%)",
                "CPU Max (%)",
                "RAM Avg (%)",
                "RAM Max (%)",
                "Loss Avg (%)",
                "Loss Max (%)",
                "Latency Avg (ms)",
                "Latency Max (ms)",
                "Warning Findings",
                "Critical Findings",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.device_id,
                    _safe_csv(row.device_name),
                    _safe_csv(row.site),
                    row.latest_status,
                    row.checks_count,
                    _display(row.cpu_avg),
                    _display(row.cpu_max),
                    _display(row.ram_avg),
                    _display(row.ram_max),
                    _display(row.loss_avg),
                    _display(row.loss_max),
                    _display(row.latency_avg),
                    _display(row.latency_max),
                    row.warning_findings,
                    row.critical_findings,
                ]
            )
        return b"\xef\xbb\xbf" + stream.getvalue().encode("utf-8")

    @staticmethod
    def build_pdf(rows: list[ReportRow]) -> bytes:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        font_name = "Helvetica"
        font_paths = (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/arial.ttf",
        )
        for path in font_paths:
            if Path(path).is_file():
                pdfmetrics.registerFont(TTFont("ReportFont", path))
                font_name = "ReportFont"
                break

        output = io.BytesIO()
        document = SimpleDocTemplate(
            output,
            pagesize=landscape(A4),
            leftMargin=10 * mm,
            rightMargin=10 * mm,
            topMargin=10 * mm,
            bottomMargin=10 * mm,
            title="Bao cao suc khoe he thong mang",
        )
        styles = getSampleStyleSheet()
        styles["Title"].fontName = font_name
        styles["Normal"].fontName = font_name
        story = [
            Paragraph("Báo cáo sức khỏe hệ thống mạng", styles["Title"]),
            Paragraph(
                f"Thời điểm xuất: {datetime.now(timezone.utc).isoformat()}",
                styles["Normal"],
            ),
            Spacer(1, 6 * mm),
        ]
        data = [
            [
                "Thiết bị",
                "Trạng thái",
                "Số lần",
                "CPU TB/Max",
                "RAM TB/Max",
                "Loss TB/Max",
                "Latency TB/Max",
                "W/C",
            ]
        ]
        for row in rows:
            data.append(
                [
                    row.device_name,
                    row.latest_status,
                    str(row.checks_count),
                    f"{_display(row.cpu_avg)}/{_display(row.cpu_max)}",
                    f"{_display(row.ram_avg)}/{_display(row.ram_max)}",
                    f"{_display(row.loss_avg)}/{_display(row.loss_max)}",
                    f"{_display(row.latency_avg)}/{_display(row.latency_max)}",
                    f"{row.warning_findings}/{row.critical_findings}",
                ]
            )
        if len(data) == 1:
            data.append(["Không có dữ liệu", "", "", "", "", "", "", ""])
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF3F8")]),
                ]
            )
        )
        story.append(table)
        document.build(story)
        return output.getvalue()


def _average(values: list[float]) -> float | None:
    return round(fmean(values), 2) if values else None


def _display(value: float | None) -> str:
    return "" if value is None else f"{value:.2f}"


def _safe_csv(value: str) -> str:
    return f"'{value}" if value.startswith(("=", "+", "-", "@")) else value

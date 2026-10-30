from __future__ import annotations

from contextlib import asynccontextmanager
import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_settings, require_admin
from app.api.routes import (
    auth,
    checks,
    dashboard,
    devices,
    health,
    reports,
    settings as settings_routes,
)
from app.core.config import Settings
from app.db.session import SessionLocal
from app.services.auth import ensure_admin_account
from app.repositories.settings import SystemSettingRepository
from app.services.scheduler import build_scheduler
from app.services.startup_recovery import recover_interrupted_work
from app.services.retention import (
    HistoryRetentionScheduler,
    HistoryRetentionService,
)


logger = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    *,
    session_factory: sessionmaker[Session] | None = None,
) -> FastAPI:
    """Create the FastAPI application and register versioned routes."""
    resolved_settings = settings or get_settings()
    resolved_session_factory = session_factory or SessionLocal
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        scheduler = None
        retention_scheduler = None
        with resolved_session_factory() as session:
            recovered_scans, recovered_checks = recover_interrupted_work(
                session
            )
        if recovered_scans or recovered_checks:
            logger.warning(
                "Recovered interrupted work after backend restart",
                extra={
                    "recovered_scans": recovered_scans,
                    "recovered_checks": recovered_checks,
                },
            )
        if resolved_settings.auth_enabled:
            with resolved_session_factory() as session:
                ensure_admin_account(session, resolved_settings)
        if resolved_settings.scheduler_enabled:
            with resolved_session_factory() as session:
                stored = SystemSettingRepository(session).get_or_create()
            scheduler_settings = resolved_settings.model_copy(
                update={
                    "scheduler_interval_minutes": (
                        stored.scheduler_interval_minutes
                    ),
                    "scheduler_cooldown_seconds": (
                        stored.scheduler_cooldown_seconds
                    ),
                    "max_concurrent_checks": stored.max_concurrent_checks,
                }
            )
            scheduler = build_scheduler(scheduler_settings)
            scheduler.start()
            application.state.scheduler = scheduler
        if resolved_settings.data_retention_enabled:
            def cleanup_history() -> None:
                with resolved_session_factory() as session:
                    result = HistoryRetentionService(session).prune(
                        retention_days=resolved_settings.data_retention_days
                    )
                if result.deleted_checks or result.deleted_scans:
                    logger.info(
                        "Pruned expired monitoring history",
                        extra={
                            "deleted_checks": result.deleted_checks,
                            "deleted_scans": result.deleted_scans,
                        },
                    )

            retention_scheduler = HistoryRetentionScheduler(cleanup_history)
            retention_scheduler.start()
            application.state.retention_scheduler = retention_scheduler
        yield
        if scheduler is not None:
            scheduler.shutdown(wait=False)
        if retention_scheduler is not None:
            retention_scheduler.shutdown(wait=False)

    application = FastAPI(
        title=resolved_settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    application.include_router(health.router, prefix="/api/v1")
    application.include_router(auth.router, prefix="/api/v1")
    protected = [Depends(require_admin)]
    application.include_router(
        devices.router, prefix="/api/v1", dependencies=protected
    )
    application.include_router(
        checks.router, prefix="/api/v1", dependencies=protected
    )
    application.include_router(
        dashboard.router, prefix="/api/v1", dependencies=protected
    )
    application.include_router(
        reports.router, prefix="/api/v1", dependencies=protected
    )
    application.include_router(
        settings_routes.router, prefix="/api/v1", dependencies=protected
    )
    return application


app = create_app()

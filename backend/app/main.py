from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import get_settings
from app.api.routes import checks, devices, health
from app.core.config import Settings
from app.services.scheduler import build_scheduler


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the FastAPI application and register versioned routes."""
    resolved_settings = settings or get_settings()
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        scheduler = None
        if resolved_settings.scheduler_enabled:
            scheduler = build_scheduler(resolved_settings)
            scheduler.start()
            application.state.scheduler = scheduler
        yield
        if scheduler is not None:
            scheduler.shutdown(wait=False)

    application = FastAPI(
        title=resolved_settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    application.include_router(health.router, prefix="/api/v1")
    application.include_router(devices.router, prefix="/api/v1")
    application.include_router(checks.router, prefix="/api/v1")
    return application


app = create_app()

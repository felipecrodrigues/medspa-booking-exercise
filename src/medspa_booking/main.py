"""FastAPI application composition and shared HTTP error mapping."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.engine import Engine

import medspa_booking.db.metadata  # noqa: F401
from medspa_booking.appointments.router import router as appointment_router
from medspa_booking.db.engine import make_engine, make_session_factory
from medspa_booking.errors import (
    InvalidServiceSelectionError,
    ResourceNotFoundError,
)
from medspa_booking.health import router as health_router
from medspa_booking.services.router import router as service_router


def create_app(
    *,
    engine: Engine | None = None,
    database_url: str | None = None,
) -> FastAPI:
    """Build an app with its own engine, or a caller-provided engine for tests."""
    owns_engine = engine is None
    database_engine = engine or make_engine(database_url)
    session_factory = make_session_factory(database_engine)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            if owns_engine:
                database_engine.dispose()

    app = FastAPI(title="Medspa Booking API", lifespan=lifespan)
    app.state.engine = database_engine
    app.state.session_factory = session_factory

    @app.exception_handler(ResourceNotFoundError)
    async def resource_not_found(
        _: Request,
        exc: ResourceNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(InvalidServiceSelectionError)
    async def invalid_service_selection(
        _: Request,
        exc: InvalidServiceSelectionError,
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    app.include_router(health_router)
    app.include_router(service_router)
    app.include_router(appointment_router)
    return app


app = create_app()

__all__ = ["app", "create_app"]

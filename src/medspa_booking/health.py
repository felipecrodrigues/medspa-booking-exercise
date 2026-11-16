"""Database-aware infrastructure readiness endpoint."""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from medspa_booking.dependencies import SessionDep

router = APIRouter(tags=["health"])


@router.get("/health")
def health(session: SessionDep) -> dict[str, str]:
    """Return readiness only when the configured database is reachable."""
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(
            status_code=503,
            detail="database unavailable",
        ) from exc
    return {"status": "ok", "database": "ok"}


__all__ = ["router"]

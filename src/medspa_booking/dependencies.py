"""FastAPI dependencies shared by the health and feature routers."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Path, Request
from sqlalchemy.orm import Session, sessionmaker

from medspa_booking.db.limits import MAX_POSTGRES_INTEGER

PathId = Annotated[int, Path(gt=0, le=MAX_POSTGRES_INTEGER)]


def get_session(request: Request) -> Iterator[Session]:
    """Yield one SQLAlchemy session for an HTTP request."""
    session_factory: sessionmaker[Session] = request.app.state.session_factory
    session = session_factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]

__all__ = ["PathId", "SessionDep", "get_session"]

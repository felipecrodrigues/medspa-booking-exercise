"""SQLAlchemy engine and session-factory construction."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_DATABASE_URL = "postgresql+psycopg://booking:booking@localhost:5432/medspa_booking"


def make_engine(database_url: str | None = None) -> Engine:
    """Create a PostgreSQL engine using the explicit URL or runtime environment."""
    return create_engine(
        database_url or os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL),
        pool_pre_ping=True,
    )


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Build the synchronous request session factory for an engine."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


__all__ = ["DEFAULT_DATABASE_URL", "make_engine", "make_session_factory"]

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from medspa_booking.main import create_app


def test_health_returns_503_when_database_is_unreachable() -> None:
    engine = create_engine(
        "postgresql+psycopg://booking:booking@127.0.0.1:1/unreachable",
        connect_args={"connect_timeout": 1},
    )
    try:
        with TestClient(create_app(engine=engine)) as client:
            response = client.get("/health")
    finally:
        engine.dispose()

    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="set TEST_DATABASE_URL to run PostgreSQL integration checks",
)
def test_health_reports_ready_when_postgresql_is_reachable() -> None:
    database_url = os.environ["TEST_DATABASE_URL"]
    engine: Engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT 1")) == 1
        with TestClient(create_app(engine=engine)) as client:
            response = client.get("/health")
    finally:
        engine.dispose()

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}

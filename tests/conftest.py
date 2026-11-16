from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic.config import Config
from db_url_safety import validate_test_database_url
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from medspa_booking.db.seed import seed_demo_data
from medspa_booking.main import create_app
from medspa_booking.medspas.models import Medspa
from medspa_booking.services.models import Service

ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="session")
def postgres_engine() -> Iterator[Engine]:
    database_url = os.getenv("TEST_DATABASE_URL")
    if database_url is None:
        pytest.skip("set TEST_DATABASE_URL to run PostgreSQL integration tests")

    url = validate_test_database_url(database_url)

    engine = create_engine(url, pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP SCHEMA public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))

        config = Config(str(ROOT / "alembic.ini"))
        config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
        command.upgrade(config, "head")
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def clean_postgres(postgres_engine: Engine) -> None:
    with postgres_engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE appointment_services, appointments, services, medspas "
                "RESTART IDENTITY CASCADE"
            )
        )


@pytest.fixture
def session_factory(
    postgres_engine: Engine,
    clean_postgres: None,
) -> sessionmaker[Session]:
    return sessionmaker(bind=postgres_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def second_medspa_with_service(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory.begin() as session:
        session.add(
            Medspa(
                id=2,
                name="Other Medspa",
                address="200 Example Road",
                phone_number="+1-555-0200",
                email="other@example.test",
            )
        )
        session.add(
            Service(
                id=99,
                medspa_id=2,
                name="Other Service",
                price=1000,
                duration=45,
            )
        )


@pytest.fixture
def api_client(
    postgres_engine: Engine,
    clean_postgres: None,
) -> Iterator[TestClient]:
    seed_demo_data(postgres_engine)
    with TestClient(
        create_app(engine=postgres_engine),
        raise_server_exceptions=False,
    ) as client:
        yield client

from __future__ import annotations

import os
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.util import CommandError
from sqlalchemy import CheckConstraint, inspect
from sqlalchemy.engine import Engine

from alembic import command
from medspa_booking.db.metadata import Base

ROOT = Path(__file__).parents[1]


def test_alembic_schema_matches_runtime_metadata(
    monkeypatch: pytest.MonkeyPatch,
    postgres_engine: Engine,
) -> None:
    monkeypatch.setenv("DATABASE_URL", os.environ["TEST_DATABASE_URL"])
    config = Config(str(ROOT / "alembic.ini"))

    command.check(config)


def test_explicit_alembic_config_url_precedes_database_url(
    monkeypatch: pytest.MonkeyPatch,
    postgres_engine: Engine,
) -> None:
    database_url = os.environ["TEST_DATABASE_URL"]
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://booking:booking@127.0.0.1:1/unreachable",
    )
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

    command.check(config)


def test_postgresql_named_check_constraints_match_metadata(
    postgres_engine: Engine,
) -> None:
    inspector = inspect(postgres_engine)
    expected = {
        (table.name, constraint.name)
        for table in Base.metadata.tables.values()
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint) and constraint.name is not None
    }
    actual = {
        (table_name, constraint["name"])
        for table_name in Base.metadata.tables
        for constraint in inspector.get_check_constraints(table_name, schema="public")
        if constraint["name"] is not None
    }

    assert expected
    assert actual == expected


def test_alembic_check_detects_server_default_drift(
    monkeypatch: pytest.MonkeyPatch,
    postgres_engine: Engine,
) -> None:
    database_url = os.environ["TEST_DATABASE_URL"]
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config(str(ROOT / "alembic.ini"))

    with postgres_engine.begin() as connection:
        connection.exec_driver_sql(
            "ALTER TABLE appointments ALTER COLUMN status SET DEFAULT 'pending'"
        )

    try:
        with pytest.raises(CommandError, match="New upgrade operations detected"):
            command.check(config)
    finally:
        with postgres_engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE appointments ALTER COLUMN status SET DEFAULT 'scheduled'"
            )

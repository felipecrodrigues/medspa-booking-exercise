from pathlib import Path

from medspa_booking.db.metadata import Base
from medspa_booking.db.schema_ddl import render_schema


def test_metadata_contains_only_the_booking_tables() -> None:
    assert set(Base.metadata.tables) == {
        "medspas",
        "services",
        "appointments",
        "appointment_services",
    }


def test_reviewable_postgresql_ddl_matches_runtime_metadata() -> None:
    schema_file = Path(__file__).parents[1] / "sql" / "schema.sql"

    assert schema_file.read_text(encoding="utf-8") == render_schema()

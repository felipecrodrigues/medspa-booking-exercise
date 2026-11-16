"""Generate reviewable PostgreSQL DDL from the registered SQLAlchemy metadata."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from medspa_booking.db.metadata import Base

HEADER = "-- Generated from medspa_booking.db.metadata; do not edit by hand.\n"


def render_schema() -> str:
    """Return the PostgreSQL CREATE TABLE and index statements."""
    dialect = postgresql.dialect()
    statements: list[str] = []

    for table in Base.metadata.sorted_tables:
        statements.append(f"{CreateTable(table).compile(dialect=dialect).string.strip()};")
        for index in sorted(table.indexes, key=lambda item: item.name or ""):
            statements.append(f"{CreateIndex(index).compile(dialect=dialect).string.strip()};")

    return HEADER + "\n\n".join(statements) + "\n"


def main() -> None:
    """Write generated DDL to the repository's reviewable SQL file."""
    repository_root = Path(__file__).parents[3]
    schema_path = repository_root / "sql" / "schema.sql"
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_text(render_schema(), encoding="utf-8")


if __name__ == "__main__":
    main()

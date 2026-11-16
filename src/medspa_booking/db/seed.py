"""Seed deterministic local demo data without overwriting existing rows."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from medspa_booking.db.engine import make_engine
from medspa_booking.db.metadata import Medspa, Service


@dataclass(frozen=True, slots=True, kw_only=True)
class DemoService:
    id: int
    name: str
    description: str
    price: int
    duration: int


DEMO_MEDSPA_ID = 1
DEMO_SERVICES: tuple[DemoService, ...] = (
    DemoService(
        id=1,
        name="Initial Consultation",
        description="A sample first visit.",
        price=0,
        duration=30,
    ),
    DemoService(
        id=2,
        name="Rejuvenating Facial",
        description="A sample facial service.",
        price=12500,
        duration=60,
    ),
)


def seed_demo_data(engine: Engine) -> None:
    """Insert the documented medspa and example services when their IDs are free."""
    with Session(engine) as session, session.begin():
        if session.get(Medspa, DEMO_MEDSPA_ID) is None:
            session.add(
                Medspa(
                    id=DEMO_MEDSPA_ID,
                    name="Moxie Demo Medspa",
                    address="100 Demo Avenue, Austin, TX",
                    phone_number="+1-555-0100",
                    email="hello@example.test",
                )
            )

        for demo_service in DEMO_SERVICES:
            if session.get(Service, demo_service.id) is None:
                session.add(
                    Service(
                        id=demo_service.id,
                        medspa_id=DEMO_MEDSPA_ID,
                        name=demo_service.name,
                        description=demo_service.description,
                        price=demo_service.price,
                        duration=demo_service.duration,
                    )
                )

    _advance_identity_sequences(engine)


def _advance_identity_sequences(engine: Engine) -> None:
    """Keep generated IDs beyond the fixed IDs used for demo rows."""
    for table_name in ("medspas", "services"):
        statement = text(
            f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), "
            f"COALESCE((SELECT MAX(id) FROM {table_name}), 1), true)"
        )
        with engine.begin() as connection:
            connection.execute(statement)


def main() -> None:
    """Run the repeatable seed command against the configured database."""
    engine = make_engine()
    try:
        seed_demo_data(engine)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()

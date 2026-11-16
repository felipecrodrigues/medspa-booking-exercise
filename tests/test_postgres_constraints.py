from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from medspa_booking.appointments.models import (
    Appointment,
    AppointmentService,
)
from medspa_booking.db.seed import seed_demo_data
from medspa_booking.main import create_app
from medspa_booking.services.models import Service


@pytest.mark.parametrize(
    ("name", "price", "duration"),
    [
        ("", 100, 30),
        (" \t", 100, 30),
        ("Negative price", -1, 30),
        ("Zero duration", 100, 0),
    ],
)
def test_postgresql_enforces_service_check_constraints(
    postgres_engine: Engine,
    clean_postgres: None,
    name: str,
    price: int,
    duration: int,
) -> None:
    seed_demo_data(postgres_engine)

    with pytest.raises(IntegrityError):
        with postgres_engine.begin() as connection:
            connection.execute(
                insert(Service).values(
                    medspa_id=1,
                    name=name,
                    description=None,
                    price=price,
                    duration=duration,
                )
            )


def test_postgresql_enforces_appointment_and_snapshot_check_constraints(
    postgres_engine: Engine,
    clean_postgres: None,
) -> None:
    seed_demo_data(postgres_engine)
    start_time = datetime.now(UTC) + timedelta(days=1)
    with postgres_engine.begin() as connection:
        appointment_id = connection.execute(
            insert(Appointment)
            .values(medspa_id=1, start_time=start_time, status="scheduled")
            .returning(Appointment.id)
        ).scalar_one()

    with pytest.raises(IntegrityError):
        with postgres_engine.begin() as connection:
            connection.execute(
                insert(Appointment).values(
                    medspa_id=1,
                    start_time=start_time,
                    status="pending",
                )
            )

    for snapshot in (
        {"price_at_booking": -1, "duration_at_booking": 30},
        {"price_at_booking": 100, "duration_at_booking": 0},
    ):
        with pytest.raises(IntegrityError):
            with postgres_engine.begin() as connection:
                connection.execute(
                    insert(AppointmentService).values(
                        appointment_id=appointment_id,
                        service_id=1,
                        **snapshot,
                    )
                )


def test_database_failure_during_appointment_selection_rolls_back_all_rows(
    postgres_engine: Engine,
    clean_postgres: None,
) -> None:
    seed_demo_data(postgres_engine)
    with postgres_engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE FUNCTION fail_selection_insert() RETURNS trigger "
            "LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'injected test failure'; "
            "END; $$"
        )
        connection.exec_driver_sql(
            "CREATE TRIGGER fail_selection_insert BEFORE INSERT "
            "ON appointment_services FOR EACH ROW "
            "EXECUTE FUNCTION fail_selection_insert()"
        )

    try:
        with TestClient(
            create_app(engine=postgres_engine),
            raise_server_exceptions=False,
        ) as client:
            response = client.post(
                "/medspas/1/appointments",
                json={
                    "start_time": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                    "service_ids": [1],
                },
            )

        assert response.status_code == 500
        with Session(postgres_engine) as session:
            assert session.scalar(select(Appointment.id)) is None
            assert session.scalar(select(AppointmentService.appointment_id)) is None
    finally:
        with postgres_engine.begin() as connection:
            connection.exec_driver_sql(
                "DROP TRIGGER IF EXISTS fail_selection_insert ON appointment_services"
            )
            connection.exec_driver_sql(
                "DROP FUNCTION IF EXISTS fail_selection_insert()"
            )

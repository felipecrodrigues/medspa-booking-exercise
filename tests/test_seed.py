import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from medspa_booking.db.seed import seed_demo_data
from medspa_booking.medspas.models import Medspa
from medspa_booking.services.models import Service

ROOT = Path(__file__).parents[1]


def test_demo_seed_is_deterministic_and_repeatable(
    postgres_engine: Engine,
    session_factory: sessionmaker[Session],
) -> None:
    seed_demo_data(postgres_engine)
    seed_demo_data(postgres_engine)

    with session_factory() as session:
        medspas = session.scalars(select(Medspa).order_by(Medspa.id)).all()
        services = session.scalars(select(Service).order_by(Service.id)).all()

    assert [(medspa.id, medspa.name) for medspa in medspas] == [
        (1, "Moxie Demo Medspa")
    ]
    assert [(service.id, service.medspa_id) for service in services] == [(1, 1), (2, 1)]


def test_seed_entrypoint_registers_all_models_in_a_fresh_process(
    postgres_engine: Engine,
    clean_postgres: None,
) -> None:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]

    subprocess.run(
        [sys.executable, "-m", "medspa_booking.db.seed"],
        check=True,
        cwd=ROOT,
        env=environment,
        timeout=30,
    )

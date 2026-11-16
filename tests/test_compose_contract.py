from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).parents[1]


def test_compose_waits_for_postgresql_and_checks_api_readiness() -> None:
    compose_path = ROOT / "compose.yaml"
    compose: dict[str, Any] = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    services = compose["services"]

    assert services["db"]["healthcheck"]["test"][0] == "CMD-SHELL"
    assert "pg_isready" in services["db"]["healthcheck"]["test"][1]
    assert services["api"]["depends_on"]["db"]["condition"] == "service_healthy"
    assert "/health" in " ".join(services["api"]["healthcheck"]["test"])


def test_runtime_image_targets_python_314() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "FROM python:3.14-slim" in dockerfile

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from medspa_booking.db.limits import MAX_POSTGRES_INTEGER

TOO_LARGE_ID = MAX_POSTGRES_INTEGER + 1
FUTURE_START_TIME = (datetime.now(UTC) + timedelta(days=1)).isoformat()


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "POST",
            f"/medspas/{TOO_LARGE_ID}/services",
            {"name": "New service", "price": 100, "duration": 30},
        ),
        ("GET", f"/services/{TOO_LARGE_ID}", None),
        ("GET", f"/medspas/{TOO_LARGE_ID}/services", None),
        ("PATCH", f"/services/{TOO_LARGE_ID}", {"name": "Updated"}),
        (
            "POST",
            f"/medspas/{TOO_LARGE_ID}/appointments",
            {"start_time": FUTURE_START_TIME, "service_ids": [1]},
        ),
        ("GET", f"/appointments/{TOO_LARGE_ID}", None),
        (
            "PATCH",
            f"/appointments/{TOO_LARGE_ID}",
            {"status": "scheduled"},
        ),
    ],
)
def test_all_path_ids_reject_postgres_integer_overflow(
    api_client: TestClient,
    method: str,
    path: str,
    payload: dict[str, object] | None,
) -> None:
    response = api_client.request(method, path, json=payload)

    assert response.status_code == 422


def test_service_ids_reject_postgres_integer_overflow(
    api_client: TestClient,
) -> None:
    response = api_client.post(
        "/medspas/1/appointments",
        json={"start_time": FUTURE_START_TIME, "service_ids": [TOO_LARGE_ID]},
    )

    assert response.status_code == 422
    assert api_client.get("/appointments").json() == []

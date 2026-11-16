from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient


def future_start_time() -> str:
    return (datetime.now(UTC) + timedelta(days=1)).isoformat()


def test_appointment_creation_snapshots_and_retrieval_are_stable(
    api_client: TestClient,
) -> None:
    create_response = api_client.post(
        "/medspas/1/appointments",
        json={"start_time": future_start_time(), "service_ids": [2, 1]},
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] == "scheduled"
    assert created["total_price"] == 12500
    assert created["total_duration"] == 90
    assert created["service_selections"] == [
        {"service_id": 1, "price_at_booking": 0, "duration_at_booking": 30},
        {"service_id": 2, "price_at_booking": 12500, "duration_at_booking": 60},
    ]

    catalog_update = api_client.patch(
        "/services/2",
        json={"price": 15000, "duration": 75},
    )
    assert catalog_update.status_code == 200

    get_response = api_client.get(f"/appointments/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json() == created


def test_non_utc_appointment_create_and_read_responses_agree(
    api_client: TestClient,
) -> None:
    create_response = api_client.post(
        "/medspas/1/appointments",
        json={
            "start_time": "2035-01-15T10:00:00+05:30",
            "service_ids": [1],
        },
    )
    assert create_response.status_code == 201

    appointment_id = create_response.json()["id"]
    read_response = api_client.get(f"/appointments/{appointment_id}")

    assert read_response.status_code == 200
    assert create_response.json()["start_time"] == "2035-01-15T04:30:00Z"
    assert create_response.json()["start_time"] == read_response.json()["start_time"]


def test_appointment_service_selection_errors_are_atomic(
    api_client: TestClient,
    second_medspa_with_service: None,
) -> None:
    for service_ids in ([], [1, 1], [1, 999], [1, 99]):
        response = api_client.post(
            "/medspas/1/appointments",
            json={"start_time": future_start_time(), "service_ids": service_ids},
        )
        assert response.status_code == 422

    assert api_client.get("/appointments").json() == []


@pytest.mark.parametrize(
    "start_time",
    [
        "2099-01-01T10:00:00",
        "2000-01-01T10:00:00+00:00",
    ],
)
def test_invalid_appointment_time_creates_no_records(
    api_client: TestClient,
    start_time: str,
) -> None:
    response = api_client.post(
        "/medspas/1/appointments",
        json={"start_time": start_time, "service_ids": [1]},
    )

    assert response.status_code == 422
    assert api_client.get("/appointments").json() == []


def test_status_patch_allows_free_transitions_and_empty_body_noop(
    api_client: TestClient,
) -> None:
    create_response = api_client.post(
        "/medspas/1/appointments",
        json={"start_time": future_start_time(), "service_ids": [1]},
    )
    assert create_response.status_code == 201
    appointment_id = create_response.json()["id"]

    empty_response = api_client.patch(f"/appointments/{appointment_id}", json={})
    assert empty_response.status_code == 200
    assert empty_response.json()["status"] == "scheduled"

    for status in ("completed", "canceled", "scheduled"):
        response = api_client.patch(
            f"/appointments/{appointment_id}",
            json={"status": status},
        )
        assert response.status_code == 200
        assert response.json()["status"] == status

    assert (
        api_client.patch(
            f"/appointments/{appointment_id}",
            json={"status": "pending"},
        ).status_code
        == 422
    )
    assert api_client.get(f"/appointments/{appointment_id}").json()["status"] == (
        "scheduled"
    )


def test_status_patch_rejects_null_without_changing_appointment(
    api_client: TestClient,
) -> None:
    create_response = api_client.post(
        "/medspas/1/appointments",
        json={"start_time": future_start_time(), "service_ids": [1]},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    appointment_id = created["id"]

    response = api_client.patch(
        f"/appointments/{appointment_id}",
        json={"status": None},
    )

    assert response.status_code == 422
    assert api_client.get(f"/appointments/{appointment_id}").json() == created
    assert api_client.get("/appointments").json() == [created]


@pytest.mark.parametrize("field", ["start_time", "service_ids"])
def test_appointment_create_rejects_explicit_null_required_fields_without_records(
    api_client: TestClient,
    field: str,
) -> None:
    payload: dict[str, object] = {
        "start_time": future_start_time(),
        "service_ids": [1],
    }
    payload[field] = None

    response = api_client.post("/medspas/1/appointments", json=payload)

    assert response.status_code == 422
    assert api_client.get("/appointments").json() == []


def test_appointment_create_returns_not_found_for_missing_medspa(
    api_client: TestClient,
) -> None:
    response = api_client.post(
        "/medspas/999/appointments",
        json={"start_time": future_start_time(), "service_ids": [1]},
    )

    assert response.status_code == 404
    assert api_client.get("/appointments").json() == []


def test_global_appointment_list_includes_multiple_medspas(
    api_client: TestClient,
    second_medspa_with_service: None,
) -> None:
    for medspa_id, service_id in ((1, 1), (2, 99)):
        response = api_client.post(
            f"/medspas/{medspa_id}/appointments",
            json={"start_time": future_start_time(), "service_ids": [service_id]},
        )
        assert response.status_code == 201

    list_response = api_client.get("/appointments")

    assert list_response.status_code == 200
    assert [appointment["medspa_id"] for appointment in list_response.json()] == [1, 2]


def test_appointment_patch_rejects_unknown_start_time_field(
    api_client: TestClient,
) -> None:
    response = api_client.patch(
        "/appointments/999",
        json={"start_time": future_start_time()},
    )

    assert response.status_code == 422


def test_appointment_list_is_ordered_and_missing_records_are_not_found(
    api_client: TestClient,
) -> None:
    for _ in range(2):
        response = api_client.post(
            "/medspas/1/appointments",
            json={"start_time": future_start_time(), "service_ids": [1]},
        )
        assert response.status_code == 201

    list_response = api_client.get("/appointments")
    assert list_response.status_code == 200
    assert [appointment["id"] for appointment in list_response.json()] == [1, 2]
    assert api_client.get("/appointments/999").status_code == 404
    patch_response = api_client.patch(
        "/appointments/999",
        json={"status": "completed"},
    )
    assert patch_response.status_code == 404

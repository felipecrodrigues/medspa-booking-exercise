import pytest
from fastapi.testclient import TestClient

from medspa_booking.db.limits import MAX_POSTGRES_INTEGER


def test_service_create_get_and_list_routes(api_client: TestClient) -> None:
    create_response = api_client.post(
        "/medspas/1/services",
        json={
            "name": "Therapeutic Massage",
            "price": 17500,
            "duration": 75,
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Therapeutic Massage"
    assert created["description"] is None
    assert created["price"] == 17500
    assert created["duration"] == 75

    get_response = api_client.get(f"/services/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json() == created

    list_response = api_client.get("/medspas/1/services")
    assert list_response.status_code == 200
    assert [service["id"] for service in list_response.json()] == [1, 2, created["id"]]


def test_service_patch_updates_values_and_preserves_omitted_fields(
    api_client: TestClient,
) -> None:
    before = api_client.get("/services/2").json()
    update_response = api_client.patch(
        "/services/2",
        json={"name": "Updated Facial", "price": 13000},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Facial"
    assert update_response.json()["price"] == 13000
    assert update_response.json()["description"] == before["description"]
    assert update_response.json()["duration"] == before["duration"]

    get_response = api_client.get("/services/2")
    assert get_response.status_code == 200
    assert get_response.json() == update_response.json()


def test_service_patch_sets_zero_and_empty_description(
    api_client: TestClient,
) -> None:
    before = api_client.get("/services/2").json()
    response = api_client.patch(
        "/services/2",
        json={"price": 0, "description": ""},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["price"] == 0
    assert updated["description"] == ""
    assert updated["name"] == before["name"]
    assert updated["duration"] == before["duration"]

    assert api_client.get("/services/2").json() == updated
    list_response = api_client.get("/medspas/1/services")
    assert list_response.status_code == 200
    assert next(item for item in list_response.json() if item["id"] == 2) == updated


def test_service_patch_clears_description_in_response_get_and_list(
    api_client: TestClient,
) -> None:
    set_response = api_client.patch(
        "/services/2",
        json={"description": "Existing description"},
    )
    assert set_response.status_code == 200
    assert set_response.json()["description"] == "Existing description"

    clear_response = api_client.patch("/services/2", json={"description": None})
    assert clear_response.status_code == 200
    assert clear_response.json()["description"] is None

    get_response = api_client.get("/services/2")
    assert get_response.status_code == 200
    assert get_response.json() == clear_response.json()

    list_response = api_client.get("/medspas/1/services")
    assert list_response.status_code == 200
    listed_service = next(item for item in list_response.json() if item["id"] == 2)
    assert listed_service == clear_response.json()
    assert listed_service["description"] is None


@pytest.mark.parametrize(
    ("null_field", "valid_change"),
    [
        ("name", {"price": 0}),
        ("price", {"name": "Must not be applied"}),
        ("duration", {"name": "Must not be applied"}),
    ],
)
def test_service_patch_rejects_nonnullable_null_atomically(
    api_client: TestClient,
    null_field: str,
    valid_change: dict[str, object],
) -> None:
    before = api_client.get("/services/2").json()
    payload = {**valid_change, null_field: None}

    response = api_client.patch("/services/2", json=payload)

    assert response.status_code == 422
    assert api_client.get("/services/2").json() == before


def test_service_patch_empty_object_is_a_noop(api_client: TestClient) -> None:
    before = api_client.get("/services/2").json()

    response = api_client.patch("/services/2", json={})

    assert response.status_code == 200
    assert response.json() == before
    assert api_client.get("/services/2").json() == before


def test_service_create_allows_explicit_null_description(
    api_client: TestClient,
) -> None:
    response = api_client.post(
        "/medspas/1/services",
        json={
            "name": "Null description service",
            "price": 0,
            "duration": 30,
            "description": None,
        },
    )

    assert response.status_code == 201
    created = response.json()
    assert created["description"] is None
    assert api_client.get(f"/services/{created['id']}").json() == created


@pytest.mark.parametrize("field", ["name", "price", "duration"])
def test_service_create_rejects_explicit_null_required_fields(
    api_client: TestClient,
    field: str,
) -> None:
    payload: dict[str, object] = {
        "name": "Required field check",
        "price": 100,
        "duration": 30,
    }
    payload[field] = None
    before = api_client.get("/medspas/1/services").json()

    response = api_client.post("/medspas/1/services", json=payload)

    assert response.status_code == 422
    assert api_client.get("/medspas/1/services").json() == before


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Invalid price", "price": -1, "duration": 30},
        {"name": "Invalid duration", "price": 100, "duration": 0},
        {"name": "Fractional cents", "price": 10.5, "duration": 30},
        {"name": "Fractional minutes", "price": 100, "duration": 30.5},
        {
            "name": "Price exceeds PostgreSQL INTEGER",
            "price": MAX_POSTGRES_INTEGER + 1,
            "duration": 30,
        },
        {
            "name": "Duration exceeds PostgreSQL INTEGER",
            "price": 100,
            "duration": MAX_POSTGRES_INTEGER + 1,
        },
    ],
)
def test_service_create_rejects_invalid_values(
    api_client: TestClient,
    payload: dict[str, object],
) -> None:
    response = api_client.post("/medspas/1/services", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {"price": -1},
        {"duration": 0},
        {"price": MAX_POSTGRES_INTEGER + 1},
        {"duration": MAX_POSTGRES_INTEGER + 1},
    ],
)
def test_service_patch_rejects_invalid_values(
    api_client: TestClient,
    payload: dict[str, object],
) -> None:
    response = api_client.patch("/services/2", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize("name", ["", " ", "\t\n"])
def test_service_routes_reject_blank_names(
    api_client: TestClient,
    name: str,
) -> None:
    response = api_client.post(
        "/medspas/1/services",
        json={"name": name, "price": 100, "duration": 30},
    )

    assert response.status_code == 422


def test_service_patch_rejects_unknown_medspa_id(
    api_client: TestClient,
) -> None:
    response = api_client.patch("/services/2", json={"medspa_id": 1})

    assert response.status_code == 422


def test_service_list_excludes_other_medspas_services(
    api_client: TestClient,
    second_medspa_with_service: None,
) -> None:
    response = api_client.get("/medspas/1/services")

    assert response.status_code == 200
    assert [service["id"] for service in response.json()] == [1, 2]


def test_service_routes_return_not_found_for_unknown_resources(
    api_client: TestClient,
) -> None:
    assert api_client.get("/services/999").status_code == 404
    patch_response = api_client.patch("/services/999", json={"name": "Missing"})
    assert patch_response.status_code == 404
    assert api_client.get("/medspas/999/services").status_code == 404
    assert (
        api_client.post(
            "/medspas/999/services",
            json={"name": "Missing Medspa", "price": 100, "duration": 30},
        ).status_code
        == 404
    )

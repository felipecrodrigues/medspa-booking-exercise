from typing import get_args, get_type_hints

import pytest
from pydantic import ValidationError

from medspa_booking.db.limits import MAX_POSTGRES_INTEGER
from medspa_booking.services.schemas import ServiceCreate, ServicePatch


def test_service_create_allows_optional_description() -> None:
    service = ServiceCreate(name="Consultation", price=0, duration=30)
    service_with_null_description = ServiceCreate(
        name="Consultation",
        price=0,
        duration=30,
        description=None,
    )

    assert service.description is None
    assert service_with_null_description.description is None


@pytest.mark.parametrize("field", ["name", "price", "duration"])
def test_service_create_rejects_explicit_null_required_fields(field: str) -> None:
    payload: dict[str, object] = {
        "name": "Consultation",
        "price": 100,
        "duration": 30,
    }
    payload[field] = None

    with pytest.raises(ValidationError):
        ServiceCreate(**payload)


@pytest.mark.parametrize("price", [-1, 1.5, True, "100"])
def test_service_price_must_be_nonnegative_integer_cents(price: object) -> None:
    with pytest.raises(ValidationError):
        ServiceCreate(name="Consultation", price=price, duration=30)


@pytest.mark.parametrize("duration", [0, -1, 1.5, True, "30"])
def test_service_duration_must_be_positive_integer_minutes(duration: object) -> None:
    with pytest.raises(ValidationError):
        ServiceCreate(name="Consultation", price=100, duration=duration)


def test_service_patch_distinguishes_omission_from_description_clear() -> None:
    omitted_patch = ServicePatch()
    clear_description_patch = ServicePatch(description=None)

    assert omitted_patch.model_fields_set == set()
    assert omitted_patch.model_dump(exclude_unset=True) == {}
    assert clear_description_patch.model_fields_set == {"description"}
    assert clear_description_patch.model_dump(exclude_unset=True) == {
        "description": None,
    }


def test_service_patch_omitted_field_types_include_none() -> None:
    annotations = get_type_hints(ServicePatch)

    for field in ("name", "price", "duration"):
        assert type(None) in get_args(annotations[field])


@pytest.mark.parametrize("field", ["name", "price", "duration"])
def test_service_patch_rejects_explicit_null_for_nonnullable_fields(
    field: str,
) -> None:
    with pytest.raises(ValidationError):
        ServicePatch(**{field: None})


def test_service_patch_json_schema_matches_presence_and_null_contract() -> None:
    schema = ServicePatch.model_json_schema()
    properties = schema["properties"]

    assert not {"name", "price", "duration"}.intersection(
        schema.get("required", [])
    )
    for field in ("name", "price", "duration"):
        assert "default" not in properties[field]
    assert properties["name"]["type"] == "string"
    assert properties["price"]["type"] == "integer"
    assert properties["duration"]["type"] == "integer"
    assert properties["description"].get("anyOf") == [
        {"type": "string"},
        {"type": "null"},
    ]


def test_service_schema_accepts_postgres_integer_maximum() -> None:
    service = ServiceCreate(
        name="Maximum values",
        price=MAX_POSTGRES_INTEGER,
        duration=MAX_POSTGRES_INTEGER,
    )

    assert service.price == MAX_POSTGRES_INTEGER
    assert service.duration == MAX_POSTGRES_INTEGER


@pytest.mark.parametrize("field", ["price", "duration"])
def test_service_create_rejects_postgres_integer_overflow(field: str) -> None:
    payload: dict[str, object] = {
        "name": "Too large",
        "price": 1,
        "duration": 1,
        field: MAX_POSTGRES_INTEGER + 1,
    }

    with pytest.raises(ValidationError):
        ServiceCreate(**payload)


@pytest.mark.parametrize("field", ["price", "duration"])
def test_service_patch_rejects_postgres_integer_overflow(field: str) -> None:
    with pytest.raises(ValidationError):
        ServicePatch(**{field: MAX_POSTGRES_INTEGER + 1})


@pytest.mark.parametrize("name", ["", " ", "\t\n"])
def test_service_create_rejects_blank_names(name: str) -> None:
    with pytest.raises(ValidationError):
        ServiceCreate(name=name, price=100, duration=30)


@pytest.mark.parametrize("name", ["", " ", "\t\n"])
def test_service_patch_rejects_blank_names(name: str) -> None:
    with pytest.raises(ValidationError):
        ServicePatch(name=name)


def test_service_create_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ServiceCreate(
            name="Consultation",
            price=100,
            duration=30,
            medspa_id=1,
        )


def test_service_patch_rejects_medspa_id() -> None:
    with pytest.raises(ValidationError):
        ServicePatch(medspa_id=1)

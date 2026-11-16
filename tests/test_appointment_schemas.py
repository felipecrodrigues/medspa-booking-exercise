from datetime import UTC, datetime, timedelta, timezone
from json import dumps
from typing import get_args, get_type_hints

import pytest
from pydantic import ValidationError

from medspa_booking.appointments.schemas import AppointmentCreate, AppointmentPatch
from medspa_booking.db.limits import MAX_POSTGRES_INTEGER


def test_appointment_accepts_future_timezone_aware_time() -> None:
    start_time = datetime.now(UTC) + timedelta(days=1)

    request = AppointmentCreate(start_time=start_time, service_ids=[1])

    assert request.start_time == start_time


def test_appointment_normalizes_non_utc_time_to_utc() -> None:
    non_utc = timezone(timedelta(hours=5, minutes=30))
    start_time = datetime.now(non_utc) + timedelta(days=1)

    request = AppointmentCreate(start_time=start_time, service_ids=[1])

    assert request.start_time.utcoffset() == timedelta(0)
    assert request.start_time == start_time.astimezone(UTC)


@pytest.mark.parametrize("as_string", [False, True])
def test_appointment_rejects_future_epoch_timestamp(as_string: bool) -> None:
    future_epoch = int((datetime.now(UTC) + timedelta(days=1)).timestamp())
    start_time: int | str = str(future_epoch) if as_string else future_epoch
    payload = dumps({"start_time": start_time, "service_ids": [1]})

    with pytest.raises(ValidationError):
        AppointmentCreate.model_validate_json(payload)


@pytest.mark.parametrize(
    "start_time",
    [
        datetime.now(),
        datetime.now(UTC) - timedelta(days=1),
        "2099-01-01T10:00:00",
    ],
)
def test_appointment_rejects_naive_or_non_future_start_time(
    start_time: object,
) -> None:
    with pytest.raises(ValidationError):
        AppointmentCreate(start_time=start_time, service_ids=[1])


@pytest.mark.parametrize("service_ids", [[], [True]])
def test_appointment_requires_at_least_one_integer_service_id(
    service_ids: list[object],
) -> None:
    with pytest.raises(ValidationError):
        AppointmentCreate(
            start_time=datetime.now(UTC) + timedelta(days=1),
            service_ids=service_ids,
        )


def test_appointment_patch_accepts_only_supported_status_values() -> None:
    assert AppointmentPatch(status="completed").status == "completed"
    omitted_patch = AppointmentPatch()
    assert omitted_patch.status is None
    assert omitted_patch.model_fields_set == set()
    assert omitted_patch.model_dump(exclude_unset=True) == {}
    with pytest.raises(ValidationError):
        AppointmentPatch(status="pending")


def test_appointment_patch_omitted_status_type_includes_none() -> None:
    status_type = get_type_hints(AppointmentPatch)["status"]

    assert type(None) in get_args(status_type)


def test_appointment_patch_rejects_explicit_null_status() -> None:
    with pytest.raises(ValidationError):
        AppointmentPatch(status=None)


def test_appointment_patch_json_schema_keeps_status_optional_and_nonnullable() -> None:
    schema = AppointmentPatch.model_json_schema()
    status_schema = schema["properties"]["status"]

    assert "status" not in schema.get("required", [])
    assert "default" not in status_schema
    assert status_schema["$ref"].endswith("/AppointmentStatus")
    assert "anyOf" not in status_schema


@pytest.mark.parametrize("field", ["start_time", "service_ids"])
def test_appointment_create_rejects_explicit_null_required_fields(field: str) -> None:
    payload: dict[str, object] = {
        "start_time": datetime.now(UTC) + timedelta(days=1),
        "service_ids": [1],
    }
    payload[field] = None

    with pytest.raises(ValidationError):
        AppointmentCreate(**payload)


def test_appointment_service_ids_reject_postgres_integer_overflow() -> None:
    with pytest.raises(ValidationError):
        AppointmentCreate(
            start_time=datetime.now(UTC) + timedelta(days=1),
            service_ids=[MAX_POSTGRES_INTEGER + 1],
        )


def test_appointment_create_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        AppointmentCreate(
            start_time=datetime.now(UTC) + timedelta(days=1),
            service_ids=[1],
            unexpected_field="not in the API contract",
        )


def test_appointment_patch_rejects_start_time() -> None:
    with pytest.raises(ValidationError):
        AppointmentPatch(start_time=datetime.now(UTC) + timedelta(days=1))

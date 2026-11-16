"""Pydantic contracts for the appointment feature."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.json_schema import SkipJsonSchema

from medspa_booking.appointments.rules import ensure_future_utc
from medspa_booking.appointments.status import AppointmentStatus
from medspa_booking.db.limits import MAX_POSTGRES_INTEGER

ServiceId = Annotated[
    int,
    Field(strict=True, gt=0, le=MAX_POSTGRES_INTEGER),
]


class AppointmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start_time: datetime
    service_ids: Annotated[list[ServiceId], Field(min_length=1)]

    @field_validator("start_time", mode="before")
    @classmethod
    def require_explicit_timezone_offset(cls, value: object) -> object:
        if isinstance(value, datetime):
            parsed_time = value
        elif isinstance(value, str):
            try:
                parsed_time = datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError(
                    "start_time must be an ISO 8601 datetime with an explicit "
                    "timezone offset"
                ) from exc
        else:
            raise ValueError(
                "start_time must be an ISO 8601 datetime with an explicit "
                "timezone offset"
            )

        if parsed_time.utcoffset() is None:
            raise ValueError("start_time must include an explicit timezone offset")
        return value

    @field_validator("start_time")
    @classmethod
    def require_future_timezone_aware_time(cls, value: datetime) -> datetime:
        return ensure_future_utc(value)


class AppointmentPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Omitted attributes default to None; the request schema still rejects null.
    status: AppointmentStatus | SkipJsonSchema[None] = Field(
        default_factory=lambda: None,
    )

    @field_validator("status", mode="before")
    @classmethod
    def reject_explicit_null_status(cls, value: object) -> object:
        if value is None:
            raise ValueError("status may not be null")
        return value


class AppointmentServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    service_id: int
    price_at_booking: int
    duration_at_booking: int


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    medspa_id: int
    start_time: datetime
    status: AppointmentStatus
    service_selections: list[AppointmentServiceRead]
    total_price: int
    total_duration: int

    @field_validator("start_time")
    @classmethod
    def normalize_start_time_to_utc(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)


__all__ = [
    "AppointmentCreate",
    "AppointmentPatch",
    "AppointmentRead",
    "AppointmentServiceRead",
    "ServiceId",
]

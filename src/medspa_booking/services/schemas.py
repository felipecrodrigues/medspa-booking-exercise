"""Pydantic contracts for the service feature."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.json_schema import SkipJsonSchema

from medspa_booking.db.limits import MAX_POSTGRES_INTEGER

PriceCents = Annotated[
    int,
    Field(strict=True, ge=0, le=MAX_POSTGRES_INTEGER),
]
DurationMinutes = Annotated[
    int,
    Field(strict=True, gt=0, le=MAX_POSTGRES_INTEGER),
]


def require_nonblank_service_name(value: str) -> str:
    """Reject service names containing only whitespace."""
    if not value.strip():
        raise ValueError("name must contain a non-whitespace character")
    return value


class ServiceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    price: PriceCents
    duration: DurationMinutes
    description: str | None = None

    @field_validator("name")
    @classmethod
    def require_nonblank_name(cls, value: str) -> str:
        return require_nonblank_service_name(value)


class ServicePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Omitted attributes default to None; dumps must use exclude_unset=True.
    # SkipJsonSchema keeps the internal None branch out of the request schema.
    name: str | SkipJsonSchema[None] = Field(default_factory=lambda: None)
    description: str | None = None
    price: PriceCents | SkipJsonSchema[None] = Field(default_factory=lambda: None)
    duration: DurationMinutes | SkipJsonSchema[None] = Field(
        default_factory=lambda: None,
    )

    @field_validator("name", "price", "duration", mode="before")
    @classmethod
    def reject_explicit_nulls(cls, value: object) -> object:
        if value is None:
            raise ValueError("field may not be null")
        return value

    @field_validator("name")
    @classmethod
    def require_nonblank_name(cls, value: str) -> str:
        return require_nonblank_service_name(value)


class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    medspa_id: int
    name: str
    description: str | None
    price: int
    duration: int


__all__ = [
    "DurationMinutes",
    "PriceCents",
    "ServiceCreate",
    "ServicePatch",
    "ServiceRead",
    "require_nonblank_service_name",
]

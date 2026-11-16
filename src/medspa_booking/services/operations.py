"""Service feature use cases and persistence operations."""

from __future__ import annotations

from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from medspa_booking.errors import ResourceNotFoundError
from medspa_booking.medspas.operations import require_medspa_exists
from medspa_booking.services.models import Service

_PATCHABLE_FIELDS = frozenset({"name", "description", "price", "duration"})
_NON_NULLABLE_PATCH_FIELDS = frozenset({"name", "price", "duration"})


def create_service(
    session: Session,
    medspa_id: int,
    *,
    name: str,
    price: int,
    duration: int,
    description: str | None,
) -> Service:
    """Create a service after confirming its medspa exists."""
    require_medspa_exists(session, medspa_id)
    service = Service(
        medspa_id=medspa_id,
        name=name,
        description=description,
        price=price,
        duration=duration,
    )
    session.add(service)
    session.commit()
    session.refresh(service)
    return service


def get_service(session: Session, service_id: int) -> Service:
    """Retrieve one service by ID."""
    service = session.get(Service, service_id)
    if service is None:
        raise ResourceNotFoundError(f"service {service_id} not found")
    return service


def list_services(session: Session, medspa_id: int) -> list[Service]:
    """Return every service for a medspa in stable ID order."""
    require_medspa_exists(session, medspa_id)
    statement = (
        select(Service)
        .where(Service.medspa_id == medspa_id)
        .order_by(Service.id)
    )
    return list(session.scalars(statement).all())


def patch_service(
    session: Session,
    service_id: int,
    changes: Mapping[str, object],
) -> Service:
    """Apply supplied values; omitted fields stay and null clears description."""
    service = get_service(session, service_id)
    unsupported_fields = set(changes) - _PATCHABLE_FIELDS
    if unsupported_fields:
        invalid_fields = ", ".join(sorted(unsupported_fields))
        raise ValueError(f"unsupported service patch field(s): {invalid_fields}")

    null_fields = {
        field_name
        for field_name, value in changes.items()
        if field_name in _NON_NULLABLE_PATCH_FIELDS and value is None
    }
    if null_fields:
        invalid_fields = ", ".join(sorted(null_fields))
        raise ValueError(f"service patch field(s) may not be null: {invalid_fields}")

    changed = False
    for field_name, value in changes.items():
        if getattr(service, field_name) != value:
            setattr(service, field_name, value)
            changed = True

    if changed:
        session.commit()
        session.refresh(service)
    return service


__all__ = ["create_service", "get_service", "list_services", "patch_service"]

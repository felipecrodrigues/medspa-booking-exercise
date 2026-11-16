"""Appointment feature use cases and persistence operations."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from medspa_booking.appointments.models import Appointment, AppointmentService
from medspa_booking.appointments.rules import (
    ServiceValues,
    build_service_snapshots,
)
from medspa_booking.appointments.status import AppointmentStatus
from medspa_booking.errors import (
    InvalidServiceSelectionError,
    ResourceNotFoundError,
)
from medspa_booking.medspas.operations import require_medspa_exists
from medspa_booking.services.models import Service


def create_appointment(
    session: Session,
    medspa_id: int,
    *,
    start_time: datetime,
    service_ids: Sequence[int],
) -> Appointment:
    """Atomically book distinct same-medspa services and preserve snapshots."""
    require_medspa_exists(session, medspa_id)
    selected_services = session.scalars(
        select(Service).where(Service.id.in_(service_ids))
    ).all()
    services_by_id: dict[int, ServiceValues] = {
        service.id: (service.medspa_id, service.price, service.duration)
        for service in selected_services
    }
    try:
        snapshots = build_service_snapshots(
            service_ids=service_ids,
            medspa_id=medspa_id,
            services_by_id=services_by_id,
        )
    except ValueError as exc:
        raise InvalidServiceSelectionError(str(exc)) from exc

    appointment = Appointment(
        medspa_id=medspa_id,
        start_time=start_time,
        status=AppointmentStatus.SCHEDULED.value,
        service_selections=[
            AppointmentService(
                service_id=service_id,
                price_at_booking=price,
                duration_at_booking=duration,
            )
            for service_id, price, duration in snapshots
        ],
    )
    session.add(appointment)
    session.commit()
    return appointment


def get_appointment(session: Session, appointment_id: int) -> Appointment:
    """Retrieve an appointment and its booking-time service snapshots."""
    statement = (
        select(Appointment)
        .options(selectinload(Appointment.service_selections))
        .where(Appointment.id == appointment_id)
    )
    appointment = session.scalars(statement).one_or_none()
    if appointment is None:
        raise ResourceNotFoundError(f"appointment {appointment_id} not found")
    return appointment


def patch_appointment(
    session: Session,
    appointment_id: int,
    *,
    status: AppointmentStatus | None,
) -> Appointment:
    """Update a supplied status; None represents omission after request validation."""
    appointment = get_appointment(session, appointment_id)
    if status is not None and appointment.status != status.value:
        appointment.status = status.value
        session.commit()
    return appointment


def list_appointments(session: Session) -> list[Appointment]:
    """Return all appointments in stable ID order with their saved snapshots."""
    statement = (
        select(Appointment)
        .options(selectinload(Appointment.service_selections))
        .order_by(Appointment.id)
    )
    return list(session.scalars(statement).all())


__all__ = [
    "create_appointment",
    "get_appointment",
    "list_appointments",
    "patch_appointment",
]

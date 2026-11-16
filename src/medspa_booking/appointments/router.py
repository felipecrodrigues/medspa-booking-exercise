"""HTTP routes for the appointment feature."""

from fastapi import APIRouter

from medspa_booking.appointments.operations import (
    create_appointment,
    get_appointment,
    list_appointments,
    patch_appointment,
)
from medspa_booking.appointments.schemas import (
    AppointmentCreate,
    AppointmentPatch,
    AppointmentRead,
)
from medspa_booking.dependencies import PathId, SessionDep

router = APIRouter(tags=["appointments"])


@router.post(
    "/medspas/{medspa_id}/appointments",
    response_model=AppointmentRead,
    status_code=201,
)
def create_appointment_endpoint(
    medspa_id: PathId,
    request: AppointmentCreate,
    session: SessionDep,
) -> AppointmentRead:
    return create_appointment(
        session,
        medspa_id,
        start_time=request.start_time,
        service_ids=request.service_ids,
    )


@router.get("/appointments/{appointment_id}", response_model=AppointmentRead)
def get_appointment_endpoint(
    appointment_id: PathId,
    session: SessionDep,
) -> AppointmentRead:
    return get_appointment(session, appointment_id)


@router.patch("/appointments/{appointment_id}", response_model=AppointmentRead)
def patch_appointment_endpoint(
    appointment_id: PathId,
    request: AppointmentPatch,
    session: SessionDep,
) -> AppointmentRead:
    return patch_appointment(
        session,
        appointment_id,
        status=request.status,
    )


@router.get("/appointments", response_model=list[AppointmentRead])
def list_appointments_endpoint(session: SessionDep) -> list[AppointmentRead]:
    return list_appointments(session)


__all__ = ["router"]

"""HTTP routes for the service feature."""

from fastapi import APIRouter

from medspa_booking.dependencies import PathId, SessionDep
from medspa_booking.services.operations import (
    create_service,
    get_service,
    list_services,
    patch_service,
)
from medspa_booking.services.schemas import ServiceCreate, ServicePatch, ServiceRead

router = APIRouter(tags=["services"])


@router.post(
    "/medspas/{medspa_id}/services",
    response_model=ServiceRead,
    status_code=201,
)
def create_service_endpoint(
    medspa_id: PathId,
    request: ServiceCreate,
    session: SessionDep,
) -> ServiceRead:
    return create_service(
        session,
        medspa_id,
        name=request.name,
        price=request.price,
        duration=request.duration,
        description=request.description,
    )


@router.get("/services/{service_id}", response_model=ServiceRead)
def get_service_endpoint(service_id: PathId, session: SessionDep) -> ServiceRead:
    return get_service(session, service_id)


@router.get(
    "/medspas/{medspa_id}/services",
    response_model=list[ServiceRead],
)
def list_services_endpoint(
    medspa_id: PathId,
    session: SessionDep,
) -> list[ServiceRead]:
    return list_services(session, medspa_id)


@router.patch("/services/{service_id}", response_model=ServiceRead)
def patch_service_endpoint(
    service_id: PathId,
    request: ServicePatch,
    session: SessionDep,
) -> ServiceRead:
    return patch_service(
        session,
        service_id,
        changes=request.model_dump(exclude_unset=True),
    )


__all__ = ["router"]

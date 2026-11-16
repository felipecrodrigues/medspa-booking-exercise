"""Shared medspa lookup used by the service and appointment features."""

from sqlalchemy.orm import Session

from medspa_booking.errors import ResourceNotFoundError
from medspa_booking.medspas.models import Medspa


def require_medspa_exists(session: Session, medspa_id: int) -> None:
    """Raise the shared not-found error when a nested route's medspa is absent."""
    if session.get(Medspa, medspa_id) is None:
        raise ResourceNotFoundError(f"medspa {medspa_id} not found")


__all__ = ["require_medspa_exists"]

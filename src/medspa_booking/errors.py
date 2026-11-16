"""Use-case errors shared by feature operations and HTTP exception handlers."""


class BookingOperationError(Exception):
    """Base exception for booking use-case failures."""


class ResourceNotFoundError(BookingOperationError):
    """Raised when a requested medspa, service, or appointment is missing."""


class InvalidServiceSelectionError(BookingOperationError):
    """Raised when selected services are invalid for an appointment medspa."""


__all__ = [
    "BookingOperationError",
    "InvalidServiceSelectionError",
    "ResourceNotFoundError",
]

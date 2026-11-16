"""Appointment statuses shared by domain rules and persistence/API layers."""

from enum import StrEnum


class AppointmentStatus(StrEnum):
    """Statuses accepted by the appointment API."""

    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELED = "canceled"


__all__ = ["AppointmentStatus"]

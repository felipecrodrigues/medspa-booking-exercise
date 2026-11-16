"""Register all ORM feature models on the shared SQLAlchemy metadata."""

from medspa_booking.appointments.models import Appointment, AppointmentService
from medspa_booking.db.base import Base
from medspa_booking.medspas.models import Medspa
from medspa_booking.services.models import Service

__all__ = ["Appointment", "AppointmentService", "Base", "Medspa", "Service"]

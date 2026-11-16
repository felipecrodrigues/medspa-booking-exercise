"""SQLAlchemy persistence models for appointments and booking snapshots."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medspa_booking.appointments.rules import appointment_totals
from medspa_booking.appointments.status import AppointmentStatus
from medspa_booking.db.base import Base

if TYPE_CHECKING:
    from medspa_booking.medspas.models import Medspa
    from medspa_booking.services.models import Service


_APPOINTMENT_STATUS_CHECK_VALUES = ", ".join(
    f"'{status.value}'" for status in AppointmentStatus
)


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        CheckConstraint(
            f"status IN ({_APPOINTMENT_STATUS_CHECK_VALUES})",
            name="ck_appointments_status_allowed",
        ),
        Index("ix_appointments_medspa_id", "medspa_id"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    medspa_id: Mapped[int] = mapped_column(
        ForeignKey("medspas.id"), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=AppointmentStatus.SCHEDULED.value,
        server_default=text("'scheduled'"),
    )

    medspa: Mapped[Medspa] = relationship("Medspa", back_populates="appointments")
    service_selections: Mapped[list[AppointmentService]] = relationship(
        "AppointmentService",
        back_populates="appointment",
        cascade="all, delete-orphan",
        order_by="AppointmentService.service_id",
    )

    def _totals(self) -> tuple[int, int]:
        snapshots = tuple(
            (
                selection.service_id,
                selection.price_at_booking,
                selection.duration_at_booking,
            )
            for selection in self.service_selections
        )
        return appointment_totals(snapshots)

    @property
    def total_price(self) -> int:
        """Sum the prices captured when the appointment was booked."""
        return self._totals()[0]

    @property
    def total_duration(self) -> int:
        """Sum the durations captured when the appointment was booked."""
        return self._totals()[1]


class AppointmentService(Base):
    __tablename__ = "appointment_services"
    __table_args__ = (
        CheckConstraint(
            "price_at_booking >= 0",
            name="ck_appointment_services_price_nonnegative",
        ),
        CheckConstraint(
            "duration_at_booking > 0",
            name="ck_appointment_services_duration_positive",
        ),
    )

    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id", ondelete="CASCADE"), primary_key=True
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id"), primary_key=True
    )
    price_at_booking: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_at_booking: Mapped[int] = mapped_column(Integer, nullable=False)

    appointment: Mapped[Appointment] = relationship(
        "Appointment",
        back_populates="service_selections",
    )
    service: Mapped[Service] = relationship(
        "Service",
        back_populates="appointment_selections",
    )


__all__ = ["Appointment", "AppointmentService"]

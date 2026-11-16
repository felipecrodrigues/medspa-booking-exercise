"""Seed-only Medspa persistence model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medspa_booking.db.base import Base

if TYPE_CHECKING:
    from medspa_booking.appointments.models import Appointment
    from medspa_booking.services.models import Service


class Medspa(Base):
    __tablename__ = "medspas"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    phone_number: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)

    services: Mapped[list[Service]] = relationship(
        "Service",
        back_populates="medspa",
    )
    appointments: Mapped[list[Appointment]] = relationship(
        "Appointment",
        back_populates="medspa",
    )


__all__ = ["Medspa"]

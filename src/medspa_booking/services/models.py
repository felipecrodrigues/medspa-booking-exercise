"""SQLAlchemy persistence model for catalog services."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Identity, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medspa_booking.db.base import Base

if TYPE_CHECKING:
    from medspa_booking.appointments.models import AppointmentService
    from medspa_booking.medspas.models import Medspa


class Service(Base):
    __tablename__ = "services"
    __table_args__ = (
        CheckConstraint(
            "name ~ '[^[:space:]]'",
            name="ck_services_name_nonblank",
        ),
        CheckConstraint("price >= 0", name="ck_services_price_nonnegative"),
        CheckConstraint("duration > 0", name="ck_services_duration_positive"),
        Index("ix_services_medspa_id", "medspa_id"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    medspa_id: Mapped[int] = mapped_column(
        ForeignKey("medspas.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)

    medspa: Mapped[Medspa] = relationship("Medspa", back_populates="services")
    appointment_selections: Mapped[list[AppointmentService]] = relationship(
        "AppointmentService",
        back_populates="service",
    )


__all__ = ["Service"]

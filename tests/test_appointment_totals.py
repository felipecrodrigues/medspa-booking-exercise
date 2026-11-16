from datetime import UTC, datetime, timedelta

from medspa_booking.appointments.models import Appointment, AppointmentService


def test_totals_are_derived_from_booking_time_snapshots() -> None:
    appointment = Appointment(
        medspa_id=1,
        start_time=datetime.now(UTC) + timedelta(days=1),
        status="scheduled",
        service_selections=[
            AppointmentService(
                service_id=1,
                price_at_booking=5000,
                duration_at_booking=30,
            ),
            AppointmentService(
                service_id=2,
                price_at_booking=12500,
                duration_at_booking=60,
            ),
        ],
    )

    assert appointment.total_price == 17500
    assert appointment.total_duration == 90

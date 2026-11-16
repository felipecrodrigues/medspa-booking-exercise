from datetime import UTC, datetime, timedelta, timezone

import pytest

from medspa_booking.appointments.rules import (
    appointment_totals,
    build_service_snapshots,
    ensure_future_utc,
)


def test_service_snapshots_require_distinct_same_medspa_services_and_sort_ids() -> None:
    snapshots = build_service_snapshots(
        service_ids=[2, 1],
        medspa_id=1,
        services_by_id={
            1: (1, 0, 30),
            2: (1, 12_500, 60),
        },
    )

    assert snapshots == ((1, 0, 30), (2, 12_500, 60))


@pytest.mark.parametrize(
    ("service_ids", "services_by_id"),
    [
        ([], {1: (1, 100, 30)}),
        ([1, 1], {1: (1, 100, 30)}),
        ([1, 999], {1: (1, 100, 30)}),
        ([1, 2], {1: (1, 100, 30), 2: (2, 500, 45)}),
    ],
)
def test_service_snapshots_reject_invalid_selections(
    service_ids: list[int],
    services_by_id: dict[int, tuple[int, int, int]],
) -> None:
    with pytest.raises(ValueError):
        build_service_snapshots(
            service_ids=service_ids,
            medspa_id=1,
            services_by_id=services_by_id,
        )


def test_appointment_totals_sum_booking_time_snapshots() -> None:
    assert appointment_totals(((1, 0, 30), (2, 12_500, 60))) == (12_500, 90)


def test_future_start_time_is_normalized_to_utc() -> None:
    now = datetime(2035, 1, 1, 12, tzinfo=UTC)
    start_time = datetime(
        2035,
        1,
        2,
        10,
        tzinfo=timezone(timedelta(hours=5, minutes=30)),
    )

    assert ensure_future_utc(start_time, now=now) == datetime(
        2035,
        1,
        2,
        4,
        30,
        tzinfo=UTC,
    )


@pytest.mark.parametrize(
    "start_time",
    [
        datetime(2035, 1, 2, 10),
        datetime(2035, 1, 1, 12, tzinfo=UTC),
        datetime(2035, 1, 1, 11, tzinfo=UTC),
    ],
)
def test_future_start_time_rejects_naive_or_not_future_values(
    start_time: datetime,
) -> None:
    with pytest.raises(ValueError):
        ensure_future_utc(
            start_time,
            now=datetime(2035, 1, 1, 12, tzinfo=UTC),
        )

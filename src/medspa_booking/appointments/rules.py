"""Pure booking rules with no HTTP or database dependencies."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime

INVALID_SERVICE_SELECTION_DETAIL = (
    "service_ids must be distinct services belonging to this medspa"
)

ServiceValues = tuple[int, int, int]
ServiceSnapshot = tuple[int, int, int]


def build_service_snapshots(
    *,
    service_ids: Sequence[int],
    medspa_id: int,
    services_by_id: Mapping[int, ServiceValues],
) -> tuple[ServiceSnapshot, ...]:
    """Validate distinct same-medspa services and return sorted booking snapshots."""
    if not service_ids or len(set(service_ids)) != len(service_ids):
        raise ValueError(INVALID_SERVICE_SELECTION_DETAIL)

    snapshots: list[ServiceSnapshot] = []
    for service_id in service_ids:
        service_values = services_by_id.get(service_id)
        if service_values is None or service_values[0] != medspa_id:
            raise ValueError(INVALID_SERVICE_SELECTION_DETAIL)
        _, price, duration = service_values
        snapshots.append((service_id, price, duration))

    return tuple(sorted(snapshots))


def appointment_totals(
    snapshots: Sequence[ServiceSnapshot],
) -> tuple[int, int]:
    """Return total price and duration from booking-time service snapshots."""
    return (
        sum(snapshot[1] for snapshot in snapshots),
        sum(snapshot[2] for snapshot in snapshots),
    )


def ensure_future_utc(
    start_time: datetime,
    *,
    now: datetime | None = None,
) -> datetime:
    """Require a future timezone-aware start and normalize it to UTC."""
    if start_time.utcoffset() is None:
        raise ValueError("start_time must include an explicit timezone offset")

    current_time = now or datetime.now(UTC)
    if start_time <= current_time:
        raise ValueError("start_time must be in the future")

    return start_time.astimezone(UTC)


__all__ = [
    "INVALID_SERVICE_SELECTION_DETAIL",
    "ServiceSnapshot",
    "ServiceValues",
    "appointment_totals",
    "build_service_snapshots",
    "ensure_future_utc",
]

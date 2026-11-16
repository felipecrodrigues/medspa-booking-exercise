from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from medspa_booking.services.operations import patch_service


def make_service(
    *,
    description: str | None = "Current description",
    name: str = "Consultation",
    price: int = 12500,
    duration: int = 30,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        medspa_id=1,
        name=name,
        description=description,
        price=price,
        duration=duration,
    )


def test_service_patch_clears_description_and_commits() -> None:
    service = make_service()
    session = Mock()
    session.get.return_value = service

    result = patch_service(session, service_id=1, changes={"description": None})

    assert result is service
    assert service.description is None
    session.commit.assert_called_once_with()
    session.refresh.assert_called_once_with(service)


@pytest.mark.parametrize(
    "changes",
    [{}, {"description": None}],
)
def test_service_patch_noop_does_not_write_when_nothing_changes(
    changes: dict[str, object],
) -> None:
    service = make_service(description=None)
    before = vars(service).copy()
    session = Mock()
    session.get.return_value = service

    result = patch_service(session, service_id=1, changes=changes)

    assert result is service
    assert vars(service) == before
    session.commit.assert_not_called()
    session.refresh.assert_not_called()


def test_service_patch_sets_falsy_values_and_preserves_omitted_fields() -> None:
    service = make_service()
    session = Mock()
    session.get.return_value = service

    result = patch_service(
        session,
        service_id=1,
        changes={"price": 0, "description": ""},
    )

    assert result is service
    assert service.price == 0
    assert service.description == ""
    assert service.name == "Consultation"
    assert service.duration == 30
    session.commit.assert_called_once_with()
    session.refresh.assert_called_once_with(service)


@pytest.mark.parametrize(
    ("null_field", "valid_changes"),
    [
        ("name", {"price": 0}),
        ("price", {"name": "Updated"}),
        ("duration", {"name": "Updated"}),
    ],
)
def test_service_patch_rejects_nonnullable_null_atomically(
    null_field: str,
    valid_changes: dict[str, object],
) -> None:
    service = make_service()
    before = vars(service).copy()
    session = Mock()
    session.get.return_value = service
    changes = {**valid_changes, null_field: None}

    with pytest.raises(ValueError, match="may not be null"):
        patch_service(session, service_id=1, changes=changes)

    assert vars(service) == before
    session.commit.assert_not_called()
    session.refresh.assert_not_called()


@pytest.mark.parametrize(
    "changes",
    [
        {"id": 99},
        {"medspa_id": 2},
        {"arbitrary_attribute": "not allowed"},
    ],
)
def test_service_patch_rejects_fields_outside_the_public_contract(
    changes: dict[str, object],
) -> None:
    service = make_service(description=None, price=0)
    session = Mock()
    session.get.return_value = service

    with pytest.raises(ValueError, match="unsupported service patch field"):
        patch_service(session, service_id=1, changes=changes)

    assert service.id == 1
    assert service.medspa_id == 1
    session.commit.assert_not_called()

from ipaddress import ip_address

from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError


def validate_test_database_url(database_url: str) -> URL:
    """Require destructive integration tests to use a local *_test database."""
    try:
        url = make_url(database_url)
    except (ArgumentError, TypeError) as exc:
        raise ValueError(
            "TEST_DATABASE_URL must target a dedicated PostgreSQL *_test database"
        ) from exc

    if url.get_backend_name() != "postgresql" or not (url.database or "").endswith(
        "_test"
    ):
        raise ValueError(
            "TEST_DATABASE_URL must target a dedicated PostgreSQL *_test database"
        )

    if url.query:
        raise ValueError("TEST_DATABASE_URL must not include query parameters")

    host = url.host
    if host is None or not _is_loopback_host(host):
        raise ValueError("TEST_DATABASE_URL host must be a loopback host")

    return url


def _is_loopback_host(host: str) -> bool:
    if host.casefold() == "localhost":
        return True

    try:
        return ip_address(host).is_loopback
    except ValueError:
        return False

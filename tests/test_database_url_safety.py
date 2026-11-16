import pytest
from db_url_safety import validate_test_database_url
from sqlalchemy.engine import URL


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "::1"])
def test_test_database_url_accepts_loopback_hosts(host: str) -> None:
    host_part = f"[{host}]" if ":" in host else host
    database_url = (
        f"postgresql+psycopg://booking:booking@{host_part}:55432/medspa_booking_test"
    )

    url = validate_test_database_url(database_url)

    assert isinstance(url, URL)
    assert url.host == host


@pytest.mark.parametrize("host", ["db", "host.docker.internal", "db.example.test"])
def test_test_database_url_rejects_non_loopback_hosts(host: str) -> None:
    database_url = (
        f"postgresql+psycopg://booking:booking@{host}:5432/medspa_booking_test"
    )

    with pytest.raises(ValueError, match="loopback"):
        validate_test_database_url(database_url)


@pytest.mark.parametrize(
    "query",
    [
        "host=remote.example.invalid",
        "hostaddr=203.0.113.10",
        "port=5432",
        "dbname=postgres",
        "service=production",
        "host=remote.example.invalid&dbname=postgres",
    ],
)
def test_test_database_url_rejects_connection_query_parameters(query: str) -> None:
    database_url = (
        "postgresql+psycopg://booking:booking@localhost:55432/"
        f"medspa_booking_test?{query}"
    )

    with pytest.raises(ValueError, match="must not include query parameters"):
        validate_test_database_url(database_url)


def test_test_database_url_requires_dedicated_postgresql_database() -> None:
    with pytest.raises(ValueError, match="dedicated PostgreSQL.*_test"):
        validate_test_database_url(
            "postgresql+psycopg://booking:booking@localhost:5432/medspa_booking"
        )

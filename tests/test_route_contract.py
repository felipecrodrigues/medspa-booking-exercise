from medspa_booking.main import create_app


def test_api_exposes_only_approved_routes_and_database_health() -> None:
    app = create_app(
        database_url="postgresql+psycopg://booking:booking@127.0.0.1:1/unreachable"
    )
    try:
        path_items = app.openapi()["paths"]
        routes: dict[str, set[str]] = {}
        for path, path_item in path_items.items():
            routes[path] = {
                method.upper()
                for method in path_item
                if method in {"get", "post", "patch", "put", "delete"}
            }
    finally:
        app.state.engine.dispose()

    assert routes == {
        "/health": {"GET"},
        "/medspas/{medspa_id}/services": {"POST", "GET"},
        "/services/{service_id}": {"GET", "PATCH"},
        "/medspas/{medspa_id}/appointments": {"POST"},
        "/appointments/{appointment_id}": {"GET", "PATCH"},
        "/appointments": {"GET"},
    }

from pathlib import Path

from fastapi.routing import APIRoute

from src.main import create_app

ROOT = Path(__file__).resolve().parents[1]


def test_notification_schema_and_api_cover_social_events() -> None:
    migration = (
        (ROOT / "migrations" / "20261008_015_create_notifications.sql")
        .read_text(encoding="utf-8")
        .lower()
    )
    repository = (
        ROOT
        / "src"
        / "infrastructure"
        / "repositories"
        / "social_profile_repository.py"
    ).read_text(encoding="utf-8")
    for event in ("follow", "like", "save"):
        assert event in migration
    assert "recipient_user_id" in migration and "read_at" in migration
    assert "on delete cascade" in migration
    assert "insert into notifications" in repository

    routes = {
        route.path: route.methods or set()
        for route in create_app().routes
        if isinstance(route, APIRoute)
    }
    assert "GET" in routes["/api/v1/notifications"]
    assert "PUT" in routes["/api/v1/notifications/read"]
    route_source = (
        ROOT / "src" / "interface" / "api" / "routes" / "notifications.py"
    ).read_text(encoding="utf-8")
    assert "work_title" in route_source
    assert "left join works" in route_source.lower()

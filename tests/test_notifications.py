from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_notification_schema_and_api_cover_social_events() -> None:
    migration = (ROOT / "migrations" / "20261008_015_create_notifications.sql").read_text(encoding="utf-8").lower()
    route = (ROOT / "src" / "interface" / "api" / "routes" / "notifications.py").read_text(encoding="utf-8")
    repository = (ROOT / "src" / "infrastructure" / "repositories" / "social_profile_repository.py").read_text(encoding="utf-8")
    for event in ("follow", "like", "save"):
        assert event in migration
    assert "recipient_user_id" in migration and "read_at" in migration
    assert "on delete cascade" in migration
    assert '@router.get("")' in route
    assert '@router.put("/read"' in route
    assert "insert into notifications" in repository

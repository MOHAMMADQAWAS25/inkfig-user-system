from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_admin_and_session_indexes_match_repository_queries() -> None:
    migration = (
        ROOT / "migrations" / "20261006_009_optimize_query_indexes.sql"
    ).read_text(encoding="utf-8")

    assert "(created_at desc, user_id desc)" in migration
    assert "refresh_tokens (user_id)" in migration
    assert "where revoked_at is null" in migration


def test_low_selectivity_and_superseded_indexes_are_removed() -> None:
    migration = (
        ROOT / "migrations" / "20261006_009_optimize_query_indexes.sql"
    ).read_text(encoding="utf-8")

    assert "drop index if exists public.user_profiles_active_idx" in migration
    assert "drop index if exists public.user_accounts_active_idx" in migration
    assert "drop index if exists public.refresh_tokens_user_idx" in migration


def test_follow_indexes_support_both_connection_directions() -> None:
    migration = (
        ROOT / "migrations" / "20261006_010_add_user_follows.sql"
    ).read_text(encoding="utf-8")

    assert "(follower_user_id, followed_user_id)" in migration
    assert "(follower_user_id, created_at desc, followed_user_id)" in migration
    assert "(followed_user_id, created_at desc, follower_user_id)" in migration
    assert "check (follower_user_id <> followed_user_id)" in migration

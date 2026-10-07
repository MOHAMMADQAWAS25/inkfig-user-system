from pathlib import Path


def test_only_administrators_receive_work_moderation_permission() -> None:
    migration = (
        Path(__file__).parents[1]
        / "migrations"
        / "20261007_014_add_work_moderation_permission.sql"
    ).read_text(encoding="utf-8")

    assert "'works.delete_any'" in migration
    assert "('admin', 'works.delete_any')" in migration
    assert "('system_administrator', 'works.delete_any')" in migration
    assert "('user', 'works.delete_any')" not in migration
    assert "('supervisor', 'works.delete_any')" not in migration
    assert "('viewer', 'works.delete_any')" not in migration

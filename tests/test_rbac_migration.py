from pathlib import Path


def test_registered_roles_receive_work_save_permission() -> None:
    migration = (
        Path(__file__).parents[1]
        / "migrations"
        / "20261005_008_add_work_save_permission.sql"
    ).read_text(encoding="utf-8")

    assert "'works.save'" in migration
    for role in ("user", "supervisor", "admin", "system_administrator"):
        assert f"('{role}','works.save')" in migration
    assert "('viewer','works.save')" not in migration

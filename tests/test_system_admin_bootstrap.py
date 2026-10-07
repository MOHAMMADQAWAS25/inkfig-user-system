import argparse
from pathlib import Path

import pytest

from scripts.create_system_admin import parse_profile


def arguments(**overrides: str) -> argparse.Namespace:
    values = {
        "email": "mohammadqawas25@gmail.com",
        "full_name": "InkFig Admin",
        "phone_number": "0590000000",
        "gender": "male",
        "date_of_birth": "2000-01-01",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_accepts_a_valid_external_administrator_profile() -> None:
    profile = parse_profile(arguments(email=" MOHAMMADQAWAS25@gmail.com "))

    assert profile.email == "mohammadqawas25@gmail.com"
    assert profile.full_name == "InkFig Admin"
    assert profile.phone_number == "0590000000"


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("email", "administrator@example.com"),
        ("phone_number", "123"),
        ("date_of_birth", "2999-01-01"),
    ),
)
def test_rejects_invalid_administrator_profiles(field: str, value: str) -> None:
    with pytest.raises(ValueError):
        parse_profile(arguments(**{field: value}))


def test_password_is_prompted_and_never_accepted_as_an_argument() -> None:
    source = (
        Path(__file__).parents[1] / "scripts" / "create_system_admin.py"
    ).read_text(encoding="utf-8")

    assert 'parser.add_argument("--password"' not in source
    assert "getpass.getpass" in source


def test_external_email_migration_is_limited_to_the_authorized_administrator() -> None:
    migration = (
        Path(__file__).parents[1]
        / "migrations"
        / "20261007_013_allow_external_administrator_emails.sql"
    ).read_text(encoding="utf-8")

    assert "user_accounts_email_allowed_check" in migration
    assert "user_profiles_email_allowed_check" in migration
    assert "mohammadqawas25@gmail.com" in migration
    assert "@students\\.hebron\\.edu" in migration
    assert "@hebron\\.edu" in migration

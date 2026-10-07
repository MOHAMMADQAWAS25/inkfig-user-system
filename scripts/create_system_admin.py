import argparse
import asyncio
import getpass
import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from uuid import UUID, uuid4

import asyncpg  # type: ignore[import-untyped]

from src.infrastructure.security.passwords import Pbkdf2PasswordHasher

STUDENT_EMAIL_PATTERN = re.compile(r"^\d{8}@students\.hebron\.edu$")
STAFF_EMAIL_PATTERN = re.compile(r"^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@hebron\.edu$")
EXTERNAL_SYSTEM_ADMIN_EMAIL = "mohammadqawas25@gmail.com"
PHONE_PATTERN = re.compile(r"^[0-9]{10}$")


@dataclass(frozen=True)
class SystemAdministratorProfile:
    email: str
    full_name: str
    phone_number: str
    gender: str
    date_of_birth: date


def parse_profile(arguments: argparse.Namespace) -> SystemAdministratorProfile:
    email = arguments.email.strip().lower()
    full_name = " ".join(arguments.full_name.split())
    phone_number = arguments.phone_number.strip()
    if not (
        STUDENT_EMAIL_PATTERN.fullmatch(email)
        or STAFF_EMAIL_PATTERN.fullmatch(email)
        or email == EXTERNAL_SYSTEM_ADMIN_EMAIL
    ):
        raise ValueError("Email is not permitted for administrator bootstrap.")
    if not 2 <= len(full_name) <= 120:
        raise ValueError("Full name must contain between 2 and 120 characters.")
    if not PHONE_PATTERN.fullmatch(phone_number):
        raise ValueError("Phone number must contain exactly 10 digits.")
    if arguments.gender not in {"male", "female"}:
        raise ValueError("Gender must be male or female.")
    date_of_birth = date.fromisoformat(arguments.date_of_birth)
    if date_of_birth >= datetime.now(timezone.utc).date():
        raise ValueError("Date of birth must be in the past.")
    return SystemAdministratorProfile(
        email=email,
        full_name=full_name,
        phone_number=phone_number,
        gender=arguments.gender,
        date_of_birth=date_of_birth,
    )


def read_password() -> str:
    password = getpass.getpass("Password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise ValueError("Password and confirmation do not match.")
    if not 8 <= len(password) <= 128:
        raise ValueError("Password must contain between 8 and 128 characters.")
    return password


async def create_system_administrator(
    profile: SystemAdministratorProfile, password_hash: str
) -> tuple[UUID, bool]:
    database_url = os.environ.get("DATABASE_URL", "").replace(
        "postgresql+asyncpg://", "postgresql://", 1
    )
    if not database_url:
        raise RuntimeError("DATABASE_URL is required.")

    connection = await asyncpg.connect(database_url)
    try:
        async with connection.transaction():
            role_exists = await connection.fetchval(
                "select exists(select 1 from public.roles where code = 'system_administrator')"
            )
            if not role_exists:
                raise RuntimeError(
                    "RBAC migrations must run before administrator bootstrap."
                )

            phone_owner = await connection.fetchval(
                "select user_id from public.user_profiles where phone_number = $1",
                profile.phone_number,
            )
            existing_id = await connection.fetchval(
                "select user_id from public.user_accounts where lower(email) = $1 for update",
                profile.email,
            )
            if phone_owner is not None and phone_owner != existing_id:
                raise RuntimeError("The phone number belongs to another account.")

            created = existing_id is None
            user_id = uuid4() if created else existing_id
            if created:
                await connection.execute(
                    """insert into public.user_accounts
                       (user_id, email, password_hash, is_active, account_status, email_verified_at)
                       values ($1, $2, $3, true, 'active', now())""",
                    user_id,
                    profile.email,
                    password_hash,
                )
                await connection.execute(
                    """insert into public.user_profiles
                       (user_id, email, full_name, phone_number, gender, date_of_birth,
                        is_active, email_verified_at)
                       values ($1, $2, $3, $4, $5, $6, true, now())""",
                    user_id,
                    profile.email,
                    profile.full_name,
                    profile.phone_number,
                    profile.gender,
                    profile.date_of_birth,
                )
            else:
                await connection.execute(
                    """update public.user_accounts
                       set password_hash = $2, is_active = true, account_status = 'active',
                           email_verified_at = coalesce(email_verified_at, now()),
                           token_version = token_version + 1, updated_at = now()
                       where user_id = $1""",
                    user_id,
                    password_hash,
                )
                await connection.execute(
                    """insert into public.user_profiles
                       (user_id, email, full_name, phone_number, gender, date_of_birth,
                        is_active, email_verified_at)
                       values ($1, $2, $3, $4, $5, $6, true, now())
                       on conflict (user_id) do update set
                         email = excluded.email,
                         full_name = excluded.full_name,
                         phone_number = excluded.phone_number,
                         gender = excluded.gender,
                         date_of_birth = excluded.date_of_birth,
                         is_active = true,
                         email_verified_at = coalesce(user_profiles.email_verified_at, now()),
                         updated_at = now()""",
                    user_id,
                    profile.email,
                    profile.full_name,
                    profile.phone_number,
                    profile.gender,
                    profile.date_of_birth,
                )
                await connection.execute(
                    "delete from public.refresh_tokens where user_id = $1", user_id
                )

            await connection.execute(
                """insert into public.user_roles
                   (user_id, role_code, assigned_at, assigned_by)
                   values ($1, 'system_administrator', now(), null)
                   on conflict (user_id) do update set
                     role_code = excluded.role_code,
                     assigned_at = excluded.assigned_at,
                     assigned_by = null""",
                user_id,
            )
            await connection.execute(
                "delete from public.email_verification_codes where user_id = $1",
                user_id,
            )
            await connection.execute(
                "delete from public.password_reset_codes where user_id = $1", user_id
            )
            return user_id, created
    finally:
        await connection.close()


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or securely repair the single InkFig system administrator."
    )
    parser.add_argument("--email", required=True)
    parser.add_argument("--full-name", required=True)
    parser.add_argument("--phone-number", required=True)
    parser.add_argument("--gender", required=True, choices=("male", "female"))
    parser.add_argument("--date-of-birth", required=True)
    return parser


def main() -> None:
    profile = parse_profile(argument_parser().parse_args())
    password_hash = Pbkdf2PasswordHasher().hash(read_password())
    user_id, created = asyncio.run(create_system_administrator(profile, password_hash))
    action = "Created" if created else "Updated"
    print(f"{action} verified system administrator {user_id}.")


if __name__ == "__main__":
    main()

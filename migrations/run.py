import asyncio
import os
from pathlib import Path

import asyncpg


async def run() -> None:
    database_url = os.environ.get("DATABASE_URL", "").replace(
        "postgresql+asyncpg://", "postgresql://", 1
    )
    if not database_url:
        raise RuntimeError("DATABASE_URL is required.")

    connection = await asyncpg.connect(database_url)
    try:
        await connection.execute(
            """
            create table if not exists public.schema_migrations (
                filename text primary key,
                applied_at timestamptz not null default now()
            )
            """
        )
        migration_directory = Path(__file__).parent
        for migration in sorted(migration_directory.glob("*.sql")):
            applied = await connection.fetchval(
                "select exists(select 1 from public.schema_migrations where filename = $1)",
                migration.name,
            )
            if applied:
                continue
            async with connection.transaction():
                await connection.execute(migration.read_text(encoding="utf-8"))
                await connection.execute(
                    "insert into public.schema_migrations (filename) values ($1)",
                    migration.name,
                )
            print(f"Applied {migration.name}")
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(run())

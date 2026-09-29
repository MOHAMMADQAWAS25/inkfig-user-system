# Database migrations

Timestamped PostgreSQL `.sql` migrations live in this directory and are applied in
filename order by `python -m migrations.run`. Applied filenames are recorded in
`public.schema_migrations`, so deployed migrations must never be edited or renamed.

Set `DATABASE_URL` to the Supabase Session Pooler SQLAlchemy URL before running the
command. The runner converts the `postgresql+asyncpg://` prefix for asyncpg.

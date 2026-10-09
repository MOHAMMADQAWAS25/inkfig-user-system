create table if not exists public.avatar_storage_cleanup_jobs (
    object_path varchar(512) primary key,
    attempts integer not null default 0 check (attempts >= 0),
    next_attempt_at timestamptz not null default now(),
    last_error varchar(1000),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists avatar_storage_cleanup_jobs_due_idx
    on public.avatar_storage_cleanup_jobs(next_attempt_at, created_at);
alter table public.avatar_storage_cleanup_jobs enable row level security;
revoke all on public.avatar_storage_cleanup_jobs from anon, authenticated;
grant select, insert, update, delete on public.avatar_storage_cleanup_jobs to service_role;

create table if not exists public.password_reset_codes (
    challenge_id uuid primary key,
    user_id uuid not null references public.user_accounts(user_id) on delete cascade,
    code_hash char(64) not null,
    expires_at timestamptz not null,
    attempts integer not null default 0 check (attempts >= 0),
    max_attempts integer not null default 5 check (max_attempts > 0),
    verified_at timestamptz,
    reset_token_hash char(64) unique,
    reset_token_expires_at timestamptz,
    consumed_at timestamptz,
    invalidated_at timestamptz,
    sent_at timestamptz not null default now()
);
create index if not exists password_reset_pending_idx on public.password_reset_codes (user_id, sent_at desc)
where consumed_at is null and invalidated_at is null;
create index if not exists password_reset_expiry_idx on public.password_reset_codes (expires_at);
alter table public.password_reset_codes enable row level security;
revoke all on table public.password_reset_codes from anon, authenticated;
grant select, insert, update, delete on table public.password_reset_codes to service_role;

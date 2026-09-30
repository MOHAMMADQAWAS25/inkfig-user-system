alter table public.user_profiles
    add column if not exists email_verified_at timestamptz;

update public.user_profiles
set email_verified_at = created_at
where is_active = true and email_verified_at is null;

alter table public.user_profiles alter column is_active set default false;

create table if not exists public.email_verification_codes (
    verification_id uuid primary key,
    user_id uuid not null references public.user_profiles(user_id) on delete cascade,
    code_hash char(64) not null,
    expires_at timestamptz not null,
    attempts integer not null default 0 check (attempts >= 0),
    max_attempts integer not null default 5 check (max_attempts > 0),
    consumed_at timestamptz,
    invalidated_at timestamptz,
    sent_at timestamptz not null default now()
);

create index if not exists email_verification_codes_pending_idx
    on public.email_verification_codes (user_id, sent_at desc)
    where consumed_at is null and invalidated_at is null;
create index if not exists email_verification_codes_expiry_idx
    on public.email_verification_codes (expires_at);

alter table public.email_verification_codes enable row level security;
revoke all on table public.email_verification_codes from anon, authenticated;
grant select, insert, update, delete on table public.email_verification_codes to service_role;

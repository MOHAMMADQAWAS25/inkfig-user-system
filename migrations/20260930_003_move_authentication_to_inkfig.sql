create table if not exists public.users (
    user_id uuid primary key,
    email varchar(254) not null,
    password_hash varchar(255) not null,
    is_active boolean not null default false,
    email_verified_at timestamptz,
    token_version integer not null default 0 check (token_version >= 0),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint users_email_hebron_check check (
        email ~ '^[0-9]{8}@students\.hebron\.edu$'
        or email ~ '^[a-z0-9.!#$%&''*+/=?^_`{|}~-]+@hebron\.edu$'
    )
);

insert into public.users (
    user_id, email, password_hash, is_active, email_verified_at, created_at, updated_at
)
select user_id, email, '!password-reset-required!', is_active, email_verified_at, created_at, updated_at
from public.user_profiles
on conflict (user_id) do nothing;

create unique index if not exists users_email_lower_uq on public.users (lower(email));
create index if not exists users_active_idx on public.users (is_active);

alter table public.user_profiles drop constraint if exists user_profiles_user_id_fkey;
alter table public.user_profiles
    add constraint user_profiles_user_id_fkey foreign key (user_id)
    references public.users(user_id) on delete cascade;

alter table public.email_verification_codes
    drop constraint if exists email_verification_codes_user_id_fkey;
alter table public.email_verification_codes
    add constraint email_verification_codes_user_id_fkey foreign key (user_id)
    references public.users(user_id) on delete cascade;

create table if not exists public.refresh_tokens (
    token_id uuid primary key,
    user_id uuid not null references public.users(user_id) on delete cascade,
    token_hash char(64) not null unique,
    expires_at timestamptz not null,
    revoked_at timestamptz,
    created_at timestamptz not null default now()
);

create index if not exists refresh_tokens_user_idx on public.refresh_tokens (user_id);
create index if not exists refresh_tokens_expiry_idx on public.refresh_tokens (expires_at);

alter table public.users enable row level security;
alter table public.refresh_tokens enable row level security;
revoke all on table public.users, public.refresh_tokens from anon, authenticated;
grant select, insert, update, delete on table public.users, public.refresh_tokens to service_role;

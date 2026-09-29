create table if not exists public.user_profiles (
    user_id uuid primary key references auth.users(id) on delete cascade,
    email varchar(254) not null,
    full_name varchar(120) not null,
    phone_number varchar(16) not null,
    gender varchar(16) not null check (gender in ('male', 'female')),
    date_of_birth date not null check (date_of_birth < current_date),
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint user_profiles_email_hebron_check check (
        email ~ '^[0-9]{8}@students\.hebron\.edu$'
        or email ~ '^[a-z0-9.!#$%&''*+/=?^_`{|}~-]+@hebron\.edu$'
    )
);

create unique index if not exists user_profiles_email_lower_uq
    on public.user_profiles (lower(email));
create index if not exists user_profiles_active_idx
    on public.user_profiles (is_active);

alter table public.user_profiles enable row level security;
revoke all on table public.user_profiles from anon, authenticated;
grant select, insert, update, delete on table public.user_profiles to service_role;

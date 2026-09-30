create table if not exists public.email_code_rate_limits (
    scope varchar(32) not null,
    identifier_hash char(64) not null,
    send_count integer not null default 0 check (send_count >= 0),
    last_sent_at timestamptz,
    blocked_until timestamptz,
    updated_at timestamptz not null default now(),
    primary key (scope, identifier_hash)
);

create index if not exists email_code_rate_limits_blocked_idx
on public.email_code_rate_limits (blocked_until)
where blocked_until is not null;

alter table public.email_code_rate_limits enable row level security;
revoke all on table public.email_code_rate_limits from anon, authenticated;
grant select, insert, update, delete on table public.email_code_rate_limits to service_role;

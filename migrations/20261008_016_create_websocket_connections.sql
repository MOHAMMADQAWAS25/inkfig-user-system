create table if not exists public.websocket_connections (
    connection_id varchar(128) primary key,
    user_id uuid not null references public.user_accounts(user_id) on delete cascade,
    connected_at timestamptz not null default now()
);
create index if not exists websocket_connections_user_idx
    on public.websocket_connections(user_id);
alter table public.websocket_connections enable row level security;
revoke all on public.websocket_connections from anon, authenticated;
grant select, insert, update, delete on public.websocket_connections to service_role;

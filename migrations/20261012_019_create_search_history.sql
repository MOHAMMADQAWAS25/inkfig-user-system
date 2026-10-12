create table public.search_history (
    search_history_id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.user_accounts(user_id) on delete cascade,
    query text not null check (char_length(query) between 1 and 500),
    normalized_query text not null check (char_length(normalized_query) between 1 and 500),
    last_searched_at timestamptz not null default now(),
    unique (user_id, normalized_query)
);
create index search_history_recent_idx on public.search_history(user_id, last_searched_at desc, search_history_id desc);
alter table public.search_history enable row level security;
revoke all on public.search_history from anon, authenticated;
grant select, insert, update, delete on public.search_history to service_role;

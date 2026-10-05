create table if not exists public.user_follows (
    follower_user_id uuid not null
        references public.user_accounts(user_id) on delete cascade,
    followed_user_id uuid not null
        references public.user_accounts(user_id) on delete cascade,
    created_at timestamptz not null default now(),
    primary key (follower_user_id, followed_user_id),
    constraint user_follows_no_self_check
        check (follower_user_id <> followed_user_id)
);

create index if not exists user_follows_following_order_idx
    on public.user_follows
        (follower_user_id, created_at desc, followed_user_id);

create index if not exists user_follows_followers_order_idx
    on public.user_follows
        (followed_user_id, created_at desc, follower_user_id);

alter table public.user_follows enable row level security;
revoke all on public.user_follows from anon, authenticated;
grant select, insert, delete on public.user_follows to service_role;


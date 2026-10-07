create table if not exists public.notifications (
    notification_id uuid primary key default gen_random_uuid(),
    recipient_user_id uuid not null references public.user_accounts(user_id) on delete cascade,
    actor_user_id uuid not null references public.user_accounts(user_id) on delete cascade,
    event_type varchar(20) not null check (event_type in ('follow','like','save')),
    work_id uuid references public.works(work_id) on delete cascade,
    created_at timestamptz not null default now(),
    read_at timestamptz,
    constraint notifications_no_self check (recipient_user_id <> actor_user_id),
    constraint notifications_event_unique unique nulls not distinct
        (recipient_user_id, actor_user_id, event_type, work_id)
);
create index if not exists notifications_recipient_created_idx
    on public.notifications(recipient_user_id, created_at desc);
create index if not exists notifications_recipient_unread_idx
    on public.notifications(recipient_user_id, created_at desc) where read_at is null;
alter table public.notifications enable row level security;
revoke all on public.notifications from anon, authenticated;
grant select, insert, update, delete on public.notifications to service_role;

alter table public.user_accounts add column if not exists account_status varchar(32);
update public.user_accounts set account_status = case when is_active then 'active' else 'admin_suspended' end where account_status is null;
alter table public.user_accounts alter column account_status set default 'active';
alter table public.user_accounts alter column account_status set not null;
alter table public.user_accounts drop constraint if exists user_accounts_status_check;
alter table public.user_accounts add constraint user_accounts_status_check check (account_status in ('active','self_deactivated','admin_suspended'));
create index if not exists user_accounts_status_idx on public.user_accounts (account_status, user_id);

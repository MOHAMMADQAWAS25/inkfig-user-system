-- Keep only indexes that match current production access paths.
drop index if exists public.user_profiles_active_idx;
drop index if exists public.user_accounts_active_idx;
drop index if exists public.refresh_tokens_user_idx;

create index if not exists user_accounts_admin_order_idx
    on public.user_accounts (created_at desc, user_id desc);

create index if not exists refresh_tokens_active_user_idx
    on public.refresh_tokens (user_id)
    where revoked_at is null;


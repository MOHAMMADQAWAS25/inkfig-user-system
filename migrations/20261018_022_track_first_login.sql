alter table public.user_accounts add column first_login_at timestamptz null;

-- Expired and revoked sessions are still evidence of a previous successful login.
update public.user_accounts as account
set first_login_at = history.first_session_at
from (
    select user_id, min(created_at) as first_session_at
    from public.refresh_tokens
    group by user_id
) as history
where account.user_id = history.user_id;

alter table public.search_history
    add column artist_user_id uuid references public.user_accounts(user_id) on delete set null,
    add column artist_name text;

-- Recover older text-only entries only when the mention identifies one account.
with candidates as (
    select h.search_history_id, p.user_id, p.full_name,
           count(*) over (partition by h.search_history_id) as matches
    from public.search_history h
    join public.user_profiles p
      on position('@' || lower(p.full_name) || ' ' in h.normalized_query || ' ') > 0
    join public.user_accounts a on a.user_id=p.user_id and a.account_status='active'
)
update public.search_history h
set artist_user_id=c.user_id, artist_name=c.full_name
from candidates c
where h.search_history_id=c.search_history_id and c.matches=1;

-- Restrict reporting only; preserve account access, existing reports and duplicate indexes.
alter table public.user_accounts
    add column if not exists reporting_blocked boolean not null default false,
    add column if not exists reporting_restriction_updated_by uuid references public.user_accounts(user_id) on delete set null,
    add column if not exists reporting_restriction_updated_at timestamptz;

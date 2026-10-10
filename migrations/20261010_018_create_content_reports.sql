create table public.content_reports (
    report_id uuid primary key default gen_random_uuid(),
    reporter_user_id uuid not null,
    target_type text not null check (target_type in ('work', 'user')),
    target_user_id uuid not null,
    target_work_id uuid,
    reason_code text not null check (reason_code in ('harassment', 'hate_speech', 'sexual_content', 'violence', 'spam', 'copyright', 'impersonation', 'other')),
    details text,
    status text not null default 'pending' check (status in ('pending', 'reviewed', 'dismissed', 'actioned')),
    reviewer_user_id uuid,
    reviewer_notes text,
    created_at timestamptz not null default now(),
    reviewed_at timestamptz,
    check ((target_type = 'work' and target_work_id is not null) or (target_type = 'user' and target_work_id is null)),
    check (details is null or char_length(details) between 10 and 2000),
    check (reviewer_notes is null or char_length(reviewer_notes) <= 2000)
);

create index content_reports_queue_idx on public.content_reports(status, created_at desc, report_id desc);
create index content_reports_target_user_idx on public.content_reports(target_user_id, created_at desc);
create index content_reports_target_work_idx on public.content_reports(target_work_id) where target_work_id is not null;
create unique index content_reports_unique_user_report_idx on public.content_reports(reporter_user_id, target_user_id) where target_type = 'user';
create unique index content_reports_unique_work_report_idx on public.content_reports(reporter_user_id, target_work_id) where target_type = 'work';

insert into public.permissions(code, description) values
 ('reports.create', 'Report another account or published work'),
 ('reports.manage', 'Review and resolve submitted reports')
on conflict (code) do update set description = excluded.description;

insert into public.role_permissions(role_code, permission_code) values
 ('user', 'reports.create'), ('supervisor', 'reports.create'), ('admin', 'reports.create'), ('system_administrator', 'reports.create'),
 ('admin', 'reports.manage'), ('system_administrator', 'reports.manage')
on conflict do nothing;

alter table public.content_reports enable row level security;
revoke all on public.content_reports from anon, authenticated;
grant select, insert, update, delete on public.content_reports to service_role;

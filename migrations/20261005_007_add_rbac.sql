create table public.roles (
    code text primary key,
    name text not null unique,
    rank smallint not null unique check (rank between 0 and 100)
);

create table public.permissions (
    code text primary key,
    description text not null
);

create table public.role_permissions (
    role_code text not null references public.roles(code) on delete cascade,
    permission_code text not null references public.permissions(code) on delete cascade,
    primary key (role_code, permission_code)
);

create table public.user_roles (
    user_id uuid primary key references public.user_accounts(user_id) on delete cascade,
    role_code text not null default 'user' references public.roles(code),
    assigned_at timestamptz not null default now(),
    assigned_by uuid null references public.user_accounts(user_id) on delete set null
);

insert into public.roles(code, name, rank) values
 ('viewer', 'Viewer', 10), ('user', 'User', 20), ('supervisor', 'Supervisor', 40),
 ('admin', 'Admin', 80), ('system_administrator', 'System Administrator', 100);

insert into public.permissions(code, description) values
 ('works.upload', 'Upload and publish owned artwork'),
 ('works.like', 'Like and unlike published artwork'),
 ('profile.read_own', 'Read own works and likes'),
 ('users.read', 'List user accounts and roles'),
 ('users.status.manage', 'Activate or ban lower-ranked accounts'),
 ('users.role.manage', 'Assign roles within the actor role ceiling'),
 ('system.manage', 'Unrestricted system administration');

insert into public.role_permissions(role_code, permission_code) values
 ('user','works.upload'), ('user','works.like'), ('user','profile.read_own'),
 ('supervisor','works.upload'), ('supervisor','works.like'), ('supervisor','profile.read_own'),
 ('admin','works.upload'), ('admin','works.like'), ('admin','profile.read_own'),
 ('admin','users.read'), ('admin','users.status.manage'), ('admin','users.role.manage'),
 ('system_administrator','works.upload'), ('system_administrator','works.like'),
 ('system_administrator','profile.read_own'), ('system_administrator','users.read'),
 ('system_administrator','users.status.manage'), ('system_administrator','users.role.manage'),
 ('system_administrator','system.manage');

insert into public.user_roles(user_id, role_code)
select user_id, 'user' from public.user_accounts on conflict (user_id) do nothing;

create function public.assign_default_inkfig_role() returns trigger language plpgsql security definer as $$
begin
  insert into public.user_roles(user_id, role_code) values (new.user_id, 'user');
  return new;
end $$;

create trigger user_accounts_assign_default_role after insert on public.user_accounts
for each row execute function public.assign_default_inkfig_role();

alter table public.roles enable row level security;
alter table public.permissions enable row level security;
alter table public.role_permissions enable row level security;
alter table public.user_roles enable row level security;
revoke all on public.roles, public.permissions, public.role_permissions, public.user_roles from anon, authenticated;
grant select, insert, update, delete on public.roles, public.permissions, public.role_permissions, public.user_roles to service_role;

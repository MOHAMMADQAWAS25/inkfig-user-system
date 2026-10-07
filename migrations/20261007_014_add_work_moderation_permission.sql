insert into public.permissions(code, description) values
 ('works.delete_any', 'Delete any published artwork with a recorded moderation reason')
on conflict (code) do update set description = excluded.description;

insert into public.role_permissions(role_code, permission_code) values
 ('admin', 'works.delete_any'),
 ('system_administrator', 'works.delete_any')
on conflict (role_code, permission_code) do nothing;

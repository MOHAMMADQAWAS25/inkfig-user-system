insert into public.permissions(code, description) values
 ('works.save', 'Save and unsave published artwork')
on conflict (code) do update set description = excluded.description;

insert into public.role_permissions(role_code, permission_code) values
 ('user','works.save'),
 ('supervisor','works.save'),
 ('admin','works.save'),
 ('system_administrator','works.save')
on conflict (role_code, permission_code) do nothing;

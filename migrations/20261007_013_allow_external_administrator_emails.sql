alter table public.user_accounts
    drop constraint if exists user_accounts_email_hebron_check;

alter table public.user_accounts
    add constraint user_accounts_email_allowed_check check (
        email ~ '^[0-9]{8}@students\.hebron\.edu$'
        or email ~ '^[a-z0-9.!#$%&''*+/=?^_`{|}~-]+@hebron\.edu$'
        or lower(email) = 'mohammadqawas25@gmail.com'
    );

alter table public.user_profiles
    drop constraint if exists user_profiles_email_hebron_check;

alter table public.user_profiles
    add constraint user_profiles_email_allowed_check check (
        email ~ '^[0-9]{8}@students\.hebron\.edu$'
        or email ~ '^[a-z0-9.!#$%&''*+/=?^_`{|}~-]+@hebron\.edu$'
        or lower(email) = 'mohammadqawas25@gmail.com'
    );

comment on constraint user_accounts_email_allowed_check on public.user_accounts is
    'Allows Hebron University accounts and the explicitly authorized bootstrap system administrator.';

comment on constraint user_profiles_email_allowed_check on public.user_profiles is
    'Allows Hebron University profiles and the explicitly authorized bootstrap system administrator.';

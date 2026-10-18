alter table public.user_accounts
    add column backup_email varchar(254) null,
    add constraint user_accounts_backup_email_format check (
        backup_email is null or (
            backup_email = lower(btrim(backup_email))
            and backup_email ~ '^[a-z0-9][a-z0-9.]{0,63}@gmail\.com$'
            and backup_email <> email
        )
    );

-- Private account metadata: no grants or public-profile exposure are added.

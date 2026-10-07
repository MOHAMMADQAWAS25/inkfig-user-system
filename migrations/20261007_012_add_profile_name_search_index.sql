create extension if not exists pg_trgm;

create index if not exists user_profiles_full_name_trgm_idx
    on public.user_profiles using gin (lower(full_name) gin_trgm_ops)
    where is_active = true;

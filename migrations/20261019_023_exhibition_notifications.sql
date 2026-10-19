-- Keep existing social upserts compatible with the named constraint.
alter table public.notifications
    add column exhibition_id uuid references public.exhibitions(exhibition_id) on delete set null,
    add column submission_id uuid,
    add column exhibition_name varchar(160),
    add column decision_reason varchar(2000),
    add column decision_key varchar(160),
    drop constraint notifications_event_type_check,
    drop constraint notifications_event_unique;

alter table public.notifications
    add constraint notifications_event_type_check check (event_type in (
        'follow','like','save','submission_approved','submission_rejected',
        'withdrawal_approved','withdrawal_rejected'
    )),
    add constraint notifications_event_unique unique nulls not distinct
        (recipient_user_id,actor_user_id,event_type,work_id,exhibition_id,decision_key);

-- No FK on submission_id: approved withdrawals remove the membership, not its notification.
-- Existing rows/permissions/read state remain unchanged; no historical notifications generated.

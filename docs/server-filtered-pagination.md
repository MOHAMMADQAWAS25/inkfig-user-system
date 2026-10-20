# Administration query filtering and pagination

## Additive API changes

- `GET /api/v1/reports`: existing status/limit/cursor plus validated
  `target_type=work|user`, `reason_code`, `sort=newest|oldest`. All predicates run
  before LIMIT/OFFSET. Sorting uses created_at/report_id in the same direction.
  `total` counts all matches; `type_counts={all,work,user}` uses status/reason scope
  without selected target type so tab totals are meaningful. Legacy stored
  sexual_content reports can be filtered; create-report reason rules unchanged.
- `GET /api/v1/admin/users`: existing limit/cursor plus `query` (max 200, trimmed,
  case-insensitive literal name/email substring), `role` enum and `is_active`
  boolean. WHERE precedes stable creation/user ID order and pagination. `%`, `_`
  and escape characters are escaped for LIKE, not interpreted as wildcards.
  `total` counts matching users; `summary={total,active,administrators}` counts the
  full existing administrable account/profile/role join for overview cards.

Default requests retain their old order/scope. Additive metadata allows deployment
before the companion frontend. `reports.manage` and `users.read` remain mandatory;
mutation role/permission checks are unchanged. Unauthenticated/forbidden requests
are 401/403; invalid enums/query bounds are 422. Values remain SQL parameters;
only a hardcoded asc/desc choice is interpolated.

No migration, stored data/backfill, credentials, new dependencies or configuration.
Existing report status/date index supports forward/reverse ordering; additional
type/reason predicates are applied in SQL before pagination. User substring search
and exact count aggregates may scan rows as data grows; no speculative index for
each combination was added. Review real PostgreSQL plans at production scale.
No import-time clients, clocks or SnapStart-sensitive state introduced.

## Verification and limitations

Regression fixtures execute real relational queries against isolated SQLite (not
production PostgreSQL), including matches beyond the initial unfiltered batch,
combined filters, literal wildcard characters, tied timestamps, oldest/newest,
empty/beyond-last pages, totals and summaries. HTTP tests verify permission gates
and invalid filter values. No production user/report fixtures or mutations.
DATABASE_URL is not configured locally, so live PostgreSQL integration is not
claimed. Existing offset bounds remain. Concurrent edits can shift offset pages
and briefly change counts between aggregate/list reads; refresh recovers current
state. This ticket is not snapshot-pagination redesign.

## Deployment and rollback

Matching branch `fix/server-filtered-pagination` in user-system and user-FE.
Deploy user-system first, frontend second; main-system is unchanged. Backend
baseline `7262b4c0bc2034cda0d75ae48f501317840972b3`; frontend baseline
`398ea79706d0df068f1f3ced98465bd60006de9f`.

Commit subjects: `Filter report and user directories before pagination` (backend),
`Use server-filtered pagination for administration lists` (frontend).
If reversal is requested, revert only frontend ticket commit then backend ticket
commit and redeploy, retaining unrelated later changes and appending rollback
logs. Do not reset main or force-push. No database/schema rollback is needed.

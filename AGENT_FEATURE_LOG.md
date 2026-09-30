# Agent Feature Log

This file is the repository's running implementation history for agent-assisted work.

## Working rule

- Read this file before making any change in this repository.
- After completing work, add a dated entry describing what changed and how it was verified.
- State whether a database migration is required and name it when applicable.
- Keep entries concise, factual, and limited to this repository.

## Entries

### 2026-09-28 - Retest Supabase database connectivity

- Verified the corrected `DATABASE_URL` has the asyncpg driver, complete direct Supabase host, port `5432`, database name, username, and a populated password without exposing secret values.
- Verified the authenticated Supabase API request still succeeds.
- The read-only PostgreSQL check reached connection setup but failed DNS resolution because the direct Supabase database endpoint requires IPv6 in this environment; use the project's Session Pooler connection string for IPv4 access.
- Verification: Supabase API passed; database `SELECT 1` was not reached because direct-host DNS resolution failed.
- Migration required: No.

### 2026-09-28 - Validate Supabase connectivity configuration

- Confirmed the ignored local environment contains all three required Supabase variables without exposing their values.
- Verified an authenticated request to the configured Supabase API succeeds.
- The read-only PostgreSQL `SELECT 1` check could not start because the configured `DATABASE_URL` is malformed with an empty port; the URL must be replaced with a complete single-line connection string.
- Verification: Supabase API passed; database URL parsing failed before any database connection was attempted.
- Migration required: No.

### 2026-09-28 - Make database configuration Supabase-only

- Removed the local `POSTGRES_*` fallback fields from application settings, `.env.example`, and the ignored local `.env` file.
- Made `DATABASE_URL` the single PostgreSQL connection setting alongside the Supabase project URL and backend secret key.
- Added a regression test confirming that no localhost/PostgreSQL-host fallback remains.
- Verification: 3 pytest tests passed; mypy reported no issues in 29 source files; Python byte-compilation and `git diff --check` passed.
- Migration required: No.

### 2026-09-28 - Add local Supabase configuration placeholders

- Added blank `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, and `DATABASE_URL` placeholders to `.env.example`.
- Created the ignored local `.env` file with the same blank placeholders for developer-supplied secrets.
- Verification: confirmed `.env` exists locally, is ignored by Git, and contains no secret values; `git diff --check` passed.
- Migration required: No.

### 2026-09-28 - Establish the FastAPI architecture foundation

- Added the `entities -> app -> interface/infrastructure` package structure based on Shadow's practical clean architecture, adapted for the InkFig domain.
- Added a FastAPI application factory, configurable CORS and `/api/v1` prefix, root and versioned health endpoints, environment template, PostgreSQL-ready dependencies, test/type-check configuration, and architecture documentation.
- Reserved organized locations for DTOs, enums, exceptions, repository ports, services, routes, controllers, dependencies, middleware, SQLAlchemy models, repositories, integrations, and timestamped migrations.
- Verification: 2 pytest tests passed; mypy reported no issues in 29 source files; Python byte-compilation and `git diff --check` passed.
- Migration required: No. The migrations directory is structural only.

### 2026-09-28 - Document the InkFig product vision

- Added `README.md` with the project's university context, art-community purpose, planned discovery and interaction features, AI-assisted image search, teacher event moderation workflow, and access-control direction.
- Clarified that this repository owns authentication, accounts, profiles, roles, permissions, scopes, and account status.
- Verification: reviewed the rendered Markdown structure and ran Git's whitespace validation.
- Migration required: No.

### 2026-09-27 - Initialize agent feature log

- Added this repository-level feature log and established the read-before-work and update-after-work convention.
- Verification: confirmed the file exists in the repository.
- Migration required: No.

## 2026-09-28 - Standardize agent feature log requirements

### Request

Require every repository to use a root `AGENT_FEATURE_LOG.md`, read it fully before each ticket, preserve its history, and append every completed ticket using the prescribed structured sections.

### Changes

- Renamed the existing root feature log to the exact uppercase filename while preserving all previous entries unchanged.
- Adopted the required entry format for this and all future tickets.
- Intentionally left application behavior, authorization, APIs, database configuration, and dependencies unchanged.

### Repositories

- `delivery-main-system`: standardized the root feature-log filename and adopted the structured ticket record.
- `delivery-user-system`: standardized the root feature-log filename and adopted the structured ticket record.
- `delivery-user-FE`: standardized the root feature-log filename and adopted the structured ticket record.

### Files

- `AGENT_FEATURE_LOG.md`: renamed from `agent_feature_log.md` and appended this structured entry.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions or role access changed.
- No organization or domain scope changed.
- Backend authorization behavior is unchanged.

### Frontend

No frontend changes.

### Verification

- `[passed] git status --short` - confirmed the case-only rename is tracked.
- `[passed] git diff --check`
- `[not run] application tests and builds` - documentation-only filename and log-format change.

### Deployment

No special deployment steps.

### Git

- Branch: `main`
- Commit: `2ce6971`
- Push: `successful`

### Notes

Historical entries retain their original format; the required structured format applies from this entry onward.

## 2026-09-28 - Verify live Supabase connections

### Request

Retest the backend connection after replacing the direct IPv6 PostgreSQL URL with the Supabase Session Pooler connection string.

### Changes

- Performed read-only live checks against the configured Supabase API and PostgreSQL database without printing credentials.
- Confirmed the Session Pooler connection works with SQLAlchemy and asyncpg.
- Removed the temporary diagnostic script after verification.
- Intentionally left runtime application code and configuration values unchanged.

### Repositories

- `delivery-main-system`: verified its local Supabase API and database configuration.
- `delivery-user-system`: verified its local Supabase API and database configuration.

### Files

- `AGENT_FEATURE_LOG.md`: recorded the successful live connection verification.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions or roles changed.
- No organization or domain scope changed.
- Backend authorization behavior is unchanged.

### Frontend

No frontend changes.

### Verification

- `[passed] authenticated GET to the configured Supabase REST API root`
- `[passed] SQLAlchemy asyncpg connection through the Supabase Session Pooler`
- `[passed] SELECT 1`
- `[not run] pytest and mypy` - no application source code changed.

### Deployment

- Configure `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, and the Session Pooler `DATABASE_URL` in each deployed backend environment.
- No migrations must run before deployment.

### Git

- Branch: `main`
- Commit: `023a33c`
- Push: `successful`

### Notes

The verified local `.env` secrets remain ignored by Git and were not printed or committed.

## 2026-09-29 - Add AWS SAM Lambda deployment template

### Request

Prepare the InkFig user FastAPI backend for deployment to AWS Lambda using AWS SAM and add a root `template.yaml`.

### Changes

- Added a Mangum adapter that exposes the existing FastAPI application as an AWS Lambda handler.
- Added a SAM template with Python 3.13, x86_64 Lambda, API Gateway HTTP API root/proxy events, tracing, resource tags, and API/function outputs.
- Added deployment parameters for environment, trusted CORS origins, Supabase URL, backend secret key, Session Pooler database URL, and project name; secret parameters use `NoEcho`.
- Added Mangum to backend dependencies and excluded `.aws-sam/` build output from Git.
- Made the existing settings regression test inspect model defaults without loading local secrets.
- Documented SAM validation, build, and guided deployment commands.
- Intentionally left FastAPI routes, authorization behavior, database schema, and custom-domain configuration unchanged.

### Repositories

- `delivery-main-system`: added its Lambda handler, SAM template, deployment documentation, dependency, and focused test.
- `delivery-user-system`: added its Lambda handler, SAM template, deployment documentation, dependency, and focused test.

### Files

- `template.yaml`: defines the user-system Lambda and API Gateway HTTP API.
- `src/lambda_handler.py`: wraps FastAPI with Mangum.
- `requirements.txt`: adds Mangum.
- `tests/test_health.py`: verifies the Lambda handler and avoids loading secret configuration in assertions.
- `.gitignore`: excludes SAM build artifacts.
- `README.md`: documents validation, build, deployment, and parameter handling.
- `AGENT_FEATURE_LOG.md`: records this ticket.

### API

- `ANY /`: API Gateway forwards root requests to FastAPI.
- `ANY /{proxy+}`: API Gateway forwards all nested paths, including `/api/v1/*`, to FastAPI.
- No request fields, responses, filters, validation, permission checks, or application error contracts changed.

### Database

No migration required.

### Permissions and scope

- No application permissions, roles, or access scopes changed.
- Existing and future backend authorization remains authoritative inside FastAPI.
- The SAM template creates only the Lambda execution role required by the serverless function; no domain-specific IAM permissions were added.

### Frontend

No frontend changes.

### Verification

- `[passed] Python YAML compose check for template.yaml`
- `[passed] py -m pytest` - 4 tests passed.
- `[passed] py -m mypy src tests` - no issues in 30 source files.
- `[passed] py -m compileall -q src tests`
- `[passed] git diff --check`
- `[failed] initial py -m pytest` - the pre-existing settings test loaded local `.env` data and was corrected to inspect field defaults without exposing values.
- `[not run] sam validate --lint` - AWS SAM CLI is not installed in this environment.
- `[not run] sam build` - AWS SAM CLI is not installed in this environment.

### Deployment

- Deploy `delivery-user-system` as its own SAM/CloudFormation stack.
- Run `sam validate --lint`, `sam build`, and `sam deploy --guided` on a machine with AWS SAM CLI and configured AWS credentials.
- Provide `CorsOrigins`, `SupabaseUrl`, `SupabaseSecretKey`, and the Session Pooler `DatabaseUrl` during deployment; do not save secrets in committed files.
- No migrations must run before deployment.

### Git

- Branch: `main`
- Commit: `7c278ee`
- Push: `successful`

### Notes

Custom domains and ACM certificates remain follow-up work after the production domains are chosen. The database password appeared in failed test output and must be rotated before deployment.

## 2026-09-29 - Align local folders with renamed repositories

### Request

Rename the local repository folders to match the new InkFig GitHub repository names.

### Changes

- Renamed the local folder from `delivery-user-system` to `inkfig-user-system`.
- Updated `origin` from the legacy redirected repository URL to the canonical `inkfig-user-system` GitHub URL.
- Removed only the empty old folder remnant left by the Windows move operation.
- Intentionally left application code, configuration values, dependencies, and runtime behavior unchanged.

### Repositories

- `inkfig-main-system`: renamed its local folder and updated its canonical `origin` URL.
- `inkfig-user-system`: renamed its local folder and updated its canonical `origin` URL.
- `inkfig-user-FE`: renamed its local folder and updated its canonical `origin` URL.

### Files

- `AGENT_FEATURE_LOG.md`: recorded the local folder and remote URL alignment.
- No application files changed.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions, roles, authorization checks, or access scopes changed.
- Backend authorization behavior is unchanged.

### Frontend

No frontend changes.

### Verification

- `[passed] git status --short --branch` - repository remained clean after the move.
- `[passed] git remote get-url origin` - canonical InkFig remote URL is configured.
- `[passed] git ls-remote --exit-code origin refs/heads/main` - renamed GitHub repository is reachable.
- `[passed] workspace directory inspection` - only the three new repository folder names remain.
- `[not run] application tests and builds` - no application files changed.

### Deployment

- Update local scripts or external deployment jobs that still reference the old `delivery-user-system` folder or repository URL.
- No migrations must run before deployment.

### Git

- Branch: `main`
- Commit: `ebefdcc`
- Push: `successful`

### Notes

The old GitHub URL redirected successfully, but the canonical URL is now configured directly.
## 2026-09-29 - Align AWS SAM runtime with local Python 3.12

### Request

Fix the AWS SAM build failure caused by the template requiring Python 3.13 while the development machine provides Python 3.12.

### Changes

- Changed the Lambda runtime from `python3.13` to `python3.12` so SAM can use the installed interpreter.
- Aligned mypy's configured Python version and the README development documentation with Python 3.12.
- Left application behavior, authentication, API contracts, and deployment topology unchanged.

### Repositories

- `inkfig-user-system`: aligned the SAM, type-checking, and documented Python runtime.
- `inkfig-main-system`: received the matching runtime alignment in its own repository.

### Files

- `template.yaml`: changed the Lambda runtime to `python3.12`.
- `mypy.ini`: changed the type-checking target to Python 3.12.
- `README.md`: documented Python 3.12 as the backend development version.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions or role scopes changed.
- Existing backend authorization remains unchanged and backend-enforced.

### Frontend

No frontend changes.

### Verification

- `[passed] sam build`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] py -m compileall -q src tests`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-user-system` when this runtime correction is needed in AWS.
- No migration is required before deployment.
- No environment-variable or configuration-value changes are required; rebuild the SAM artifact before deployment.

### Git

- Branch: `main`
- Commit: `fadd3c5`
- Push: `successful`

### Notes

Python 3.12 is an AWS Lambda-supported runtime and matches the installed local interpreter. Using `sam build --use-container` remains an optional alternative when a matching local interpreter is unavailable.
## 2026-09-29 - Configure the user API custom domain

### Request

Configure `user-api.inkfig-hu.com` as the Cloudflare-managed hostname for the user backend.

### Changes

- Added a regional API Gateway custom domain secured by an ACM certificate supplied at deployment.
- Mapped the custom domain root path to the HTTP API `$default` stage using TLS 1.2.
- Added stack outputs for the public custom URL and the generated API Gateway hostname required as the Cloudflare CNAME target.
- Assigned the user backend its own CloudFormation stack and S3 prefix so it cannot collide with the main backend deployment.
- Documented ACM region and Cloudflare DNS/proxy requirements.
- Left FastAPI behavior, authorization, APIs, and database access unchanged.

### Repositories

- `inkfig-user-system`: configured `user-api.inkfig-hu.com` and its deployment outputs.
- `inkfig-main-system`: separately configured `main-api.inkfig-hu.com`.

### Files

- `template.yaml`: added the certificate parameter, API Gateway custom domain, API mapping, and domain outputs.
- `samconfig.toml`: added the repository-specific deployment stack configuration.
- `README.md`: documented certificate and Cloudflare CNAME setup.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

- `ANY https://user-api.inkfig-hu.com/`: maps to the existing HTTP API `$default` stage.
- `ANY https://user-api.inkfig-hu.com/{proxy+}`: continues forwarding nested FastAPI routes.
- No request, response, validation, filtering, or error-contract changes.

### Database

No migration required.

### Permissions and scope

- No application permissions, roles, or scopes changed.
- Existing backend authorization remains authoritative and backend-enforced.

### Frontend

No frontend changes.

### Verification

- `[passed] sam validate --lint`
- `[passed] sam build`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] git diff --check`

### Deployment

- Deploy the `inkfig-user-system` stack in `eu-west-1` and provide an ACM certificate ARN valid for `user-api.inkfig-hu.com` from that region.
- After deployment, create Cloudflare CNAME `user-api` pointing to the `CloudflareCnameTarget` stack output; use DNS-only during initial validation.
- No migration is required before deployment.
- Existing Supabase, database, CORS, and environment parameters remain required.

### Git

- Branch: `main`
- Commit: `6ea895c`
- Push: `successful`

### Notes

Cloudflare DNS cannot be completed until AWS deploys the custom domain and returns its unique regional hostname. If Cloudflare proxying is enabled later, use Full (strict) SSL/TLS mode.
## 2026-09-29 - Order API domain mapping after stage creation

### Request

Fix the API Gateway custom-domain deployment failure reporting `Invalid stage identifier specified` while creating the domain mapping.

### Changes

- Added an explicit CloudFormation dependency so `ApiDomainMapping` waits for the SAM-generated `$default` HTTP API stage.
- Applied the correction to both backends to prevent the same creation-order race during fresh deployments or resource replacement.
- Preserved locally generated `samconfig.toml` deployment values without committing them.
- Left application behavior, API contracts, authorization, and database access unchanged.

### Repositories

- `inkfig-user-system`: added the stage dependency that resolves the observed failed deployment.
- `inkfig-main-system`: added the same dependency as a preventive correction.

### Files

- `template.yaml`: made `ApiDomainMapping` depend on `HttpApiApiGatewayDefaultStage`.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions, roles, or access scopes changed.
- Existing backend authorization remains backend-enforced.

### Frontend

No frontend changes.

### Verification

- `[passed] sam validate --lint`
- `[passed] sam build`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] git diff --check -- template.yaml`
- `[failed] prior sam deploy --guided` — `ApiDomainMapping` raced the generated `$default` stage and API Gateway returned `Invalid stage identifier specified`.

### Deployment

- Delete the failed `inkfig-user-system` stack, rebuild, and deploy the corrected template using the issued ACM certificate.
- No migration is required and no new environment variables are needed.

### Git

- Branch: `main`
- Commit: `3bbc3b0`
- Push: `successful`

### Notes

The certificate and custom-domain resource were valid; only the missing creation-order dependency caused the failure.
## 2026-09-29 - Deploy the user backend from GitHub Actions

### Request

Automatically test and deploy the user backend to AWS whenever changes are pushed to the `main` branch.

### Changes

- Added a GitHub Actions workflow triggered by pushes to `main` and manual dispatches.
- Added Python 3.12 dependency installation, pytest, mypy, SAM validation, SAM build, non-interactive deployment, and production health verification.
- Used GitHub OIDC and temporary AWS credentials instead of permanent AWS access keys.
- Serialized production deployments to prevent overlapping CloudFormation updates.
- Passed production backend configuration from GitHub secrets without relying on local `samconfig.toml` values.
- Documented the required GitHub environment, secrets, and AWS deployment-role responsibilities.
- Left runtime behavior, APIs, authorization, and database schema unchanged.

### Repositories

- `inkfig-user-system`: added automated deployment for the user backend.
- `inkfig-main-system`: added the corresponding main-backend deployment workflow.

### Files

- `.github/workflows/deploy.yml`: tests, validates, builds, deploys, and health-checks the user backend.
- `README.md`: documents OIDC and required GitHub secrets.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- The workflow requests only `contents: read` and `id-token: write` GitHub permissions.
- AWS access is obtained through an IAM role restricted by its GitHub OIDC trust policy and AWS permissions.
- No application roles or backend authorization rules changed.

### Frontend

No frontend changes.

### Verification

- `[passed] Python YAML parse of .github/workflows/deploy.yml`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] git diff --check -- .github/workflows/deploy.yml README.md`
- `[not run] GitHub Actions deployment` — requires the production environment, OIDC role, and repository secrets to be configured in GitHub.

### Deployment

- Configure the GitHub `production` environment and the documented secrets before relying on automatic deployment.
- Configure the AWS GitHub OIDC provider and deployment role, restricted to this repository's `main` branch.
- After setup, every push to `main` deploys the `inkfig-user-system` stack in `eu-west-1`.
- No migration is required.

### Git

- Branch: `main`
- Commit: `0449170`
- Push: `successful`

### Notes

The first workflow run will fail at AWS authentication until `AWS_DEPLOY_ROLE_ARN` and the other required secrets exist. Local `samconfig.toml` changes and the pre-existing empty untracked `aws` file were preserved and intentionally excluded.
## 2026-09-29 - Review and map the current project foundation

### Request

Read the InkFig repositories and establish an accurate understanding of the product, service boundaries, implementation status, and deployment model before future feature work.

### Changes

- Reviewed the product documentation, architecture rules, runtime entry points, health request flow, configuration, tests, SAM infrastructure, and deployment workflow.
- Confirmed this service owns registration, authentication, users, profiles, roles, permissions, access scopes, university membership, account status, and user lookup.
- Confirmed the repository currently provides architecture and deployment foundations plus health endpoints; authentication, account, authorization, and persistence workflows are not yet implemented.
- Intentionally left application behavior and configuration unchanged.

### Repositories

- `inkfig-user-system`: reviewed and documented the current identity-backend baseline.
- `inkfig-main-system`: reviewed alongside this service to verify ownership boundaries.
- `inkfig-user-FE`: reviewed alongside this service to verify client integration and deployment boundaries.

### Files

- `AGENT_FEATURE_LOG.md`: recorded the project-understanding pass.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

No permissions, roles, authorization behavior, or access scopes changed.

### Frontend

No frontend changes.

### Verification

- `[passed] repository source, architecture, configuration, tests, and deployment files reviewed`
- `[passed] git diff --check`
- `[not run] application tests and builds` - documentation-only change.

### Deployment

No deployment changes or special steps.

### Git

- Branch: `main`
- Commit and push: performed after verification.

### Notes

This entry records understanding only; it does not claim that planned identity capabilities are already implemented.
## 2026-09-29 - Preserve JSON configuration in automated SAM deployment

### Request

Fix the backend deployment workflow's handling of structured CORS configuration after the same workflow pattern caused a production startup failure in the main service.

### Changes

- Replaced shell-expanded SAM overrides with an ephemeral structured JSON parameter file generated on the GitHub runner.
- Preserved the exact production CORS JSON and passed Supabase, database, and certificate secrets without printing them.
- Applied the correction to both backend workflows so the user service cannot receive the malformed `CORS_ORIGINS` value observed in the main service.
- Left application behavior, API contracts, authorization, and database schema unchanged.

### Repositories

- `inkfig-user-system`: corrected automated SAM parameter handling.
- `inkfig-main-system`: corrected the workflow responsible for the observed production 500.

### Files

- `.github/workflows/deploy.yml`: generates and supplies a structured SAM deployment-parameter file.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- GitHub OIDC and AWS IAM permissions remain unchanged.
- No application permissions, roles, or authorization scopes changed.

### Frontend

No frontend changes.

### Verification

- `[passed] Python YAML parse of .github/workflows/deploy.yml`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] git diff --check -- .github/workflows/deploy.yml`
- `[not run] corrected GitHub Actions deployment` — triggered by pushing this fix and verified after the push.

### Deployment

- Pushing this correction triggers deployment of the `inkfig-user-system` stack and its production health check.
- No environment-secret changes or database migrations are required.

### Git

- Branch: `main`
- Commit: `39b7542`
- Push: `successful`

### Notes

The structured parameter file prevents SAM's command-line parser from truncating JSON values containing quotation marks.
## 2026-09-29 - Use a SAM-supported deployment parameter file

### Request

Complete the automated CORS deployment correction after the first structured-parameter workflow run failed immediately in the SAM deploy step.

### Changes

- Changed the ephemeral parameter filename from `.json` to `.yaml`, one of the file extensions supported by the installed SAM CLI parameter parser.
- Retained JSON-formatted content because JSON is valid YAML and preserves the CORS array and secret strings exactly.
- Left application behavior, APIs, authorization, infrastructure resources, and database schema unchanged.

### Repositories

- `inkfig-user-system`: corrected the deployment parameter-file extension.
- `inkfig-main-system`: applied the same correction.

### Files

- `.github/workflows/deploy.yml`: writes the structured parameter document with a SAM-supported `.yaml` extension.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No GitHub, AWS IAM, application permission, role, or scope changes.

### Frontend

No frontend changes.

### Verification

- `[passed] installed SAM CLI parameter parser loaded the YAML file and returned ["https://inkfig-hu.com"] exactly`
- `[passed] Python YAML parse of .github/workflows/deploy.yml`
- `[passed] git diff --check -- .github/workflows/deploy.yml`
- `[failed] prior corrected GitHub Actions deployment` — SAM rejected `.json` as an unsupported parameter-file extension before contacting CloudFormation.

### Deployment

- Pushing this correction triggers the user production deployment again.
- No secret, configuration-value, or migration changes are required.

### Git

- Branch: `main`
- Commit: `484d9e0`
- Push: `successful`

### Notes

The parameter document remains structured and ephemeral; only its extension changed for SAM CLI compatibility.

## 2026-09-30 - Add Hebron University account registration

### Request

Create the first-visit signup flow with required university email, full name, phone number, gender, date of birth, password, and password confirmation fields, with authoritative backend validation and database persistence.

### Changes

- Added a clean-architecture registration workflow that creates an active Supabase Auth user and its application profile.
- Enforced backend-only organization rules: exactly eight digits before `@students.hebron.edu`, or a non-empty valid local part before `@hebron.edu`.
- Required every field, normalized email/phone/full name, required a past birth date, restricted gender to `male` or `female`, required an 8-128 character password, and required matching confirmation.
- Added compensation that deletes the newly created Auth user when profile persistence fails.
- Kept network and database initialization lazy and request-scoped for future Lambda SnapStart compatibility.
- Intentionally left login, email verification, roles, permissions, and the main business service unchanged.

### Repositories

- `inkfig-user-system`: added registration API, Supabase Auth integration, profile persistence, migration runner, migration, tests, and deployment migration step.
- `inkfig-user-FE`: added the matching first-visit and signup experience in its own repository.

### Files

- `src/entities/dto/registration.py`: defines and validates registration contracts.
- `src/app/services/registration_service.py`: coordinates Auth and profile creation with compensation.
- `src/infrastructure/integrations/supabase_auth.py`: creates and deletes Supabase Auth users with the backend secret.
- `src/infrastructure/db/postgres/models/user_profile.py`: maps persisted user profiles.
- `src/infrastructure/repositories/user_profile_repository.py`: persists profile records transactionally.
- `src/interface/api/routes/registration.py`: exposes the public signup endpoint and error mapping.
- `migrations/20260930_001_create_user_profiles.sql`: creates and protects the profile table.
- `migrations/run.py`: applies timestamped SQL migrations once.
- `.github/workflows/deploy.yml`: runs database migrations before Lambda deployment.
- `tests/test_registration.py`: covers email formats, required fields, password matching, successful registration, and compensation.

### API

- `POST /api/v1/auth/signup`: accepts required `email`, `full_name`, `phone_number`, `gender`, `date_of_birth`, `password`, and `password_confirmation`; returns `201` with the non-secret user profile, `409` for an existing email, `422` for validation failures, and `503` when Supabase Auth is unavailable.
- Passwords and password confirmation are never persisted in `user_profiles` or returned.

### Database

- Migration: `20260930_001_create_user_profiles.sql`
- Creates `public.user_profiles` keyed to `auth.users(id)` with `ON DELETE CASCADE`, required profile columns, active default, timestamps, gender/birth-date/university-email constraints, a case-insensitive unique email index, and an active-account index.
- Enables RLS, removes direct `anon` and `authenticated` table access, and grants service-role access; the backend PostgreSQL connection performs registration writes.
- The migration is additive and idempotently tracked in `public.schema_migrations`; rollback requires dropping `user_profiles` only after preserving profile data and considering Auth-user dependencies.

### Permissions and scope

- Signup is public and requires no existing role or permission.
- Only Hebron University student/staff email formats are accepted.
- Profile storage is inaccessible directly to anonymous/authenticated database roles; validation and creation are backend-controlled.

### Frontend

- The corresponding frontend ticket adds welcome and signup routes, required fields, localized feedback, loading/success/error states, and responsive RTL/LTR styling.

### Verification

- `[passed] py -3.12 -m pytest` - 19 tests passed.
- `[passed] py -3.12 -m mypy src tests` - no issues in 44 source files.
- `[passed] py -3.12 -m compileall -q src tests migrations`
- `[passed] sam validate --lint`
- `[passed] sam build`
- `[passed] git diff --check`
- `[not run] live signup against production Supabase` - migration and deployment are intentionally performed by the protected main-branch workflow after merge.

### Deployment

- Deploy `inkfig-user-system`; the workflow applies the database migration before SAM deployment.
- The existing `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, and Session Pooler `DATABASE_URL` secrets are required; no new environment variables are needed.
- Deploy the frontend after or with the backend so the signup API exists when the form becomes public.

### Git

- Branch: `feature/user-signup`
- Commit: `c3ab400`
- Push: `successful`

### Notes

Supabase email confirmation is currently set to confirmed at backend account creation because this ticket validates organization format but does not introduce an email-verification workflow. Rate limiting and login remain follow-up authentication work.

## 2026-09-30 - Require ten-digit signup phone numbers

### Request

Confirm the Hebron University email validation and require signup phone numbers to contain exactly 10 digits.

### Changes

- Confirmed the backend continues to accept only eight-digit `@students.hebron.edu` addresses and valid non-empty `@hebron.edu` addresses.
- Changed authoritative phone validation from a variable international length to exactly 10 numeric digits.
- Continued normalizing spaces and hyphens before validation and persistence; plus-prefixed/international-length values are rejected.
- Added focused rejection coverage for 9-digit, 11-digit, plus-prefixed, and alphanumeric phone values.
- Intentionally left all other signup fields, Supabase Auth creation, profile persistence, compensation, and account status unchanged.

### Repositories

- `inkfig-user-system`: tightened the backend registration contract and tests.
- `inkfig-user-FE`: mirrored the exact 10-digit rule in the signup experience.
- `inkfig-main-system`: no changes required.

### Files

- `src/entities/dto/registration.py`: requires exactly 10 normalized digits.
- `tests/test_registration.py`: updates the valid fixture and adds invalid-length/content cases.
- `README.md`: documents the authoritative phone requirement.

### API

- `POST /api/v1/auth/signup`: `phone_number` must normalize to exactly 10 digits; invalid values return `422`. Request and response field names are unchanged.

### Database

No migration required. The existing `phone_number` column already stores the normalized value and is large enough for 10 digits.

### Permissions and scope

- Signup remains public and grants no role or permission.
- Hebron organization and phone validation remain backend-enforced.
- No account, company, role, permission, or data-scope behavior changed.

### Frontend

- The frontend mirrors the rule for immediate feedback; backend validation remains authoritative.

### Verification

- `[passed] py -3.12 -m pytest` - 23 tests passed.
- `[passed] py -3.12 -m mypy src tests` - no issues in 44 source files.
- `[passed] py -3.12 -m compileall -q src tests migrations`
- `[passed] git diff --check`

### Deployment

- Push to `main` triggers the existing user-backend AWS deployment workflow.
- No migration, environment-variable, or configuration change is required.
- Deploy the user backend before the frontend so the authoritative API rule is active first.

### Git

- Branch: `main`
- Commit: this ticket's focused commit
- Push: `successful`

### Notes

Phone validation checks digit count only; country/carrier ownership verification is outside this ticket.

## 2026-09-30 - Verify signup email before account activation

### Request

Generate and email a time-limited code after signup, validate the submitted code, and make the account usable only after successful verification.

### Changes

- Signup now creates an unconfirmed Supabase identity and an inactive profile, generates a cryptographically random six-digit code, stores only its HMAC-SHA256 hash, and sends the code through the configured Brevo template.
- Codes expire after 10 minutes, are single-use, allow at most five failed attempts, and can be resent after a 60-second cooldown; resending invalidates the previous code.
- Successful verification confirms the Supabase email and activates the profile; signup compensation deletes the pending identity if database persistence or email delivery fails.
- Existing active accounts remain active and are backfilled as previously verified.
- Hebron email, ten-digit phone, password, profile, and role behavior outside verification remain unchanged.

### Repositories

- `inkfig-user-system`: added verification domain contracts, workflow, Brevo and Supabase integrations, persistence, API endpoints, migration, deployment configuration, and tests.
- `inkfig-user-FE`: added the verification and resend user experience.
- `inkfig-main-system`: no changes required.

### Files

- `src/app/services/registration_service.py`: coordinates pending signup, secure code verification, activation, expiry, attempts, and resend cooldown.
- `src/entities/dto/registration.py`: adds verification request, response, and persistence contracts.
- `src/entities/exceptions/registration.py`: adds verification and email-delivery errors.
- `src/entities/repositories/registration.py`: expands the authentication, persistence, and email gateway interfaces.
- `src/infrastructure/integrations/brevo_email.py`: sends the English Brevo transactional template without logging the code or API key.
- `src/infrastructure/integrations/supabase_auth.py`: creates unconfirmed identities and confirms them after code verification.
- `src/infrastructure/db/postgres/models/user_profile.py`: maps inactive profiles, verification state, and hashed-code records.
- `src/infrastructure/repositories/user_profile_repository.py`: persists, locks, consumes, replaces, and activates verification challenges.
- `migrations/20260930_002_add_email_verification.sql`: adds email verification persistence and profile verification state.
- `src/interface/api/controllers/registration_controller.py`, `src/interface/api/routes/registration.py`, `src/interface/dependencies/registration.py`: expose and wire the verification workflow.
- `.env.example`, `template.yaml`, `.github/workflows/deploy.yml`: document and deploy Brevo configuration.
- `tests/test_registration.py`: covers pending signup, hashed codes, successful verification, invalid attempts, expiry, and compensation.

### API

- `POST /api/v1/auth/signup`: now returns the normalized email, `verification_required`, code lifetime, and resend cooldown after creating an inactive pending account and sending its code; returns `409` for duplicates and `503` for provider/email failures.
- `POST /api/v1/auth/verify-email`: accepts `email` and an exact six-digit `code`; activates the account on success and returns `400` for an incorrect code, `404` when no pending challenge exists, `410` when expired, `429` after the attempt limit, and `503` for provider failure.
- `POST /api/v1/auth/resend-verification`: accepts `email`, sends a replacement code, invalidates the previous code, and returns lifetime/cooldown data; returns `404`, `429`, or `503` as applicable.

### Database

- Migration: `20260930_002_add_email_verification.sql`
- Adds nullable `user_profiles.email_verified_at`, changes the default for new profiles to inactive, and backfills active existing profiles with their creation timestamp.
- Adds `email_verification_codes` with profile foreign key/cascade, hash, expiry, attempt limit, consumed/invalidated timestamps, pending and expiry indexes, RLS, and service-role-only access.
- Rollback must preserve or export verification audit data before dropping the table/column; restoring the former active default would re-enable unverified signup and is not recommended.

### Permissions and scope

- Signup, verification, and resend are public endpoints and grant no application role or permission.
- Only Hebron University email formats are accepted; account activation is limited to the matching pending identity.
- Supabase service-role and database service credentials remain backend-only; Brevo credentials never reach the frontend.
- Verification state, attempt limits, expiry, and activation are validated by the backend.

### Frontend

- Signup redirects to the localized `/:language/verify-email` route with the email prefilled.
- The responsive RTL/LTR form accepts exactly six digits, displays expiry/invalid/attempt errors, provides a resend cooldown, and links to login only after success.
- Existing visual language, theme behavior, welcome/login/signup routes, and navigation remain unchanged.

### Verification

- `[passed] py -3.12 -m pytest` - 26 tests passed.
- `[passed] py -3.12 -m mypy src tests` - no issues in 45 source files.
- `[passed] py -3.12 -m compileall -q src tests`
- `[passed] sam validate --lint`
- `[passed] sam build`
- `[passed] git diff --check`
- `[failed] initial py -3.12 -m mypy src tests` - the deliberate failing repository test double lacked the expanded protocol methods; the double was completed and the rerun passed.
- `[not run] live Brevo delivery and production signup` - no recipient address was supplied and production migration/deployment is handled by the protected workflow.

### Deployment

- Deploy `inkfig-user-system`; migration `20260930_002_add_email_verification.sql` must run before the SAM deployment and the existing workflow does so.
- Production requires `BREVO_API_KEY`, `BREVO_SENDER_EMAIL`, `BREVO_SENDER_NAME`, and `BREVO_VERIFY_EMAIL_TEMPLATE_ID` GitHub environment secrets in addition to the existing Supabase/database secrets.
- Deploy `inkfig-user-FE` after the backend deployment succeeds.

### Git

- Branch: `main`
- Commit: this ticket's focused commit
- Push: `successful`

### Notes

Pending identities and profiles exist only to hold the password securely in Supabase; they remain unconfirmed and inactive until the code succeeds. Rotating `SUPABASE_SECRET_KEY` invalidates outstanding code hashes, so users with pending codes must request replacements after a rotation.

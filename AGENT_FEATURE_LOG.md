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

## 2026-09-30 - Resume pending signup instead of reporting a duplicate account

### Request

Fix signup returning `409 An account with this email already exists` for an email whose earlier registration is still pending verification.

### Changes

- Distinguished a pending, inactive signup from a completed account when Supabase reports that the identity already exists.
- A repeated signup now resumes the existing verification flow and sends a replacement code when the resend cooldown has elapsed.
- During the cooldown, the existing verification remains valid and the response reports the remaining expiry and cooldown durations.
- Completed accounts and orphaned provider identities without a pending application profile continue to return `409`.

### Repositories

- `inkfig-user-system`: corrected pending-registration recovery and added regression coverage.
- `inkfig-user-FE`: no changes required because the successful signup response contract is unchanged.
- `inkfig-main-system`: no changes required.

### Files

- `src/app/services/registration_service.py`: resumes an existing pending verification after a duplicate Supabase identity response.
- `tests/test_registration.py`: covers pending-signup recovery and preserves conflicts for completed accounts.
- `AGENT_FEATURE_LOG.md`: records this fix.

### API

- `POST /api/v1/auth/signup`: returns the existing `201` pending-verification response for an inactive account with a pending challenge; genuine completed-account duplicates still return `409`.
- Request and response fields are unchanged.

### Database

No migration required.

### Permissions and scope

- Signup remains public and grants no role or permission.
- Only an existing inactive profile with a pending verification challenge can be resumed.
- The retry does not replace the existing Supabase password or take over an active account.

### Frontend

No frontend change is required. The existing signup success path proceeds to the email-verification screen.

### Verification

- `[passed] py -3.13 -m pytest` - 28 tests passed.
- `[passed] py -3.13 -m mypy src tests` - no issues in 45 source files.
- `[passed] py -3.13 -m compileall -q src tests migrations` using a workspace bytecode cache because existing source cache directories are not writable in this environment.
- `[passed] git diff --check`
- `[not run] py -3.12 verification` - Python 3.12 is not installed in this environment; Python 3.13 completed the full suite.
- `[not run] live production signup` - requires deployment through the protected main-branch workflow and a real university mailbox.

### Deployment

- Merge this backend branch into `main` to trigger tests, SAM build, database migration runner, AWS deployment, and the production health check.
- No new migration, secret, environment variable, or frontend deployment is required.

### Git

- Branch: `fix/resume-pending-signup`
- Commit: this ticket's focused commit.
- Push: feature branch pushed to `origin` for pull-request review.

### Notes

The retry intentionally keeps the password from the original pending registration; changing an existing identity's password through a public signup retry would be unsafe.

## 2026-09-30 - Recover orphaned unconfirmed Supabase signup identities

### Request

Fix signup still returning `409` for `22220013@students.hebron.edu` when no matching account appears in the application profile table.

### Changes

- Added recovery for an unconfirmed Supabase Auth identity that has no matching pending application profile.
- The backend locates the exact normalized Auth email, refuses recovery when the identity is confirmed, and replaces only an unconfirmed orphan before recreating the normal pending profile and verification challenge.
- Preserved pending-profile resume behavior and completed-account duplicate protection.
- Kept network clients request-scoped and generated identity, code, and timestamp state during the request for future Lambda SnapStart compatibility.

### Repositories

- `inkfig-user-system`: added orphaned Auth identity recovery and regression coverage.
- `inkfig-main-system`: no changes required.
- `inkfig-user-FE`: no changes required because the signup contract is unchanged.

### Files

- `src/entities/repositories/registration.py`: extends the Auth gateway contract with safe unconfirmed-user replacement.
- `src/infrastructure/integrations/supabase_auth.py`: finds an exact Auth user and replaces it only when unconfirmed.
- `src/app/services/registration_service.py`: invokes orphan recovery only when no pending profile exists.
- `tests/test_registration.py`: verifies recovery creates the normal pending verification flow.
- `AGENT_FEATURE_LOG.md`: records this ticket.

### API

- `POST /api/v1/auth/signup`: an unconfirmed Supabase identity without a profile can now restart registration and receive the existing `201` verification response.
- Confirmed identities continue to return `409`; request and response fields are unchanged.

### Database

No migration required.

### Permissions and scope

- Recovery applies only to the exact normalized email and only when Supabase reports that it is unconfirmed and no pending application profile exists.
- The user must still prove mailbox ownership using the newly issued verification code.
- Confirmed identities and active profiles cannot be replaced through public signup.

### Frontend

No frontend changes. The existing successful-signup path continues to the verification screen.

### Verification

- `[passed] py -3.13 -m pytest -p no:cacheprovider` - 29 tests passed.
- `[passed] py -3.13 -m mypy src tests` - no issues in 45 source files.
- `[passed] py -3.13 -m compileall -q src tests migrations` using a workspace bytecode cache.
- `[passed] git diff --check`
- `[failed] initial verification run` - a misplaced response-parsing block caused an indentation error; it was corrected before the full suite passed.
- `[not run] production Auth lookup` - this checkout has no production `.env`; no credentials were exposed or added.

### Deployment

- Push `inkfig-user-system` directly to `main` to run tests, migrations, SAM build, AWS deployment, and the production health check.
- No migration, new secret, environment variable, frontend deployment, or deployment-order change is required.

### Notes

Supabase Auth identities are stored separately from `public.user_profiles`, so an orphan can exist even when the application table contains no matching email.

## 2026-09-30 - Move authentication ownership into InkFig

### Request

Use Supabase only as the hosted PostgreSQL database and move user credentials, email activation, login, JWTs, refresh tokens, and logout into the InkFig backend.

### Changes

- Removed all Supabase Auth API integration and configuration from the user backend.
- Signup now generates its user ID, hashes the password with salted PBKDF2-HMAC-SHA256 at 600,000 iterations, and transactionally stores the InkFig user, profile, and verification challenge in PostgreSQL.
- Email verification now activates the InkFig user and profile without calling Supabase Auth.
- Added backend login with generic credential errors and explicit inactive/unverified-account rejection.
- Added InkFig-signed HS256 access JWTs with issuer, subject, email, token-version, issued-at, expiry, and token-type claims; the signing secret must contain at least 32 bytes.
- Added opaque refresh tokens stored only as SHA-256 hashes, rotated on every refresh, and revoked on logout.
- Preserved Hebron email, ten-digit phone, Brevo verification, code expiry, attempt limits, and resend cooldown behavior.

### Repositories

- `inkfig-user-system`: owns credentials, authentication workflows, token issuance, persistence, migration, APIs, deployment configuration, and tests.
- `inkfig-user-FE`: connects the login and logout UI to InkFig authentication.
- `inkfig-main-system`: no changes required.

### Files

- `src/app/services/authentication_service.py`: implements login, access/refresh issuance, refresh rotation, and logout.
- `src/app/services/registration_service.py`: replaces Supabase Auth creation/confirmation with local password hashing and activation.
- `src/entities/dto/authentication.py`, `src/entities/exceptions/authentication.py`, `src/entities/repositories/authentication.py`: define authentication contracts and domain errors.
- `src/infrastructure/security/passwords.py`: implements salted PBKDF2 password hashing and constant-time verification.
- `src/infrastructure/repositories/authentication_repository.py`: reads InkFig users and persists/rotates/revokes refresh tokens.
- `src/infrastructure/repositories/user_profile_repository.py`: creates InkFig users with profiles and activates both after verification.
- `src/infrastructure/db/postgres/models/user_profile.py`: maps `users` and `refresh_tokens` and redirects foreign keys from Supabase Auth.
- `src/infrastructure/integrations/supabase_auth.py`: deleted because Supabase Auth is no longer used.
- `src/interface/api/routes/authentication.py`, `src/interface/api/controllers/authentication_controller.py`, `src/interface/dependencies/authentication.py`: expose and wire authentication endpoints.
- `migrations/20260930_003_move_authentication_to_inkfig.sql`: creates InkFig authentication storage and redirects ownership.
- `.env.example`, `template.yaml`, `.github/workflows/deploy.yml`: replace Supabase Auth settings with InkFig JWT settings.
- `tests/test_authentication.py`, `tests/test_registration.py`, `tests/test_health.py`: cover password hashing, login, JWT claims, inactivity, refresh rotation, and the revised signup flow.

### API

- `POST /api/v1/auth/login`: accepts `email` and `password`; returns an InkFig access JWT, opaque refresh token, expiry, and user summary; returns `401` for invalid credentials and `403` until email verification/activation.
- `POST /api/v1/auth/refresh`: accepts `refresh_token`, consumes it once, and returns a rotated session; returns `401` for invalid, expired, reused, or inactive-account tokens.
- `POST /api/v1/auth/logout`: accepts `refresh_token`, revokes it idempotently, and returns `204`.
- `POST /api/v1/auth/signup`, `/verify-email`, and `/resend-verification`: preserve their public contracts but now use only InkFig-owned database identities.

### Database

- Migration: `20260930_003_move_authentication_to_inkfig.sql`
- Creates `public.user_accounts` with unique normalized email, password hash, active/verified state, token version, timestamps, and Hebron-email constraint; the dedicated name avoids the pre-existing unrelated `public.users` table.
- Creates `public.refresh_tokens` with unique token hash, expiry/revocation timestamps, user cascade, and lookup/expiry indexes.
- Backfills existing profiles into `users`, preserves IDs/status/timestamps, and redirects profile/verification foreign keys from `auth.users` to `public.users`.
- Existing accounts receive a non-authenticating password sentinel because Supabase Auth passwords are intentionally not imported; they require a future password-reset flow.
- Enables RLS and restricts both new tables to backend service-role database access. Rollback requires restoring the old `auth.users` foreign keys and Supabase Auth identities before removing these tables.

### Permissions and scope

- Signup, verification, login, refresh, and logout remain public authentication endpoints and grant no domain role.
- Only active, email-verified InkFig users receive tokens; backend checks are authoritative.
- JWT claims currently contain no domain permissions; future protected endpoints must load backend roles/scopes and validate the InkFig issuer/signature/expiry/token version.
- Supabase Auth keys are no longer deployed or used by this service; Supabase provides PostgreSQL hosting only.

### Frontend

- The login form now calls InkFig login, handles invalid credentials and unverified accounts, stores the returned session, and enables authenticated navigation.
- Logout calls the InkFig revocation endpoint and clears local session state even if the network request fails.

### Verification

- `[passed] py -3.12 -m pytest -q` - 31 tests passed.
- `[passed] py -3.12 -m mypy src tests` - no issues in 55 source files.
- `[passed] py -3.12 -m compileall -q src tests migrations`
- `[passed] sam validate --lint`
- `[passed] sam build`
- `[passed] git diff --check`
- `[not run] production login` - requires migration and deployment through the protected workflow.

### Deployment

- Deploy `inkfig-user-system`; migration `20260930_003_move_authentication_to_inkfig.sql` must run before Lambda deployment and the workflow runs it first.
- Production requires the new `JWT_SECRET` secret with at least 32 bytes; it was supplied in the GitHub `production` environment before push.
- `SUPABASE_URL` and `SUPABASE_SECRET_KEY` are no longer passed to this service; `DATABASE_URL` remains required for the Supabase-hosted PostgreSQL database.
- Deploy `inkfig-user-FE` only after the backend workflow succeeds.

### Git

- Branch: `main`
- Commit: this ticket's focused commit
- Push: `successful`

### Notes

Existing Supabase Auth rows are deliberately left untouched but are no longer read or written by InkFig. A password-reset feature is required before legacy users can authenticate through the new backend.

## 2026-09-30 - Recover migrated legacy accounts through verified signup

### Request

Allow `22220013@students.hebron.edu` and other accounts migrated from Supabase Auth to register in InkFig instead of receiving `409 An account with this email already exists`.

### Changes

- Signup now detects only accounts carrying the migration's non-authenticating `!password-reset-required!` sentinel.
- A recoverable legacy account keeps its user ID, receives the newly submitted password hash and profile fields, becomes inactive/unverified, revokes old refresh tokens, invalidates old challenges, and receives a new verification code.
- The account becomes usable only after the normal email-code verification succeeds.
- Current InkFig accounts with real password hashes remain protected and continue returning `409`.

### Repositories

- `inkfig-user-system`: added safe legacy-account recovery during signup.
- `inkfig-user-FE`: no changes required; the signup success contract is unchanged.
- `inkfig-main-system`: no changes required.

### Files

- `src/app/services/registration_service.py`: chooses the migrated user ID and starts its verification flow.
- `src/entities/repositories/registration.py`: adds legacy lookup/restart repository contracts.
- `src/infrastructure/repositories/user_profile_repository.py`: atomically replaces only sentinel credentials, refresh tokens, verification challenges, and profile state.
- `tests/test_registration.py`: covers migrated-account recovery and identity preservation.

### API

- `POST /api/v1/auth/signup`: migrated sentinel accounts now return the normal `201` verification-required response; active/current InkFig duplicates still return `409`. Request and response fields are unchanged.

### Database

No migration required. Recovery uses the sentinel written by `20260930_003_move_authentication_to_inkfig.sql` and existing account/profile/verification tables.

### Permissions and scope

- Signup remains public and grants no role or permission.
- Recovery is backend-limited to exact normalized emails with the migration sentinel and still requires mailbox ownership through the six-digit code.
- Current credentials cannot be replaced through this path; backend validation is authoritative.

### Frontend

No frontend changes. Successful recovery follows the existing localized verification screen and resend workflow.

### Verification

- `[passed] py -3.12 -m pytest -q` - 32 tests passed.
- `[passed] py -3.12 -m mypy src tests` - no issues in 55 source files.
- `[passed] py -3.12 -m compileall -q src tests migrations`
- `[passed] git diff --check`
- `[not run] live signup for 22220013@students.hebron.edu` - deployment must complete before sending a real verification email.

### Deployment

- Deploy `inkfig-user-system` through the existing AWS workflow.
- No migration, new secret, environment-variable, or frontend deployment is required.

### Git

- Branch: `main`
- Commit: this ticket's focused commit
- Push: `successful`

### Notes

Recovery deliberately reuses the migrated user ID so profiles and future references remain stable.

## 2026-09-30 - Fix false duplicate-email response during new signup

### Request

Reproduce and resolve the persistent `409 An account with this email already exists` response for `22220013@students.hebron.edu` using production API and database diagnostics.

### Changes

- Confirmed through targeted production queries that the email had no InkFig account, profile, verification challenge, legacy public-user row, or Supabase Auth identity.
- Reproduced the production `409` and then reproduced the underlying repository failure in a rolled-back ORM transaction.
- Fixed creation ordering by flushing the new `user_accounts` row before inserting its dependent profile and verification challenge.
- Restricted duplicate-email translation to PostgreSQL unique violations (`23505`); foreign-key and other integrity failures are no longer incorrectly reported as duplicate accounts.
- Removed the temporary diagnostic script after verification and intentionally left frontend behavior unchanged.

### Repositories

- `inkfig-user-system`: corrected transactional account creation and error classification.
- `inkfig-user-FE`: no changes required.
- `inkfig-main-system`: no changes required.

### Files

- `src/infrastructure/repositories/user_profile_repository.py`: enforces parent-before-child flush ordering and maps only unique violations to `EmailAlreadyRegisteredError`.
- `AGENT_FEATURE_LOG.md`: records the diagnosis, fix, and verification.

### API

- `POST /api/v1/auth/signup`: genuinely new emails can now create their account/profile/challenge; `409` is returned only for actual unique conflicts. Request and successful response fields are unchanged.

### Database

No migration required. Existing foreign keys are correct; the defect was ORM flush ordering. All diagnostic inserts were transactionally rolled back and created no records.

### Permissions and scope

- Signup remains public and limited to validated Hebron University emails.
- Email verification remains mandatory before activation.
- Backend database constraints and error classification remain authoritative.

### Frontend

No frontend changes. The existing signup and verification pages consume the unchanged API contract.

### Verification

- `[passed] production read-only account-state queries` - no record existed in the five relevant locations for the reported email.
- `[passed] production API reproduction` - confirmed the pre-fix `409`.
- `[passed] rolled-back raw SQL insert` - schema accepted the complete account graph.
- `[failed] initial rolled-back ORM flush` - exposed `email_verification_codes_user_id_fkey` because the child flushed first.
- `[passed] corrected rolled-back ORM flush` - parent-first ordering succeeded without persisting data.
- `[passed] py -3.12 -m pytest -q` - 32 tests passed.
- `[passed] py -3.12 -m mypy src tests` - no issues in 55 source files.
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-user-system` through the existing AWS workflow.
- No migration, new secret, environment-variable, or frontend deployment is required.

### Git

- Branch: `main`
- Commit: this ticket's focused commit
- Push: `successful`

### Notes

The in-app browser control was unavailable in this session; the same deployed signup endpoint was exercised directly and the production database was inspected without exposing secrets or password hashes.

## 2026-09-30 - Verify corrected signup in production

### Request

Confirm the reported email can register after the false-conflict fix and leave it ready for the user's real registration.

### Changes

- Submitted the complete production signup request for `22220013@students.hebron.edu` after deployment and received the expected verification-required response.
- Deleted only the temporary test account afterward; foreign-key cascades removed its temporary profile and verification challenge so the user can register with their real fields and password.
- Intentionally left application behavior unchanged after the verified fix.

### Repositories

- `inkfig-user-system`: recorded production verification and targeted test-data cleanup.

### Files

- `AGENT_FEATURE_LOG.md`: records the live result and cleanup.

### API

- `POST /api/v1/auth/signup`: production returned `201` with `verification_required: true`, a 600-second lifetime, and 60-second resend cooldown.

### Database

No migration required. One temporary test `user_accounts` row was deleted by exact email and its dependent test rows were cascade-deleted.

### Permissions and scope

- No permissions or roles changed.
- Backend Hebron-email validation and mandatory email verification remain authoritative.

### Frontend

No frontend changes.

### Verification

- `[passed] production POST /api/v1/auth/signup` - returned `201` for the previously failing email.
- `[passed] targeted database cleanup` - returned `DELETE 1` for the temporary test account.

### Deployment

No special deployment steps. The behavioral fix was already deployed successfully.

### Git

- Branch: `main`
- Commit: this ticket's verification-log commit
- Push: `successful`

### Notes

The verification email produced by the temporary test is intentionally invalid because its corresponding test challenge was removed. The user must submit the signup form again to receive the real code.

## 2026-09-30 - Reset forgotten passwords with an email code

### Request

Allow a user who forgot their password to request an email verification code, verify it, and securely choose a new password.

### Changes

- Added a three-step password-reset workflow: request code, verify code, and confirm a new password.
- Returns the same request response for eligible and unknown accounts to reduce email-account enumeration.
- Stores only HMAC hashes of six-digit codes and opaque reset tokens, enforces 10-minute lifetimes and five code attempts, and prevents code/token reuse.
- Hashes the replacement password with the existing PBKDF2 implementation, increments the account token version, and revokes all active refresh tokens.
- Sends an English Brevo reset email and HTML-escapes user-controlled names.
- Existing signup, email verification, login, and logout behavior was intentionally left unchanged.

### Repositories

- `inkfig-user-system`: added password-reset persistence, domain/application services, Brevo delivery, API endpoints, configuration, and tests.
- `inkfig-user-FE`: consumes this API in the login recovery workflow; its changes are recorded in that repository.

### Files

- `migrations/20260930_004_add_password_reset.sql`: creates password-reset challenge storage.
- `src/app/services/password_reset_service.py`: implements request, code verification, and password confirmation rules.
- `src/entities/dto/authentication.py`: adds reset request and response DTOs.
- `src/entities/repositories/password_reset.py`: defines reset persistence and email ports.
- `src/infrastructure/repositories/password_reset_repository.py`: persists challenges, changes password hashes, and revokes sessions.
- `src/infrastructure/integrations/brevo_email.py`: sends the English reset-code email.
- `src/interface/api/routes/password_reset.py`: exposes the reset endpoints.
- `src/interface/api/controllers/password_reset_controller.py`: delegates HTTP requests to the service.
- `src/interface/dependencies/password_reset.py`: wires reset dependencies and configuration.
- `src/infrastructure/config/settings.py`, `.env.example`, `template.yaml`: define reset lifetimes and attempt limits.
- `tests/test_password_reset.py`: verifies security and workflow behavior.

### API

- `POST /api/v1/auth/password-reset/request`: accepts `email`, always returns a neutral accepted response for valid-format emails, and sends a code only for active verified accounts.
- `POST /api/v1/auth/password-reset/verify`: accepts `email` and a six-digit `code`; returns a short-lived opaque `reset_token`; returns 400 for an invalid code, 410 for expiry, and 429 after five failed attempts.
- `POST /api/v1/auth/password-reset/confirm`: accepts `email`, `reset_token`, `password`, and `password_confirmation`; validates matching 8-128 character passwords and returns 204 after changing the password.

### Database

- Migration: `20260930_004_add_password_reset.sql`
- Adds `password_reset_codes` with an account foreign key, hashed code/token fields, expiry timestamps, attempt constraints, verification/consumption/invalidation timestamps, a unique token hash, pending and expiry indexes, RLS, and service-role access.
- Rollback requires dropping `public.password_reset_codes`; no existing account data is rewritten.

### Permissions and scope

- No authenticated permission is required because password recovery must be public.
- Only active, email-verified InkFig accounts can receive a reset challenge.
- Account eligibility, code validity, token validity, password replacement, and session revocation are validated by the backend.

### Frontend

No frontend changes in this repository. The corresponding localized page and login link are in `inkfig-user-FE`.

### Verification

- `[passed] py -3.12 -m pytest -q` - 37 tests passed.
- `[passed] py -3.12 -m mypy src tests` - no issues in 62 files.
- `[passed] py -3.12 -m compileall -q src tests`
- `[passed] sam validate --lint`
- `[passed] sam build`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-user-system`; the existing workflow must run migration 004 before the Lambda deployment.
- Deploy `inkfig-user-FE` after the backend succeeds.
- Existing Brevo and JWT secrets are reused; no new secret is required. Optional reset TTL/attempt environment values have defaults in the SAM template.

### Git

- Branch: `main`
- Commit: this ticket's focused commit
- Push: `successful`

### Notes

Requesting another reset code invalidates any earlier unconsumed challenge. Successful reset revokes refresh tokens, while already-issued short-lived access tokens also become invalid because the account token version is incremented.

## 2026-09-30 - Reuse the verification email template for password resets

### Request

Send password-reset codes with the same branded Brevo template used for signup email verification.

### Changes

- Replaced the reset email's inline HTML with the configured shared Brevo template ID.
- Added a `code_purpose` template parameter so signup and password-reset messages can display context-appropriate wording in the same design.
- Overrides the reset message subject with `Your InkFig password reset code`.
- Existing code generation, expiry, attempt limits, account eligibility, and password-reset behavior were intentionally left unchanged.

### Repositories

- `inkfig-user-system`: changed Brevo payload construction and added regression coverage.

### Files

- `src/infrastructure/integrations/brevo_email.py`: uses one template for both code-email purposes.
- `tests/test_brevo_email.py`: verifies both messages use the same template and that reset no longer sends inline HTML.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions, roles, or access scopes changed.
- Signup and password-reset eligibility continue to be validated by the backend.

### Frontend

No frontend changes.

### Verification

- `[passed] py -3.12 -m pytest -q` - 38 tests passed.
- `[passed] py -3.12 -m mypy src tests` - no issues in 63 files.
- `[passed] py -3.12 -m compileall -q src tests`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-user-system` through the existing AWS workflow.
- No migration or new environment variable is required.
- Update the existing Brevo template sentence to use `{{ params.code_purpose }}` so its wording matches signup and reset messages.

### Git

- Branch: `main`
- Commit: this ticket's focused commit
- Push: `successful`

### Notes

The shared Brevo template should say `Use the verification code below to {{ params.code_purpose }}:`. Existing `full_name`, `verification_code`, and `expires_minutes` parameters remain available.

## 2026-09-30 - Limit verification-code emails to five per hour

### Request

Limit registration and password-reset code emails to five, then prevent another code for one hour and explain the lock to the user.

### Changes

- Added a shared database-backed limiter for registration and password-reset emails.
- Allows one send every 60 seconds; the fifth code is delivered and starts a one-hour lock.
- During the lock, no code is generated, no active challenge is replaced, and no email is sent.
- Uses HMAC email identifiers rather than storing additional plaintext email addresses.
- Uses a PostgreSQL transaction advisory lock so concurrent Lambda requests cannot bypass the counter.
- Applies password-reset tracking to unknown addresses as well, preserving the neutral response and preventing account discovery.
- Existing code expiry, five incorrect-code attempts, verification, and password-reset authorization were intentionally left unchanged.

### Repositories

- `inkfig-user-system`: added persistent rate limiting, API response metadata, configuration, migration, and tests.
- `inkfig-user-FE`: displays the lock message and countdown; its changes are recorded in that repository.

### Files

- `migrations/20260930_005_add_email_code_rate_limits.sql`: creates hashed per-purpose rate-limit state.
- `src/entities/dto/email_code_rate_limit.py`: defines limiter decisions.
- `src/entities/repositories/email_code_rate_limit.py`: defines the persistence port.
- `src/entities/exceptions/email_code_rate_limit.py`: carries hourly retry information.
- `src/infrastructure/repositories/email_code_rate_limit_repository.py`: atomically reserves email sends.
- `src/infrastructure/db/postgres/models/user_profile.py`: maps the rate-limit table.
- `src/app/services/registration_service.py`: applies limits to signup and resend emails.
- `src/app/services/password_reset_service.py`: applies neutral limits to reset requests.
- `src/entities/dto/registration.py`, `src/entities/dto/authentication.py`: expose resend delay and hourly-lock state.
- `src/interface/api/routes/registration.py`: returns 429 and `Retry-After` for a locked verification email.
- `src/infrastructure/config/settings.py`, `.env.example`, `template.yaml`: configure five sends and the one-hour block.
- `tests/test_registration.py`, `tests/test_password_reset.py`: verify fifth-send and locked-send behavior.

### API

- `POST /api/v1/auth/signup`: response adds `hourly_limit_reached`; returns 429 with `Retry-After` when the email is already locked.
- `POST /api/v1/auth/resend-verification`: response adds `hourly_limit_reached`; the fifth send returns a 3600-second delay, while locked requests return 429.
- `POST /api/v1/auth/password-reset/request`: response adds `resend_after_seconds` and `hourly_limit_reached`; it continues returning neutral 202 responses for unknown, ineligible, cooldown-limited, and hourly-limited emails.

### Database

- Migration: `20260930_005_add_email_code_rate_limits.sql`
- Adds `email_code_rate_limits` with composite purpose/hash primary key, nonnegative send counter, last-send and blocked-until timestamps, a partial block-expiry index, RLS, and service-role-only access.
- Existing users and challenges require no backfill. Rollback drops only the limiter table and removes enforcement state.

### Permissions and scope

- No authenticated permission is required for public registration or password recovery.
- Limits are isolated by normalized email and purpose, so registration and password reset have independent counters.
- Eligibility, resend limits, challenge creation, and email delivery decisions are backend-enforced.

### Frontend

No frontend changes in this repository. The frontend consumes the new delay and lock fields.

### Verification

- `[passed] py -3.12 -m pytest -q` - 41 tests passed.
- `[passed] py -3.12 -m mypy src tests` - no issues in 67 files.
- `[passed] py -3.12 -m compileall -q src tests`
- `[passed] sam validate --lint`
- `[passed] sam build`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-user-system`; migration 005 must run before the Lambda update.
- Deploy `inkfig-user-FE` after the backend succeeds.
- No new secrets are required; SAM supplies defaults of five sends and a 3600-second block.

### Git

- Branch: `main`
- Commit: this ticket's focused commit
- Push: `successful`

### Notes

The hour begins when the fifth code is issued. After it expires, the counter resets. AWS WAF/IP throttling remains a complementary future defense against distributed abuse.

## 2026-09-30 - Enforce unique registration phone numbers

### Request

Require both email addresses and phone numbers to be unique during signup and return a clear conflict for either field.

### Changes

- Added database-enforced phone-number uniqueness alongside the existing email constraints.
- Maps PostgreSQL phone uniqueness violations to a dedicated domain error and HTTP 409 response.
- Applies the same protection when restarting a migrated legacy account.
- Existing email format, ten-digit phone validation, verification, login, and account scopes were intentionally unchanged.

### Repositories

- `inkfig-user-system`: added the constraint, conflict mapping, migration, and API response.
- `inkfig-user-FE`: displays the field-specific conflict and records its UI work separately.

### Files

- `migrations/20260930_006_add_unique_phone_number.sql`: creates the unique phone index.
- `src/infrastructure/db/postgres/models/user_profile.py`: maps the named unique index.
- `src/entities/exceptions/registration.py`: adds the phone conflict domain error.
- `src/infrastructure/repositories/user_profile_repository.py`: classifies unique conflicts and safely rolls back.
- `src/interface/api/routes/registration.py`: returns the phone-specific 409 response.

### API

- `POST /api/v1/auth/signup`: returns 409 with `An account with this phone number already exists.` when the normalized submitted phone is already stored; the existing email 409 remains unchanged.

### Database

- Migration: `20260930_006_add_unique_phone_number.sql`
- Adds named unique index `user_profiles_phone_number_unique_idx` on `user_profiles.phone_number`; no backfill or default is required. Existing duplicates would prevent migration application. Rollback drops this index.

### Permissions and scope

- Signup remains public and requires no authenticated permission.
- Uniqueness applies globally to every account, regardless of role.
- Validation and conflict enforcement are performed by the backend and PostgreSQL.

### Frontend

No frontend changes in this repository.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest` - 41 tests passed.
- `[passed] uv run --with-requirements requirements.txt mypy src tests`
- `[passed] focused ruff check` - all changed backend Python files passed.
- `[passed] migration runner` - migration 006 applied to the configured Supabase database.
- `[failed] full ruff check` - pre-existing formatting and lint findings remain in unrelated files.
- `[failed] sam validate --lint` - template validated, but SAM telemetry could not access its user metadata path in the sandbox.
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-user-system`; migration 006 has already run before deployment.
- No environment-variable or secret changes are required.

### Git

- Branch: `main`
- Commit: this ticket's focused commit
- Push: `successful`

### Notes

The unique index stores and compares the already validated ten-digit representation exactly.

## 2026-10-05 - Store authentication tokens in secure cookies

### Request

Move access and refresh tokens out of browser storage and protect them with secure HTTP-only cookies.

### Changes

- Login and refresh now set tokens as cookies instead of returning token values in JSON.
- Access cookie is HttpOnly, Secure in production, SameSite=Lax, shared with InkFig API subdomains, and expires with the 15-minute access token.
- Refresh cookie is HttpOnly, Secure in production, SameSite=Strict, host-only to the user API, limited to the authentication path, and expires after 30 days.
- Refresh rotates both tokens; logout revokes the refresh token and expires both cookies.
- Local development keeps configurable cookie security and domain values.

### Repositories

- `inkfig-user-system`: issues, rotates, clears, and configures secure authentication cookies.
- `inkfig-main-system`: authenticates access cookies.
- `inkfig-user-FE`: uses credentialed requests and automatic refresh.

### Files

- `src/interface/security/auth_cookies.py`: cookie creation, deletion, and safe session response mapping.
- `src/interface/api/routes/authentication.py`: cookie-based login, refresh, and logout.
- `src/entities/dto/authentication.py`: token-free public session response.
- `src/infrastructure/config/settings.py`, `.env.example`, `template.yaml`: cookie configuration.
- `tests/test_auth_cookies.py`: security-attribute and deletion tests.

### API

- `POST /api/v1/auth/login`: returns user/session metadata and sets access and refresh cookies; token values are omitted from JSON.
- `POST /api/v1/auth/refresh`: reads the HTTP-only refresh cookie, rotates it, sets a new access cookie, and returns metadata; 401 when absent, invalid, expired, or revoked.
- `POST /api/v1/auth/logout`: reads and revokes the refresh cookie when present and expires both cookies.

### Database

No migration required. Existing hashed, rotating refresh-token storage is unchanged.

### Permissions and scope

- Cookies authenticate only the account that received them.
- Token signing, account-active checks, rotation, expiry, and revocation remain backend-enforced.
- JavaScript cannot read either token.

### Frontend

- Paired frontend removes token values from localStorage and automatically refreshes expired access.

### Verification

- `[passed] pytest — 43 tests passed`
- `[passed] mypy src tests — no issues in 70 source files`
- `[passed] focused ruff check`
- `[passed] git diff --check`

### Deployment

- Deploy main backend compatibility first, then user backend, then frontend.
- Production sets `COOKIE_DOMAIN=inkfig-hu.com` and `COOKIE_SECURE=true` through SAM.
- No migration or new secret is required.

### Git

- Branch: `main`
- Commit: `01c165f`
- Push: `successful`

### Notes

The `__Host-` prefix cannot be used because the access cookie must be shared from `user-api.inkfig-hu.com` to `main-api.inkfig-hu.com`; the refresh cookie remains host-only.
## 2026-10-05 - Establish role and permission authorization

### Request

Implement the five-role InkFig authorization model with new accounts defaulting to user and protected role/account administration.

### Changes

- Added viewer, user, supervisor, admin, and system-administrator roles with normalized permissions.
- New and existing accounts receive user by default; login and refresh tokens now include authoritative role and permission claims.
- Added user listing, role assignment, banning, and activation endpoints.
- Admins may manage only lower-ranked accounts and cannot assign admin or system-administrator; system administrators can manage all other accounts.
- Role/status changes revoke the target's refresh sessions and increment its token version.

### Repositories

- `inkfig-user-system`: owns RBAC persistence, session claims, and account administration.
- `inkfig-main-system`: consumes permission claims for work endpoints.
- `inkfig-user-FE`: consumes roles and permissions for navigation and administration.

### Files

- `migrations/20261005_007_add_rbac.sql`: creates and seeds RBAC tables and default-role trigger.
- `src/app/services/administration_service.py`: enforces hierarchy rules.
- `src/infrastructure/repositories/administration_repository.py`: persists role/status changes and revokes sessions.
- `src/interface/api/routes/administration.py`: exposes protected administration endpoints.
- Authentication DTO, repository, service, cookies, migration runner, and deployment workflow now carry RBAC data.

### API

- `GET /api/v1/admin/users`: lists accounts for users.read.
- `PATCH /api/v1/admin/users/{user_id}/role`: changes a role subject to backend hierarchy rules.
- `PATCH /api/v1/admin/users/{user_id}/status`: bans or activates a lower-ranked account.
- Login and refresh responses add role and populated permissions.

### Database

- Migration: `20261005_007_add_rbac.sql`
- Creates roles, permissions, role_permissions, and user_roles with foreign keys, uniqueness, RLS, service-role grants, canonical seeds, existing-account backfill, and automatic user assignment.
- Rollback must drop the trigger/function and four RBAC tables after dependent code is rolled back.

### Permissions and scope

- `users.read`, `users.role.manage`, and `users.status.manage` protect administration.
- Admin cannot manage peers/higher roles or assign admin/system-administrator.
- Only system-administrator can assign admin or system-administrator.
- Backend validates every management decision.

### Frontend

No frontend changes in this repository.

### Verification

- `[passed] py -3.12 -m pytest -q - 43 tests passed`
- `[passed] py -3.12 -m mypy src tests - 77 files`
- `[passed] py -3.12 -m compileall -q src tests`
- `[passed] git diff --check`

### Deployment

- Deploy this service first and run migration 007 before either consumer.
- Add GitHub production secret `SYSTEM_ADMIN_EMAIL` containing the existing account that owns the system.
- No new application secret is required.

### Git

- Branch: `main`
- Commit: `502b304`
- Push: `successful`

### Notes

Role/status changes force refresh-session revocation; the short-lived access cookie expires within 15 minutes.

## 2026-10-05 - Grant artwork save permission

### Request

Allow registered users, but not viewer-only accounts, to save and unsave published artwork.

### Changes

- Added the works.save permission through an append-only RBAC migration.
- Granted it to user, supervisor, admin, and system-administrator roles.
- Intentionally excluded viewer accounts.
- Added regression coverage for the permission grants and exclusion.

### Repositories

- inkfig-user-system: save permission migration and test.
- inkfig-main-system: enforces the permission in paired save endpoints.
- inkfig-user-FE: displays save controls only when the signed session contains works.save.

### Files

- migrations/20261005_008_add_work_save_permission.sql: seeds works.save and registered-role grants idempotently.
- tests/test_rbac_migration.py: verifies the intended grants and viewer exclusion.
- AGENT_FEATURE_LOG.md: records this ticket.

### API

No route contract changes in this repository. Newly issued/refreshed session claims include works.save for granted roles.

### Database

- Migration: migrations/20261005_008_add_work_save_permission.sql.
- Adds one permission and four idempotent role-permission mappings.

### Permissions and scope

- user, supervisor, admin, and system_administrator receive works.save.
- viewer does not receive works.save.
- Existing signed-token validation and role hierarchy remain unchanged.

### Frontend

No frontend files changed in this repository.

### Verification

- [passed] git diff --check
- [passed] focused static review of the idempotent permission seed and role grants.
- [not run] pytest, mypy, Ruff, and compileall - no usable Python runtime or project runner is installed in this session.

### Deployment

- Apply migration 20261005_008_add_work_save_permission.sql and deploy inkfig-user-system before the main-system save endpoints and frontend.
- Existing users must refresh or sign in again to receive the new signed permission claim.
- No new environment variables or secrets are required.

### Git

- Branch: main
- Commit: this ticket's focused commit.
- Push: pushed directly to origin/main after synchronization.

### Notes

The migration uses conflict-safe inserts so it can run safely in environments where the permission was partially seeded.
## 2026-10-06 - Optimize user database indexes

### Request

Review and optimize the database and indexing for current InkFig workloads, and make query/index review a standard consideration for future database work.

### Changes

- Added a composite index matching the administrator user-list ordering.
- Replaced the broad refresh-token user index with a smaller partial index containing only active tokens used by session invalidation.
- Removed low-selectivity standalone boolean indexes that were not used by current repository queries and added write/storage overhead.
- Retained unique email, unique phone, pending verification/reset, expiry, rate-limit, and RBAC indexes because they match current constraints or access paths.
- Left authentication, authorization, API contracts, and frontend behavior unchanged.

### Repositories

- `inkfig-user-system`: optimized account administration and refresh-token indexes.
- `inkfig-main-system`: coordinated artwork database optimization is recorded in that repository.

### Files

- `migrations/20261006_009_optimize_query_indexes.sql`: added workload-aligned indexes and removed low-value/superseded indexes.
- `tests/test_query_indexes.py`: added regression coverage for the index migration.

### API

No API changes.

### Database

- Migration: `20261006_009_optimize_query_indexes.sql`
- Adds `user_accounts(created_at DESC, user_id DESC)` for administration ordering and a partial `refresh_tokens(user_id) WHERE revoked_at IS NULL` index for active-session invalidation.
- Drops standalone `is_active` indexes and the superseded broad refresh-token user index.
- No data backfill, constraint, default, or foreign-key changes are required. Rollback can recreate the removed indexes and drop the new ones, with no data loss.

### Permissions and scope

- `users.read` remains required for the administrator user list.
- Session invalidation remains scoped to the affected user and is performed only through backend-authorized account/role workflows.
- Role ceilings and backend authorization validation are unchanged.

### Frontend

No frontend changes.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q — 46 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests — no issues in 79 files`
- `[passed] uv run --with-requirements requirements.txt ruff check tests/test_query_indexes.py`
- `[passed] uv run --with-requirements requirements.txt python -m compileall -q src tests`
- `[passed] python -m migrations.run — migration applied to Supabase`
- `[passed] live pg_indexes query — administrator and active refresh-token indexes verified on Supabase`
- `[failed] uv run --with-requirements requirements.txt ruff check src tests — unrelated pre-existing repository-wide formatting and lint findings`

### Deployment

- Deploy `inkfig-user-system`.
- Run `20261006_009_optimize_query_indexes.sql` before deploying the application; it has already been applied to the configured Supabase database.
- No environment-variable or configuration changes.

### Git

- Branch: `main`
- Commit: `09bf7a2`
- Push: `successful`

### Notes

- Future database tickets must compare query predicates, join direction, ordering, and pagination with existing indexes and avoid redundant or low-selectivity indexes.
- Query plans should be reassessed using production-scale statistics as table cardinality grows; small tables may correctly use sequential scans despite having suitable indexes.

## 2026-10-06 - Add authenticated account settings APIs

### Request

Support profile editing, password changes, and account deactivation while keeping email immutable and phone numbers valid and unique.

### Changes

- Added authenticated profile read/update endpoints scoped to the signed-in user.
- Reused registration validation for names, exactly 10 phone digits, gender, and past dates of birth.
- Kept email outside the update request so it cannot be changed.
- Enforced phone uniqueness through the existing database index and mapped collisions to HTTP 409.
- Added current-password verification, confirmation, secure hashing, token rotation, and refresh-token revocation.
- Added self-deactivation that updates both account tables, revokes sessions, and clears cookies.
- Added focused service tests.

### Repositories

- `inkfig-user-system`: settings API, validation, persistence, security, and tests.
- `inkfig-user-FE`: paired localized settings interface.
- `inkfig-main-system`: no changes required.

### API

- `GET /api/v1/settings/profile`
- `PUT /api/v1/settings/profile`
- `PUT /api/v1/settings/password`
- `PUT /api/v1/settings/account-status`

### Database

- No new migration required.
- Phone uniqueness already exists in `migrations/20260930_006_add_unique_phone_number.sql`.

### Permissions and scope

- Every endpoint requires the signed `profile.read_own` permission.
- User identity comes only from the verified access-cookie principal.
- Password changes and deactivation invalidate refresh sessions and rotate the token version.

### Verification

- `[passed] git diff --check`
- `[not run] pytest` - no Python interpreter or pytest executable is installed in this environment.

### Deployment

- Deploy `inkfig-user-system` before `inkfig-user-FE`.
- No migration, secret, or environment-variable change is required.

### Git

- Branch: `feature/account-settings`
- Commit and push: completed after final synchronization.

### Notes

Inactive users cannot authenticate, so self-service deactivation is reversible only by an authorized administrator.
## 2026-10-06 - Restore settings backend deployment

### Request

Fix the production 404 returned by `GET /api/v1/settings/profile` after the settings frontend was released.

### Changes

- Confirmed the settings endpoint was absent because the user-backend GitHub Actions deployment for `517a401` failed before AWS deployment.
- Identified the failed gate as strict mypy validation after all backend tests had passed.
- Added complete parameter and return annotations to the new settings repository test double.
- Kept the settings API contract and production behavior unchanged.

### Repositories

- `inkfig-user-system`: fixes the deployment-blocking type-check failure.
- `inkfig-user-FE`: no changes required.
- `inkfig-main-system`: no changes required.

### API

No contract changes. Successful deployment makes the existing `/api/v1/settings/*` routes available in production.

### Database

No migration required.

### Permissions and scope

No authentication, authorization, roles, permissions, or account scopes changed.

### Verification

- `[passed] previous GitHub Actions test step` - the settings commit passed the complete backend test suite.
- `[passed] git diff --check`
- Deployment workflow and production endpoint verified after push.

### Deployment

- Push `inkfig-user-system` to `main` to rerun tests, mypy, SAM build, and AWS deployment.
- No frontend redeployment, migration, secret, or environment-variable change is required.

### Git

- Branch: `fix/settings-deployment-typecheck`
- Commit and push: completed after final synchronization.

### Notes

The previous production version remained healthy, but correctly returned 404 because it predated the settings router.

## 2026-10-06 - Add social profiles and following

### Request

Allow signed-in users to open other accounts, follow and unfollow them, view follower/following lists with follow controls, and see follower, following, and received-like counters.

### Changes

- Added active, verified social-profile summaries with follower, following, and total published-artwork-like counts.
- Added idempotent follow/unfollow behavior and prohibited self-following in both the service and database.
- Added follower and following account lists with viewer-specific follow state.
- Excluded inactive and unverified target accounts from profile and connection responses.
- Kept authorization backend-enforced through the existing authenticated profile permission.
- Added type annotations to the recently added settings tests so the complete suite remains MyPy-clean.
- Left registration, authentication, administration, and settings behavior unchanged.

### Repositories

- `inkfig-user-system`: owns social profiles, relationships, counters, lists, and authorization.
- `inkfig-main-system`: exposes published artworks for a selected profile.
- `inkfig-user-FE`: provides profile navigation and social controls.

### Files

- `migrations/20261006_010_add_user_follows.sql`: creates the follow relation, self-follow constraint, RLS, grants, and directional indexes.
- `src/entities/dto/social_profile.py`: defines public profile and connection contracts.
- `src/entities/repositories/social_profile.py`: defines the social repository boundary.
- `src/app/services/social_profile_service.py`: enforces profile-not-found and no-self-follow rules.
- `src/infrastructure/repositories/social_profile_repository.py`: implements optimized profile counts, lists, and mutations.
- `src/interface/api/routes/social_profiles.py`: exposes profile, connection, follow, and unfollow endpoints.
- `src/interface/dependencies/social_profile.py`: wires the social service.
- `src/infrastructure/db/postgres/models/user_profile.py`: adds the synchronized follow model.
- `src/main.py`: registers the social-profile router.
- `tests/test_social_profiles.py`: covers user scope, follow/unfollow, self-follow prevention, and hidden profiles.
- `tests/test_query_indexes.py`: verifies both directional follow indexes.
- `tests/test_settings.py`: completes test-stub typing without changing settings behavior.

### API

- `GET /api/v1/profiles/{user_id}`: returns name, follower count, following count, received-like count, viewer follow state, and self-profile state; returns 404 for unavailable profiles.
- `GET /api/v1/profiles/{user_id}/followers`: returns active follower accounts and whether the viewer follows each account.
- `GET /api/v1/profiles/{user_id}/following`: returns active followed accounts and whether the viewer follows each account.
- `PUT /api/v1/profiles/{user_id}/follow`: idempotently follows an active verified account; returns 409 for self-follow and 404 for unavailable profiles.
- `DELETE /api/v1/profiles/{user_id}/follow`: idempotently unfollows an account; returns 409 for self-targeting and 404 for unavailable profiles.

### Database

- Migration: `20261006_010_add_user_follows.sql`
- Adds `user_follows` with a composite primary key, cascading account foreign keys, creation timestamp, and a check preventing self-following.
- Adds `(follower_user_id, created_at DESC, followed_user_id)` and `(followed_user_id, created_at DESC, follower_user_id)` indexes for ordered lists in both directions.
- Enables RLS and restricts direct access to the service role. No backfill is required.
- Rollback drops `user_follows`, permanently removing follow relationships but leaving accounts and artworks unchanged.

### Permissions and scope

- `profile.read_own` is required for profile details, lists, follow, and unfollow operations.
- User, supervisor, admin, and system-administrator roles with that permission can use the feature.
- A mutation is always scoped to the authenticated principal as follower; clients cannot submit another follower ID.
- Target profiles must be active and email-verified. Authorization and scope are validated by the backend.

### Frontend

No frontend changes in this repository. The coordinated UI is in `inkfig-user-FE`.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q — 52 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests — no issues in 95 files`
- `[passed] ruff check on all changed user-backend files`
- `[passed] python -m migrations.run — follow migration applied to Supabase`
- `[passed] live schema query — table, no-self constraint, primary key, and both directional indexes verified`

### Deployment

- Deploy `inkfig-user-system`.
- Run `20261006_010_add_user_follows.sql` before application deployment; it has already been applied to Supabase.
- No environment-variable or configuration changes.

### Git

- Branch: `main`
- Commit: `0729a5d`
- Push: `successful`

### Notes

- Received likes count only includes likes on published works.
- Connection lists currently return the complete relationship list; cursor pagination should be added before unusually large accounts require it.

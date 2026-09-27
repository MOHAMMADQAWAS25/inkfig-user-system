# InkFig User System Architecture

This service uses FastAPI and the same practical clean architecture as Shadow:

```text
src/
|-- entities/
|   |-- dto/             Request and response contracts
|   |-- enums/           Domain enumerations
|   |-- exceptions/      Domain and application errors
|   `-- repositories/    Persistence ports used by services
|-- app/
|   `-- services/        Business use cases and workflow decisions
|-- interface/
|   |-- api/
|   |   |-- controllers/ HTTP-to-application coordination
|   |   `-- routes/      FastAPI route declarations
|   |-- dependencies/    FastAPI dependency providers
|   `-- middleware/      HTTP middleware
`-- infrastructure/
    |-- config/          Runtime settings
    |-- db/postgres/     SQLAlchemy setup and models
    |-- integrations/    Email and external adapters
    `-- repositories/    PostgreSQL repository implementations
```

Tests live in `tests/`. PostgreSQL migrations will live in `migrations/` once the migration tool is selected. Every public API is versioned under `/api/v1`; `/health` is also exposed at the root for infrastructure checks.

## Dependency rules

- `entities` does not import FastAPI, SQLAlchemy, or infrastructure code.
- `app` depends on entity contracts and repository ports, never HTTP request objects or SQLAlchemy queries.
- `interface` validates HTTP input, applies authentication and permissions, invokes services, and translates errors.
- `infrastructure` implements persistence and external-service details.
- Controllers never return raw SQLAlchemy models.

## Service responsibility

The user system owns registration, authentication, users, profiles, roles, permissions, access scopes, university membership, account status, and user lookup endpoints. Artwork and event workflows belong to the main system.

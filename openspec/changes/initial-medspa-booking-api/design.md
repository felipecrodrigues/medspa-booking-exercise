# Design: Initial Medspa Booking API

## Proposed boundaries

- **Composition and HTTP:** `main.py` creates the FastAPI application and wires feature routers; `health.py` owns `/health`; `dependencies.py` owns FastAPI request/session dependencies and reusable path ID validation.
- **Features:** `services/` and `appointments/` each contain their ORM model, Pydantic schemas, focused operations, and router. `medspas/` contains the seed-only Medspa ORM model and one shared existence lookup; there is no medspa CRUD router.
- **Domain rules:** appointment status and booking rules are framework/ORM-free modules under `appointments/`; shared booking errors live in top-level `errors.py`.
- **Persistence:** a small `db/` package owns the declarative base, engine/session factory, PostgreSQL integer limit, complete metadata registration, generated DDL, and seed entry point. It does not import FastAPI.
- **Runtime:** Python 3.14 Docker image; Compose services for PostgreSQL and API; database readiness before API readiness; a database-aware health check.
- **Specifications/evaluation:** OpenSpec is the behavior source; `docs/ontology/` defines domain/evaluation concepts; `docs/eval/` stores versioned JSONL measurements with evidence.

This is a restrained feature-oriented design, not an instruction to create separate deployables, repositories, generic service layers, interfaces, a DI framework, or duplicate domain dataclasses for ORM rows. Appointment operations may depend on the service ORM model to capture booking snapshots; routers do not depend on other feature routers.

## Data model outline

- `medspas`
- `services` with a medspa foreign key and integer price/duration values
- `appointments` with medspa foreign key, future timezone-aware start time, one allowed status, and derived totals
- an appointment/service association table with unique appointment/service membership and booking-time price/duration snapshots

Apply database constraints for foreign keys, positive durations, nonnegative cent values, allowed statuses, and one selection per appointment/service pair. `sql/schema.sql` will contain reviewable PostgreSQL `CREATE TABLE` statements generated from or kept mechanically consistent with Alembic. Do not keep independent, drifting schema definitions.

The local Compose database SHALL include a deterministic demo medspa record (and only the minimal catalog data needed by request examples). The API has no medspa CRUD or delete routes.

## HTTP behavior defaults

- Missing resources return a normal not-found response.
- Malformed or semantically invalid request values return documented client-error responses; invalid appointment service selections fail atomically without partial rows.
- PATCH uses field-presence semantics: omitted fields preserve stored values, and supplied non-null values are validated and applied. Explicit null clears only `Service.description`; null `Service.name`, `price`, `duration`, or appointment `status` returns `422` without changes. A mixed valid/invalid payload is rejected atomically; `{}` is a successful no-op. Service description remains nullable on creation.
- List routes return all matching rows in stable ID order. No pagination or filter parameters are added.
- `/health` verifies a live PostgreSQL connection. This infrastructure route does not add medspa CRUD or delete behavior.
- New appointments default to `scheduled`; all transitions among the three supported status values are allowed.
- Appointment start times require an explicit timezone offset and must be future times. Availability, business hours, and overlap checks are out of scope.

## Open business decisions retained for team discussion (2026-11-15)

These questions do not change the current API contract. The implementation retains the exercise-level behavior until the product team chooses a policy:

- **Appointment status lifecycle:** No transition restrictions are enforced; any of `scheduled`, `completed`, and `canceled` may transition to another supported status. The team should decide whether completed appointments may be canceled, whether canceled appointments may be restored or completed, or whether only scheduled-to-completed and scheduled-to-canceled transitions should be allowed.
- **Additional services after a session starts:** New appointments with past start times remain invalid. A client asking to add a service after an originally booked procedure has started may need a separate in-progress appointment amendment flow, with its own validation and possibly additional permissions. Do not treat this as authorization to create arbitrary past appointments; revisit only after the team defines the supported workflow.

## TDD and validation sequence

For each slice, first add and run a test that demonstrates the missing behavior; then implement the smallest change, rerun focused tests, run the broader suite, and refactor only with green tests.

1. Configuration, DB connection, Alembic migration, demo medspa seed, and database-aware health.
2. Service create/get/list/patch endpoints and their persistence/validation tests.
3. Appointment create/get/status-patch/list, nonempty/distinct/same-medspa selection validation, booking-time snapshots, total calculations, timezone/future rules, and transaction/integration tests.
4. Full PostgreSQL integration suite, README examples, Compose cold start/restart/persistence, cURL checks, and final independent review.

Integration tests should run against PostgreSQL rather than substituting SQLite so that constraints, transaction behavior, and types match the service database.

## Operational acceptance

- A documented one-command Compose startup builds and starts the API and database.
- The API does not report ready before PostgreSQL can be reached and required schema is available.
- A clean-volume startup, service health/readiness, representative valid and invalid cURL requests, integration tests, and persistence across container restart are verified.

Exact error response formatting is an implementation detail to be documented consistently. The route scope, booking snapshots, selection validation, timezone/future rule, status behavior, PATCH null behavior, and exclusions above are user-approved and normative.

## Implementation decisions recorded before coding

- **Superseded layout decision (2026-11-15):** the first implementation used the flat technical-layer layout `app.py` / `schemas.py` / `operations.py` / `models.py` recorded in the initial review history. The focused Claude Opus 5.5 architecture review found that this mixed the services and appointments features and contradicted `proposal.md`'s feature-oriented module decision. That flat layout is superseded by the accepted feature packages recorded under “Follow-up review decisions” below; this historical note is retained to make the decision change explicit.
- Use synchronous SQLAlchemy 2 with psycopg 3 and synchronous FastAPI handlers; this avoids async-driver complexity for the single-database exercise while FastAPI keeps blocking handlers off the event loop.
- Keep `AppointmentService` as an association object with a composite `(appointment_id, service_id)` key and booking-time `price_at_booking`/`duration_at_booking`. Derive `total_price` and `total_duration` from those snapshots when returning an appointment instead of storing duplicate totals that could drift.
- Return appointment selections as `service_selections` containing service ID and the two booking-time snapshot values, alongside the derived totals. Order selection responses by service ID. List endpoints order records by their primary key.
- Validate request values at the Pydantic boundary and enforce the persistent numeric/status invariants again with PostgreSQL `CHECK` constraints. Return 404 for missing medspas/resources and 422 for invalid service selections or request values; `/health` returns 503 when PostgreSQL cannot be reached.
- Treat SQLAlchemy model metadata as the schema source of truth. Generate `sql/schema.sql` from that metadata and test that the committed DDL matches the generated PostgreSQL DDL. Keep the Alembic baseline migration in sync and verify it against PostgreSQL in integration coverage.
- Seed a deterministic local medspa with ID 1 and two example services with IDs 1 and 2. The seed operation is repeatable and inserts missing demo rows without overwriting existing rows; no medspa CRUD or delete routes are added.
- Run PostgreSQL integration tests against an explicitly set `TEST_DATABASE_URL` targeting a dedicated database whose name ends in `_test`; test setup resets only that database's `public` schema and applies Alembic migrations. Unit tests remain runnable without a database, and SQLite is not used.
- Docker Compose's default `db` and `api` services provide the local runtime. A separate `test-db` service under the `test` profile provides a disposable PostgreSQL database on host port 55432 for integration tests without risking the persistent runtime database. API startup waits for healthy PostgreSQL, runs Alembic and the idempotent seed, then starts Uvicorn; the API healthcheck calls the database-aware `/health` route.

## Hardening decisions accepted during review

- Bound service prices and durations, all path IDs, and each appointment `service_ids` item to the signed PostgreSQL `INTEGER` maximum (`2147483647`); positive identifiers/durations have a lower bound of 1, while price may be 0. Reject out-of-range values and unknown request-body fields with `422`. Service names must contain a non-whitespace character, enforced both by Pydantic and a PostgreSQL check constraint.
- Normalize accepted appointment start times to UTC at request validation and again at response serialization so create/read representations agree regardless of the incoming offset or PostgreSQL session timezone.
- Alembic URL precedence is explicit `Config` URL first, then `DATABASE_URL` only when no Config URL is present. `alembic.ini` intentionally has no default URL so an environment URL can be used without overriding a caller-supplied Config value.
- Before integration tests drop or recreate `public`, require both a PostgreSQL database whose name ends in `_test` and an allowlisted loopback host (`localhost` or an IP address recognized as loopback). DNS hostnames other than `localhost` are refused.
- Empty PATCH objects and unchanged non-null values do not trigger a write. Explicit-null service description is a write when it clears a populated description; explicit null for non-nullable PATCH fields is rejected at request validation. In operations, omitted appointment status is represented by `None` after request validation.

## Persistence choices intentionally deferred

- **Database-level same-medspa composite foreign key:** the API transaction verifies that every selected service belongs to the appointment's medspa before inserting any rows. A database guarantee would require carrying `medspa_id` through the association and adding composite uniqueness/foreign-key constraints to the parent tables, duplicating relationship data. This additional persistence invariant is deferred; direct SQL writers are outside the current enforcement boundary. Revisit before introducing non-API writers or relaxing the operation-level validation.
- **`appointment_services.service_id` index:** the current primary key begins with `appointment_id`, and current API reads load selections by appointment. No current query filters or joins starting from `service_id`, so an additional index would add write/storage cost without a demonstrated access path. Defer until a service-centric query or measured query plan justifies it.

These are explicit deferrals, not claims that PostgreSQL enforces same-medspa membership for arbitrary direct writes or that a service-ID index can never be useful.

## Follow-up review decisions (2026-11-15)

- Keep PostgreSQL integer limits and reusable path-ID validation in the request-schema/type surface, share the nonblank service-name rule between create and PATCH, and use small operation helpers for repeated medspa existence and service-selection errors. Share test setup for the second medspa/service rather than adding a fixture framework.
- Derive the SQLAlchemy appointment-status CHECK values from `AppointmentStatus`; keep the Alembic migration's historical literal frozen. Configure Alembic to compare server defaults in online and offline configuration, and compare named PostgreSQL CHECK-constraint presence to metadata through PostgreSQL inspection in migration tests. Integration tests remain restricted to the explicitly configured loopback `_test` database.
- Replace the initial flat technical-layer package with the feature-oriented tree below, consistent with `proposal.md`'s approved feature-module decision. Keep ORM entities in their feature packages; put pure appointment rules in `appointments/rules.py`; keep `db/` free of FastAPI; and import every model through `db/metadata.py` before Alembic or DDL generation.
- Keep `appointments/status.py` independent of ORM and HTTP. Schemas depend on status/rules/shared limits, operations depend on feature models/rules/errors, and routers adapt HTTP contracts to operations. Operations keep transaction ownership and accept scalar keyword values or a field-change mapping, not Pydantic request objects.
- Import `db.metadata` explicitly from `main.py` so application mapper registration is not an incidental effect of router imports. The seed command and DDL generator also use the aggregate metadata registry; a no-database subprocess test imports each entrypoint and calls `configure_mappers()` in a fresh interpreter. Service PATCH operations explicitly allow only `name`, `description`, `price`, and `duration` updates.
- **Testing boundary:** automated tests SHALL NOT read or assert README or other documentation content. Review README facts manually; do not replace the removed README contract test with documentation assertions. Runtime configuration and generated SQL DDL contract tests remain code/runtime checks.
- Keep the module-level `app = create_app()` behavior in `main.py`; only the import path changes to `medspa_booking.main:app` as required by the package move. Router modules and `SessionDep` are accepted as part of the feature-oriented separation. Docker hardening and concurrency changes remain deferred. The API image may be built to validate the entrypoint and run as a test-db-only one-off; do not recreate/restart the running default API/database containers or touch their volume.

```text
medspa_booking/
  main.py                 # app composition, shared exception-to-HTTP mapping
  dependencies.py         # FastAPI SessionDep and PathId
  errors.py               # use-case errors, independent of HTTP
  health.py               # GET /health router
  db/{base,engine,limits,metadata,schema_ddl,seed}.py
  medspas/{models,operations}.py # seed-only model and shared lookup; no public router
  services/{models,schemas,operations,router}.py
  appointments/{status,rules,models,schemas,operations,router}.py
```

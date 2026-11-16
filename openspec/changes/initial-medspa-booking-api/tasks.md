# Tasks: Initial Medspa Booking API

## Planning gate

- [x] Get user decisions for all blocking items in `proposal.md`.
- [x] Update `openspec/specs/medspa-booking/spec.md` and this change's delta spec with approved decisions.
- [x] Define and validate the machine-readable agent evaluation schema and rubric before collecting scores. (Version 1.0; PLAN baseline JSONL parses; ongoing agent runs are appended by the evaluator.)
- [x] Confirm OpenSpec CLI/version/profile and validate the change artifacts.
- [x] Begin implementation after explicit user authorization; the separate evaluation setup/evidence work proceeds in parallel.

## Implementation (after approval)

- [x] Add failing tests for runtime configuration, PostgreSQL connectivity, initialization, and health/readiness.
- [x] Implement the minimal application/runtime foundation; make foundation tests pass.
- [x] Add failing tests for the approved medspa access contract; implement and pass them.
- [x] Add failing unit and PostgreSQL integration tests for service operations; implement each listed service route.
- [x] Add failing unit and PostgreSQL integration tests for appointment creation, service associations, derived totals, retrieval, status patch, and listing; implement each listed appointment route.
- [x] Add tests for approved invalid-input, not-found, transaction, timezone, and status behavior; implement the agreed API error contract.
- [x] Provide the agreed PostgreSQL `CREATE TABLE` DDL and ensure the runtime schema setup is consistent with it.
- [x] Verify Compose cold-start, runtime readiness, and restart/persistence. (GPT-6 Luna High completed live validation; app DB volume was preserved.)
- [x] Write root README setup instructions and cURL examples for every implemented endpoint; document actual assumptions, tradeoffs, scope, and AI usage.
- [x] Initially defer the Scope Change Scenario until the user authorizes an answer; after the user later requested a response, document the design answer while keeping `customer_notes` implementation excluded.

## Review hardening follow-up

- [x] Add regression tests for PostgreSQL INTEGER bounds, strict request fields, blank service names, UTC response consistency, Alembic URL precedence, and safe PostgreSQL test URLs; observe the tests fail before implementation.
- [x] Implement the accepted API, persistence, transaction, timezone, migration, and destructive-test-setup fixes.
- [x] Synchronize SQLAlchemy metadata, the Alembic baseline, generated DDL, OpenSpec decisions, and README AI usage.
- [x] Run the focused and full suites with and without `TEST_DATABASE_URL`, Ruff, Compose config validation, and the API image build.
- [x] Run OpenSpec CLI validation for the hardening edits; main session verified 2 passed, 0 failed via the official CLI.

## Independent review and operational validation

- [x] Complete the initial Claude Opus 5.5 independent review and address its accepted findings test-first.
- [x] Run the post-fix Claude Opus 5.5 code/spec/test/documentation re-review; no remaining defects were reported at the initial pre-refactor hardening stage. (A later architecture review identified the flat-package mismatch, addressed in the follow-up tasks below.)
- [x] Run the parallel Luna High input/output evaluation under the approved rubric; store evidence-linked records in `docs/eval/` and mark unavailable data explicitly. (There are fourteen unique validated records; GPT-6.1 Sol PLAN scored 5.0/5.0, Luna Max PATCH implementation 5.0/3.5, and Claude PATCH review 5.0/4.8.)
- [x] Run Luna High live Docker startup, database-aware health checks, cURL flows, and restart/persistence checks. (Completed with the default API/database stack left running.)
- [x] Re-run implementation tests and validations after fixes; report results and remaining independent-review/operational gaps.

## Follow-up after Claude Opus 5.5 review

- [x] Remove README-content assertions without replacing them; manually review README facts and verify automated tests do not read README or other documentation content. (No test file remains and test-source searches found no README/docs/Markdown reads; root README was reviewed manually and its DDL command updated.)
- [x] Add PostgreSQL server-default drift detection and metadata-vs-inspected named CHECK-constraint coverage; observe the server-default regression guard fail before enabling comparison. (Drift test failed before `compare_server_default=True`; all four migration tests passed afterward.)
- [x] Consolidate shared schema validation, operation errors, and second-medspa/service test setup without changing route behavior. (Full PostgreSQL-backed behavior suite passes.)
- [x] Add focused pure appointment-rule and import-boundary tests; observe the source-layout/import-boundary failures before moving the implementation. (Pure rules: 10 passed; entrypoint mapper-registration guards: 3 passed; schema/ORM and layer-boundary guards pass.)
- [x] Add fresh-interpreter no-DB mapper-registration coverage for seed, app composition, and DDL entrypoints; observe the missing `Appointment` mapper in the seed process before explicitly importing aggregate metadata.
- [x] Restrict service PATCH operation fields to the public editable set and reject ID, medspa ownership, and arbitrary attributes; observe the focused regression tests fail before the allow-list.
- [x] Move the runtime to the accepted feature-oriented package tree, keep HTTP adapters thin, preserve transaction ownership and all eight business routes plus `/health`, and keep Alembic migration literals frozen. (118 PostgreSQL-backed tests pass, including the route contract and migration checks.)
- [x] Update runtime import paths and DDL/seed commands for the package move; regenerate DDL and confirm the SQL body is unchanged. (API image built; fresh one-off test-db smoke returned 200 from `/health` and the seeded service read route.)
- [x] Run final focused and full unit/PostgreSQL suites, Ruff, ontology validation, strict OpenSpec validation, Compose config, generated-DDL check, and migration consistency; confirm the default app stack remains untouched. (Unit: 69 passed/49 skipped; PostgreSQL: 118 passed; strict OpenSpec: 2 passed; ontology conforms; Ruff/Compose/DDL/migrations pass; fresh-image test-db smoke succeeds.)
- [x] Append an evidence-linked Luna High input/output evaluation for the final Luna Max follow-up and reconcile the README AI-usage summary with that record. The later user-authorized Scope Change response is documented in README; `customer_notes` remains unimplemented.

## User-approved PATCH null-semantics follow-up

- [x] Replace null-as-no-op expectations and add schema, service-operation mapping/atomicity, service API, appointment API, and create-time regression tests before changing implementation; keep automated tests independent of README and other docs content.
- [x] Observe focused tests red before implementation: `uv run --python 3.14 pytest -q tests/test_service_schemas.py tests/test_appointment_schemas.py tests/test_service_patch_operations.py` reported **10 failed, 46 passed**; `TEST_DATABASE_URL='postgresql+psycopg://booking:booking@127.0.0.1:55432/medspa_booking_test' uv run --python 3.14 pytest -q tests/test_service_api.py tests/test_appointment_api.py` reported **5 failed, 36 passed**.
- [x] Implement optional-by-presence, non-nullable PATCH schema fields; description clearing; and direct-operation validation of all non-nullable nulls before any mutation. Keep routers, create operations, routes, database schema, and migrations unchanged.
- [x] Confirm focused green: the no-DB command above reported **56 passed**; the PostgreSQL API command above reported **41 passed**. API tests verify description clearing with follow-up GET/list reads and null-status/service-null rejection with follow-up reads confirming unchanged state.
- [x] Run the no-DB full suite after the initial PATCH implementation with `env -u TEST_DATABASE_URL uv run --python 3.14 pytest -q` (**87 passed, 62 expected skips**) and the PostgreSQL suite with `TEST_DATABASE_URL='postgresql+psycopg://booking:booking@127.0.0.1:55432/medspa_booking_test' uv run --python 3.14 pytest -q` (**149 passed**); run `uv run --python 3.14 ruff check src/medspa_booking tests alembic` (passed).
- [x] Update the normative spec, change delta, proposal/design, README examples/assumptions, and evaluator summary. The latest evaluator update reports **14 unique validated records**; GPT-6.1 Sol PLAN scored **5.0/5.0**, the Luna Max PATCH implementation **5.0/3.5**, and the Claude PATCH review **5.0/4.8**. Strict OpenSpec validation passes; README and docs were manually reviewed; no automated docs-content tests or `docs/eval/` edits were added.
- [x] Append the evidence-linked evaluation record for the Luna Max PATCH null-semantics implementation. (13 unique validated records; input **5.0**, output **3.5**. The evaluator noted that the README's Scope Change status conflicted with the response in that file; this documentation inconsistency has since been corrected.)
- [x] Address Claude Opus's low-severity PATCH type-annotation finding: accurately type omitted-field `None` values without changing the non-nullable OpenAPI contract; observe the new type-annotation tests fail first, then pass after correction. (The no-DB full suite reports 89 passed/62 skipped, PostgreSQL suite 151 passed, Ruff passes, and OpenAPI contract assertions pass.)
- [x] Incorporate the user-authorized Scope Change Scenario design response into README/OpenSpec while explicitly keeping `customer_notes` unimplemented.
- [x] Obtain a read-only Claude follow-up review of the type-annotation correction and evaluate that review under the ontology-backed rubric. (Claude found no remaining issues; Luna High recorded input 5.0/output 4.8. The JSONL contains 14 unique validated records.)

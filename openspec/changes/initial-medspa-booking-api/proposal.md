# Initial Medspa Booking API

## Status

Planning review and the initial implementation are complete. The user-approved PATCH null-semantics follow-up and the low-severity schema-annotation correction are implemented and verified. The latest Luna High update reports fourteen unique validated evaluation records: the GPT-6.1 Sol PLAN scored 5.0/5.0 input/output, the Luna Max PATCH implementation scored 5.0/3.5, and the Claude PATCH review scored 5.0/4.8.

## Why

The take-home exercise asks for a clean, complete CRUD-style API for medspas, services, and appointments but gives detailed routes only for services and appointments. A small, specification-first plan is needed to distinguish the explicit contract from missing booking and API policies before code begins.

## What changes

- Create the initial FastAPI/PostgreSQL application and schema.
- Implement only the eight expressly listed service and appointment endpoints; do not add medspa CRUD or delete routes.
- Supply a local medspa seed/demo record so the nested routes can be exercised.
- Provide a single-command Docker Compose runtime, PostgreSQL schema creation, health/readiness verification, and unit/integration tests.
- Document the setup, endpoint examples, decisions, tradeoffs, scope, and actual AI usage in the root README.
- Use the ontology under `docs/ontology/` to evaluate each agent's input/output quality; store versioned, evidence-linked JSONL records under `docs/eval/` using 1–5 ratings and the approved rubric.
- Document the user-authorized Scope Change Scenario response while keeping `customer_notes` implementation outside the current API scope.

## Requirements review record

- Source reviewed: `/Users/felipe.rodrigues/workspace/personal/moxie/backend-take-home-exercise.md`.
- PLAN review completed by GPT-6.1 Sol. Its findings are reflected in this proposal and in `openspec/specs/medspa-booking/spec.md`; no code was produced by that review agent.
- Confirmed hard contract: required data fields/relationships, eight listed routes, Python/FastAPI/PostgreSQL selected by the user, PostgreSQL DDL, API/README deliverables, Docker Compose startup, test-first workflow, OpenSpec documentation, ontology-backed agent evaluation, and (at the time of the initial plan) no scope-change answer yet. The user later requested and authorized a design response; `customer_notes` remains unimplemented.
- Current OpenSpec convention selected from the official v2 documentation: repository-local `openspec/config.yaml`, `openspec/specs/`, and `openspec/changes/`.
- OpenSpec CLI structural validation passed for the initial change and main spec using the current official CLI via `npx`.
- Ontology created in `docs/ontology/`; example graph and SHACL shapes pass validation. Its namespace is provisional (`moxie.example.com`) until a stable project identity exists.
- Requested model IDs were confirmed available: implementation `github-copilot/gpt-6-luna` with `max`; evaluator/operational validation `github-copilot/gpt-6-luna` with `high`; reviewer `github-copilot/claude-opus-5.5`.

## Proposed implementation plan

1. Finish updating and validating the approved OpenSpec, ontology, and evaluation contract.
2. Start the Luna High evaluator in parallel with implementation; first score the completed PLAN agent, then collect evidence for every subsequent agent run.
3. Begin Luna Max implementation with one behavior slice at a time: failing unit/integration test, minimal code, green tests, then refactor.
4. Have Claude Opus 5.5 independently review code, tests, and docs against OpenSpec and the original exercise; address findings with regression tests.
5. Have Luna High perform clean Docker startup, health/readiness, cURL, PostgreSQL integration, and persistence checks; report any unavailable measurements or failed acceptance criteria rather than masking them.
6. Reconcile OpenSpec, schema DDL, code, tests, ontology-backed evaluation artifacts, and README before presenting the result for user review.

## Initial architecture proposal (not yet a code decision)

Use one FastAPI application and one PostgreSQL database targeting Python 3.14. Keep API routes and Pydantic request/response models separate from small application/domain operations and SQLAlchemy persistence. Use feature-oriented modules for services and appointments; medspas are seed/demo data, not a public CRUD feature. Use SQLAlchemy 2 and Alembic for constraints and schema evolution, and keep the required PostgreSQL DDL reviewable and synchronized with the migration. Compose should gate API startup on database readiness and run migrations before the HTTP server starts.

Startup command: `docker compose up --build`. The health/readiness check verifies database connectivity, not only process liveness. List endpoints return all matching rows in stable ID order; no pagination/filter surface is added for this exercise. Use conventional HTTP not-found and validation responses and document them in the README.

## User-approved decisions

| Decision | Approved behavior |
| --- | --- |
| Medspa routes | Implement only the eight listed service/appointment routes. Do not add medspa CRUD routes. Supply seed/demo data or documented DB setup for a usable medspa. |
| Delete operations | No delete routes. |
| Appointment totals | Store service price and duration snapshots on each appointment/service association; totals sum those snapshots. Catalog edits do not change existing appointment totals. |
| Service selection | Require at least one service ID; reject duplicates and services belonging to another medspa atomically. |
| Appointment status | New appointments default to `scheduled`; transitions are unrestricted among `scheduled`, `completed`, and `canceled`. |
| Time and availability | Require an explicit timezone offset and a future start time. Do not implement availability, overlap, or business-hours rules. |
| Field validation and PATCH | Price is a nonnegative integer number of cents; duration is a positive integer number of minutes; a service description may be omitted or null on creation. PATCH omission preserves a value; supplied non-null values are validated and applied; `description: null` clears the service description; null `name`, `price`, `duration`, or appointment `status` is rejected with `422` and no partial changes. An empty object is a no-op. |
| Evaluation format | Versioned JSONL in `docs/eval/`; separate input/output quality ratings on a 1–5 scale, dimension-level evidence, ontology-linked run identity, rubric version, and explicit unavailable values. |
| Evaluation evidence | Evaluate the actual agent inputs and outputs, and use code-review/test/command artifacts as corroborating evidence. Do not invent token, cost, or latency data when unavailable. |
| Python runtime | Python 3.14 for the application/container runtime. |
| OpenSpec | Use the official repository-local OpenSpec 2.0 layout and CLI; structural validation passes. |

### Superseded PATCH null decision

The initial decision that every explicit-null PATCH field would be ignored is superseded by the user's approved PATCH null-semantics follow-up. Only nullable `Service.description` clears on explicit null; null for non-nullable PATCH fields is invalid, while omission preserves the stored value. The normative contract is maintained in `openspec/specs/medspa-booking/spec.md` and the change delta. Evaluations of the implementation and latest Claude review are recorded.

## Remaining implementation details

- The exact SQLAlchemy model/module layout and migration implementation should follow the design above without introducing generic layers.
- The schema DDL must remain consistent with the Alembic migration and ORM. The implementation agent must record the chosen synchronization approach and any revised decision here before relying on it.
- HTTP error examples and health route behavior should be documented once implemented; the existing eight routes remain the public business API contract.
- The GitHub repository link is a final submission item. Repository creation/push and Git commits are not authorized by this planning request; ask separately when delivery is ready.

## Scope Change Scenario response (design only)

The user later authorized a response to the README Scope Change Scenario and selected one optional appointment-level `customer_notes` field as the working design assumption. The README documents the impact, migration, testing, privacy, and rollout considerations. This answer is design-only: `customer_notes` is not part of the current API, and no model, migration, route, or implementation task for the field is included in this change.

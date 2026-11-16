# Medspa Booking API

## Purpose

This specification captures the explicit target behavior in `backend-take-home-exercise.md`, the user's selected stack, and decisions made during the requirements review. Remaining implementation decisions are recorded in the active initial-project proposal.

## Requirements

### Requirement: Medspa data

The system SHALL represent a medspa with an identifier, name, address, phone number, and email.

#### Scenario: Medspa fields are represented

- **WHEN** a medspa is stored or returned
- **THEN** its data model supports `id`, `name`, `address`, `phone_number`, and `email`

### Requirement: Service data

The system SHALL represent a service with an identifier, nonblank name, optional description, nonnegative integer price in cents, positive integer duration in minutes, and a foreign-key relationship to its medspa. Price, duration, and identifiers SHALL fit the signed PostgreSQL `INTEGER` range (`0..2147483647` for price and `1..2147483647` for positive values).

#### Scenario: Service belongs to a medspa

- **WHEN** a service is stored
- **THEN** it references the medspa whose catalog contains it

#### Scenario: Service values use the specified units and bounds

- **WHEN** a service is created or updated
- **THEN** its price is a nonnegative integer number of cents
- **AND** its duration is a positive integer number of minutes
- **AND** both values are at most `2147483647`
- **AND** its name contains at least one non-whitespace character
- **AND** its description may be omitted or supplied as `null` when creating the service

#### Scenario: Create a service with a nullable description

- **WHEN** a client creates a service with its description omitted or set to `null`
- **THEN** the service is created with a SQL `NULL` description
- **AND** null `name`, `price`, or `duration` values are rejected with `422`

### Requirement: Appointment data and relationships

The system SHALL represent an appointment with an identifier, medspa foreign key, timezone-aware future start time, status, total duration derived from its services, and total price derived from its services. Each appointment/service association SHALL preserve the service price and duration captured when the appointment was booked. A medspa SHALL have many services and many appointments. An appointment SHALL be related to many services, and a service SHALL be related to many appointments.

#### Scenario: Appointment status uses the exercise vocabulary

- **WHEN** an appointment status is represented
- **THEN** it is one of `scheduled`, `completed`, or `canceled`

#### Scenario: Appointment totals are derived from selected services

- **WHEN** an appointment is represented
- **THEN** its total duration and total price are derived from its associated services
- **AND** the totals are sums of the association's booking-time service snapshots

#### Scenario: Booking snapshots remain stable after catalog edits

- **WHEN** a service's current price or duration changes after an appointment was created
- **THEN** the existing appointment's snapshot and derived totals remain unchanged

#### Scenario: Appointment start time is valid

- **WHEN** an appointment is created
- **THEN** its start time includes an explicit timezone offset
- **AND** its start time is in the future
- **AND** availability, business-hour, and overlap checks are not performed

#### Scenario: Appointment start times have a consistent response representation

- **WHEN** an appointment is created with a timezone offset other than UTC
- **THEN** create and subsequent read responses represent the same instant in UTC

### Requirement: Service HTTP endpoints

The API SHALL implement the four service endpoint contracts explicitly listed by the exercise.

#### Scenario: Create a service

- **WHEN** a client sends `POST /medspas/{medspa_id}/services`
- **THEN** the API supports creating a service for that medspa
- **AND** the service data passes the approved field validation rules

#### Scenario: Retrieve a service

- **WHEN** a client sends `GET /services/{service_id}`
- **THEN** the API supports retrieving that service by ID

#### Scenario: List services for a medspa

- **WHEN** a client sends `GET /medspas/{medspa_id}/services`
- **THEN** the API supports listing that medspa's services

#### Scenario: Partially update a service

- **WHEN** a client sends `PATCH /services/{service_id}`
- **THEN** the API supports updating the service's name, description, price, or duration
- **AND** omitted fields preserve their stored values
- **AND** supplied non-null values are validated and applied

### Requirement: Appointment HTTP endpoints

The API SHALL implement the four appointment endpoint contracts explicitly listed by the exercise.

#### Scenario: Create an appointment with services

- **WHEN** a client sends `POST /medspas/{medspa_id}/appointments` with service IDs
- **THEN** the API supports creating an appointment for that medspa with those services
- **AND** at least one service ID is required
- **AND** duplicate IDs and services belonging to another medspa are rejected atomically
- **AND** each selected service's price and duration are captured for this appointment
- **AND** a new appointment has status `scheduled`

#### Scenario: Status may move among the supported values

- **WHEN** a valid status update is requested
- **THEN** the appointment may move to any of `scheduled`, `completed`, or `canceled`
- **AND** no additional transition graph is imposed

#### Scenario: Retrieve an appointment

- **WHEN** a client sends `GET /appointments/{appointment_id}`
- **THEN** the API supports retrieving that appointment by ID

#### Scenario: Partially update appointment status

- **WHEN** a client sends `PATCH /appointments/{appointment_id}`
- **THEN** the API supports updating that appointment's status
- **AND** an omitted status preserves its stored value
- **AND** a supplied `null` status is rejected with `422` and leaves the appointment unchanged

#### Scenario: List appointments

- **WHEN** a client sends `GET /appointments`
- **THEN** the API supports listing appointments

### Requirement: Validate bounded request identifiers and reject unknown fields

Every path identifier and every appointment `service_ids` item SHALL be a positive signed PostgreSQL `INTEGER`. Request bodies SHALL reject fields outside the request contract. Invalid values and unknown fields SHALL return `422`.

#### Scenario: Reject out-of-range identifiers and extra fields

- **WHEN** a request supplies a path identifier or appointment service ID above `2147483647`, a non-positive identifier, or an unknown request field
- **THEN** the API rejects the request with `422` before persistence

#### Scenario: Reject a blank service name

- **WHEN** a service create or patch request supplies a name containing only whitespace
- **THEN** the API rejects the request with `422`

### Requirement: Route scope follows the explicit endpoint table

The API SHALL implement the eight explicitly listed service and appointment routes and SHALL NOT add medspa CRUD or delete routes. Local demo/seed data or documented database setup SHALL provide medspa records for the listed nested routes.

#### Scenario: Review the public route surface

- **WHEN** a reviewer inspects the API routes
- **THEN** the eight listed routes are available
- **AND** there are no additional medspa CRUD or delete routes
- **AND** a documented local medspa record can be used to exercise the API

### Requirement: Selected technology stack

The implementation SHALL use Python 3.14, FastAPI, and PostgreSQL.

#### Scenario: Build the selected stack

- **WHEN** a developer starts the project
- **THEN** the HTTP application runs with FastAPI and connects to PostgreSQL using Python
- **AND** its runtime targets Python 3.14

### Requirement: Single-command local startup

Docker Compose SHALL provide a documented, simple command that starts the database, ensures its schema is available, and starts the HTTP API connected to that database.

#### Scenario: Start the local API and database

- **WHEN** a developer follows the documented Compose startup command
- **THEN** the database and API become available without separate manual setup steps

### Requirement: Database schema deliverable

The repository SHALL provide PostgreSQL `CREATE TABLE` statements for the implemented schema.

#### Scenario: Review the database DDL

- **WHEN** a reviewer inspects the repository deliverables
- **THEN** PostgreSQL `CREATE TABLE` statements are available in a documented location

### Requirement: Test-first implementation

Each behavior SHALL have unit and/or integration coverage appropriate to its boundary. During implementation, a failing test SHALL be written and observed before the corresponding behavior is implemented. Database integration tests SHALL exercise PostgreSQL behavior.

#### Scenario: Develop a behavior test-first

- **WHEN** an implementation slice begins
- **THEN** its test is written and run before the behavior code
- **AND** the implementation is followed by passing focused and regression tests

### Requirement: Root README documentation

The root `README.md` SHALL document local setup, API examples for every implemented endpoint, AI usage, assumptions, tradeoffs, and scope decisions. It SHALL not answer the Scope Change Scenario before user authorization; after authorization, it SHALL document the answer and distinguish proposed work from implemented scope.

#### Scenario: Review project documentation

- **WHEN** a reviewer follows the root README
- **THEN** setup, all implemented endpoint examples, AI usage, assumptions, tradeoffs, and scope decisions are documented
- **AND** the Scope Change Scenario response, when authorized, accurately distinguishes a design decision from implemented API scope

### Requirement: AI contribution evaluation

The project SHALL evaluate input and output quality for each participating agent using the ontology in `docs/ontology/`, and store evidence-linked, machine-readable JSONL evaluation artifacts under `docs/eval/`. Each record SHALL identify its schema and rubric versions, agent run, input/output quality ratings on a 1–5 scale, dimension-level evidence, and any unavailable measurements; unavailable values SHALL not be fabricated.

#### Scenario: Record an agent evaluation

- **WHEN** an agent run is evaluated under the approved rubric
- **THEN** its input/output quality observations are recorded in versioned JSONL with ontology-linked run identity, 1–5 rubric ratings, and supporting evidence under `docs/eval/`
- **AND** any unavailable metric is explicitly marked unavailable rather than guessed

### Requirement: PATCH field-presence and null semantics

For supported PATCH fields, the API SHALL preserve stored values for omitted fields and SHALL validate and apply supplied non-null values. Explicit `null` SHALL clear only `Service.description`; it SHALL be rejected for `Service.name`, `Service.price`, `Service.duration`, and `Appointment.status` with `422`. A PATCH containing an invalid null SHALL make no changes, including when it also contains otherwise valid updates.

#### Scenario: Apply supplied values and preserve omitted fields

- **WHEN** a service or appointment PATCH omits a field and supplies valid non-null values for other fields
- **THEN** omitted fields retain their stored values
- **AND** supplied values are applied, including `price: 0` and `description: ""`

#### Scenario: Clear a service description

- **WHEN** a service PATCH supplies `description: null`
- **THEN** the stored description is set to SQL `NULL`
- **AND** the PATCH response, a subsequent service read, and the service list return `description: null`

#### Scenario: Reject null for non-nullable PATCH fields atomically

- **WHEN** a service PATCH supplies `null` for `name`, `price`, or `duration`, or an appointment PATCH supplies `null` for `status`
- **THEN** the request fails with `422` and makes no changes
- **AND** any otherwise valid updates in the same request are not applied

#### Scenario: Empty PATCH is a no-op

- **WHEN** a client sends an empty object to a supported PATCH endpoint
- **THEN** the request succeeds without changing the stored resource

## Explicit exclusions

- Medspa CRUD and delete endpoints are excluded; medspa fixtures/demo seed data make the listed nested routes usable.
- Appointment overlap, business-hours, provider-availability, and cancellation transition policies are excluded.
- The user-authorized README Scope Change Scenario response selects one optional appointment-level `customer_notes` field as a design assumption. This does not authorize implementation: the field, migration, and API changes remain excluded from the current scope.

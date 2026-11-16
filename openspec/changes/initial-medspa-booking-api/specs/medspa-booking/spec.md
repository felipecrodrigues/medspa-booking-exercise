## ADDED Requirements

### Requirement: Persist the required booking domain

The API SHALL persist medspas, services, appointments, and appointment/service associations in PostgreSQL. The persisted fields and relationships SHALL match `openspec/specs/medspa-booking/spec.md` and the approved decisions recorded for this change.

#### Scenario: Preserve the specified service and appointment relationships

- **WHEN** a service or appointment is persisted
- **THEN** the service references its medspa, the appointment references its medspa, and appointment/service selection supports the required many-to-many relationship

### Requirement: Serve the explicit service and appointment routes

The API SHALL implement each service and appointment HTTP method/path listed in `openspec/specs/medspa-booking/spec.md` with the behavior approved for this change.

#### Scenario: Verify the listed routes

- **WHEN** the API route contract is inspected or exercised
- **THEN** all explicitly listed service and appointment routes are present and have tests

### Requirement: Start the complete local stack with Docker Compose

The repository SHALL provide one documented Docker Compose command that brings up PostgreSQL, ensures the approved schema is available, and starts the API.

#### Scenario: Start from a clean local environment

- **WHEN** a developer follows the README command with a clean Docker environment
- **THEN** the API becomes ready only after it can use PostgreSQL and its schema

### Requirement: Verify behavior test-first

Each implemented behavior SHALL have relevant unit and PostgreSQL integration coverage, and its test SHALL be observed failing before the behavior is implemented.

#### Scenario: Build one behavior slice

- **WHEN** an implementation task adds behavior
- **THEN** its failing test is written and run first, followed by implementation, a passing test run, and regression coverage

### Requirement: Preserve appointment booking snapshots

When an appointment is created, the system SHALL persist the selected service's price and duration on its appointment/service association and SHALL derive appointment totals from those saved values. Later service catalog edits SHALL NOT alter existing appointments.

#### Scenario: Catalog edit does not alter a booked appointment

- **WHEN** a service price or duration is changed after booking
- **THEN** existing association snapshots and appointment totals remain unchanged

### Requirement: Validate appointment creation atomically

The system SHALL require at least one distinct service ID for an appointment, SHALL require each service to belong to the requested medspa, and SHALL reject invalid combinations without partial persistence.

#### Scenario: Reject invalid selected service IDs

- **WHEN** the appointment request has no service IDs, duplicate IDs, or a service owned by another medspa
- **THEN** the request fails and no appointment or selection rows are persisted

### Requirement: Validate appointment start times

The API SHALL require an explicit timezone offset and a future start time. It SHALL NOT check business hours, provider availability, or overlap.

#### Scenario: Reject an invalid appointment time

- **WHEN** a request omits its timezone offset or supplies a start time that is not in the future
- **THEN** the request is rejected without creating appointment records

### Requirement: Apply the approved field and PATCH rules

Service prices SHALL be nonnegative integer cents, durations SHALL be positive integer minutes, and descriptions MAY be omitted or `null` when creating a service. PATCH behavior SHALL follow the field-presence and null rules in the scenarios below.

#### Scenario: Preserve create-time service validation

- **WHEN** a client creates a service with its description omitted or set to `null`
- **THEN** the request is accepted with a SQL `NULL` description
- **AND** null `name`, `price`, or `duration` values are rejected with `422`

#### Scenario: Preserve omitted fields and apply valid PATCH values

- **WHEN** a service or appointment PATCH omits fields and supplies valid non-null values for other fields
- **THEN** omitted values remain unchanged and supplied values are applied
- **AND** valid values include `price: 0` and `description: ""`

#### Scenario: Clear a service description with null

- **WHEN** a service PATCH supplies `description: null`
- **THEN** the stored description is cleared to SQL `NULL`
- **AND** the PATCH response, a subsequent service read, and the service list return `description: null`

#### Scenario: Reject null for non-nullable PATCH fields without partial updates

- **WHEN** a service PATCH supplies `null` for `name`, `price`, or `duration`, or an appointment PATCH supplies `null` for `status`
- **THEN** the request fails with `422` and no stored values change
- **AND** valid changes included in the same request are not applied

#### Scenario: An empty PATCH is a no-op

- **WHEN** a client sends an empty object to a supported PATCH endpoint
- **THEN** the request succeeds without changing the stored resource

### Requirement: Bound PostgreSQL integer request values and reject unknown fields

Service prices and durations SHALL fit the signed PostgreSQL `INTEGER` range. Every path identifier and appointment `service_ids` item SHALL be positive and no greater than `2147483647`. Request bodies SHALL reject unknown fields, and service names SHALL contain at least one non-whitespace character. These invalid inputs SHALL return `422` without persistence.

#### Scenario: Reject out-of-range values and unknown request fields

- **WHEN** a request supplies an oversized price, duration, path identifier, or appointment service ID, an unknown field, or a whitespace-only service name
- **THEN** the API rejects it with `422` before writing data

### Requirement: Return appointment start times consistently

The API SHALL normalize valid timezone-aware appointment start times to UTC for create and read responses.

#### Scenario: Read back a non-UTC appointment time

- **WHEN** a client creates an appointment with a non-UTC timezone offset and reads it back
- **THEN** both responses represent the same instant in UTC

### Requirement: Protect destructive PostgreSQL test setup

The PostgreSQL integration-test fixture SHALL verify both a dedicated database name ending in `_test` and an explicitly allowed loopback host before dropping or recreating the `public` schema.

#### Scenario: Refuse unsafe integration-test database URLs

- **WHEN** `TEST_DATABASE_URL` uses a non-PostgreSQL database, a database name without the `_test` suffix, or a non-loopback host
- **THEN** the fixture fails before changing database state

### Requirement: Use the selected Python runtime

The API container SHALL use Python 3.14, FastAPI, and PostgreSQL.

#### Scenario: Start the specified runtime

- **WHEN** Docker Compose starts the API
- **THEN** it runs on Python 3.14 and connects to the Compose PostgreSQL service

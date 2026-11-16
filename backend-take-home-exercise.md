# Moxie Backend Take-Home Exercise

## Intro & Welcome!

### AI-Powered Development

At Moxie, we use AI tools daily to move faster and build better products. We expect you to do the same in this exercise.

With AI as your copilot, we're looking for:

- **Higher quality execution** — clean code, good API design, thoughtful decisions
- **Complete delivery** — all requirements met, not just partially implemented
- **Understanding over automation** — you should be able to explain every decision and line of code

Come prepared to discuss what AI tools you used, where they helped, and where you made judgment calls. Include a brief section in your README documenting your AI usage.

Thank you for your interest in Moxie! Below you will find a work sample project to help us understand your skill level and coding style.

**Focus on quality over quantity.** We'd rather see clean, well-thought-out code that meets the requirements than extra features rushed in. Come prepared to discuss your decisions and what you'd do differently with more time.

At Moxie, we're looking for Product Engineers — people who don't just execute, but think critically, make decisions, and propose solutions. This exercise is designed to see how you approach problems, not just whether you can write code.

## The Exercise

### Context

#### What is a Medspa?

A medspa is a combination of an aesthetic medical center and a day spa that provides nonsurgical aesthetic medical services.

At Moxie, each medspa defines a menu of services that customers can select when booking an appointment. You can see an example in our online booking flow where customers can select one or multiple services, each with a different name, length of time, and pricing.

### Goals

Implement a simple CRUD API that allows management of medspas, services, and appointments. This is a simplified version of our actual booking system.

### Tech Stack Requirements

Implement using Python (with FastAPI or Flask) and PostgreSQL.

At Moxie we use Python and Postgres, but if you're more comfortable with another language and database (Node.js/TypeScript, Go, etc.), that's acceptable. Just let us know in your README.

If you don't have experience with these technologies, it's okay to use AI to learn — in the interview we'll talk about your learning process.

### Requirements

#### Data Model

Design and implement a database schema that supports:

**Medspa**

- `id`
- `name`
- `address`
- `phone_number`
- `email`

**Service**

- `id`
- `name`
- `description`
- `price` (in cents)
- `duration` (in minutes)
- `medspa_id` (foreign key)

**Appointment**

- `id`
- `medspa_id` (foreign key)
- `start_time`
- `status` (`scheduled`, `completed`, `canceled`)
- `total_duration` (derived from services)
- `total_price` (derived from services)

#### Relationships

- A medspa can have many services
- A medspa can have many appointments
- An appointment can have many services (many-to-many)

#### API Endpoints

Implement an API to manage medspas, services, and appointments.

**Services**

| Endpoint | Description |
| --- | --- |
| `POST /medspas/{medspa_id}/services` | Create a service |
| `GET /services/{service_id}` | Get a service by ID |
| `GET /medspas/{medspa_id}/services` | List all services for a medspa |
| `PATCH /services/{service_id}` | Update a service (name, description, price, duration) |

**Appointments**

| Endpoint | Description |
| --- | --- |
| `POST /medspas/{medspa_id}/appointments` | Create an appointment with service IDs |
| `GET /appointments/{appointment_id}` | Get an appointment by ID |
| `PATCH /appointments/{appointment_id}` | Update appointment status |
| `GET /appointments` | List all appointments |

### Deliverables

- Provide CREATE TABLE statements (Postgres SQL)
- Working API implementation
- README with setup instructions and API examples
- Provide a link to your GitHub repository

### What We're Evaluating

Completion is a key part of our evaluation. With AI tools available, we expect you to deliver all requirements, not just a partial implementation.

We're looking at:

- **Completion** — Did you deliver all the requirements listed above?
- **Code quality** — Is your code clean, maintainable, and well-structured?
- **API design** — Are your endpoints RESTful and well-designed?
- **Data modeling** — Is your schema properly normalized with appropriate constraints?
- **Communication** — Can you clearly explain your choices and tradeoffs?

> **Time expectation:** This should take 4–6 hours. If you're spending significantly more, you may be over-engineering.

### Scope Change Scenario

A PM pings you late in the build:

> “Can we add a customer_notes field to appointments so customers can leave special instructions?”

You don't need to implement this. Instead, answer (and add it to the README):

- What would you change in your implementation?
- How would you communicate and handle this in a real scenario?

### Document Your Thinking

Include a README in your repository that covers:

- Setup instructions — How do we run your code locally?
- API examples — Show example curl or HTTP requests for each endpoint
- AI usage — What tools did you use and how?
- Assumptions — What did you assume about the requirements?
- Tradeoffs — What decisions did you make and why?
- Scope decisions — What did you leave out of scope, and why?
- Scope change response — Answer the PM scenario question above

### Submit Your Work

- Link to GitHub repository with a complete README
- CREATE TABLE statements (can be in README or separate SQL file)

Thank you for your time.

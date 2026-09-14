# KavEmploy (currently a work in progress)

KavEmploy is a job search intelligence system for discovering, organizing, and evaluating early-career software engineering opportunities. Its initial focus is Class of 2026 candidates searching for full-time roles in the Chicago area.

Milestone 3 provides job and application tracking APIs plus dashboard statistics. Jobs can be created, filtered, updated, and analyzed, then tracked from saved through offer or rejection.

## Current capabilities

- Store manually entered job postings through a validated API.
- List jobs with pagination, filters, and deterministic sorting.
- Partially update jobs while recalculating affected derived fields.
- Delete jobs and receive consistent not-found responses.
- Track one current application state per job from saved through offer or withdrawal.
- Record application dates, referrals, notes, and interview stages.
- Summarize job inventory, likely entry-level roles, weekly discoveries, and submissions.
- Preserve source values in `raw_*` fields and create deterministic normalized values.
- Normalize common software engineering title variants.
- Score entry-level suitability with versioned, explainable rules.
- Produce a deterministic duplicate-candidate fingerprint without merging data.
- Manage schema changes with Alembic migrations.
- Exercise business rules and API behavior with automated tests.
- Explore the API through FastAPI's generated OpenAPI documentation.
- Distinguish process liveness from database readiness.

## Repository structure

```text
backend/
  app/
    api/            HTTP routes
    core/           application configuration
    db/             database session and metadata
    intelligence/   normalization, classification, and fingerprint logic
    models/         SQLAlchemy persistence models
    schemas/        validated API contracts
    services/       application use cases
  migrations/       versioned database schema
  tests/            business-logic and API tests
compose.yaml        local PostgreSQL service
```

The project is a modular monolith. Intelligence rules are separate from HTTP and persistence code so future CSV, JSON, and public-API adapters can use the same behavior.

## Prerequisites

- Python 3.11 or newer
- Docker with Docker Compose

## Local setup

From the repository root, copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Start PostgreSQL:

```powershell
docker compose up -d db
```

KavEmploy maps PostgreSQL to host port `5433` to avoid conflicts with PostgreSQL installations using the default host port `5432`. Inside the container, PostgreSQL still uses port `5432`.

Create and activate a virtual environment, then install the backend:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".\backend[dev]"
```

Apply database migrations and run the API:

```powershell
Set-Location backend
alembic upgrade head
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation. Use `/health` to check process liveness and `/health/ready` to verify database connectivity.

## Job API

```text
POST   /api/v1/jobs           Create and analyze a job
GET    /api/v1/jobs           List, filter, sort, and paginate jobs
GET    /api/v1/jobs/{id}      Retrieve one job
PATCH  /api/v1/jobs/{id}      Partially update and reanalyze a job
DELETE /api/v1/jobs/{id}      Delete a job

PUT    /api/v1/jobs/{id}/application     Create or replace application tracking
GET    /api/v1/jobs/{id}/application     Retrieve application tracking
DELETE /api/v1/jobs/{id}/application     Remove tracking without deleting the job

GET    /api/v1/dashboard/summary         Retrieve dashboard statistics
```

The list endpoint accepts:

- `company`, `title`, and `location` normalized text filters
- `suitability`: `likely`, `uncertain`, or `unlikely`
- `sort_by`: `created_at`, `date_posted`, or `entry_level_score`
- `sort_order`: `asc` or `desc`
- `limit` from 1 through 100 and a non-negative `offset`

Example:

```text
GET /api/v1/jobs?location=Chicago&suitability=likely&sort_by=entry_level_score&sort_order=desc
```

List responses include `items`, `total`, `limit`, and `offset` so clients can build pagination without additional requests.

Application statuses are `saved`, `applied`, `interview`, `rejected`, `offer`, and `withdrawn`. Entering a submitted-stage status automatically records the first application timestamp when one was not supplied. The dashboard excludes `saved` jobs from `applications_submitted`, and defines the current week as Monday 00:00 UTC onward.

## Example request

```powershell
$job = @{
  raw_title = "Software Engineer I"
  raw_company = "Example Corp."
  raw_location = "Chicago, IL"
  description = "Bachelor's degree accepted. Requires 0-2 years of experience."
  employment_type = "full_time"
  minimum_years_experience = 0
  maximum_years_experience = 2
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/jobs `
  -ContentType "application/json" `
  -Body $job
```

The response contains raw and normalized fields, a score from 0 through 100, a suitability band, and the rules that contributed to the score.

## Tests and linting

From `backend/` with the development dependencies installed:

```powershell
pytest
ruff check .
```

Tests use an isolated in-memory database. Local application execution uses PostgreSQL through `DATABASE_URL`.

## Deliberate V1 limits

KavEmploy does not scrape restricted job boards. Authentication, automated ingestion, status history, frontend screens, AI matching, and AWS infrastructure are deferred to later milestones.

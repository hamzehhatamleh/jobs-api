# Jobs API

A REST API for managing companies and their job postings, built with FastAPI, PostgreSQL and Docker.

## Features

- Create a company together with its jobs in one request
- Create a single job for an existing company
- List jobs with filters (company, title) and pagination (limit, offset)
- Update a job with PATCH (only the fields you send)
- Optional salary on jobs (negative values are rejected)
- Input validation with Pydantic (clear `422` errors)
- Proper status codes: `201` for created, `404` for not found
- Database migrations with Alembic
- Runs fully in Docker: the API and PostgreSQL in two containers
- Automated tests with a separate test database, running in CI

## Tech stack

- **FastAPI**: web framework
- **SQLAlchemy 2.0**: ORM
- **PostgreSQL**: database (SQLite as a fallback for local runs)
- **Alembic**: database migrations
- **Docker + Docker Compose**: running the API and the database together
- **Pydantic**: request validation
- **pytest + GitHub Actions**: tests and CI

## Project structure

```
database.py          → database connection (reads DB_URL), Base, and the get_db session dependency
models.py            → SQLAlchemy tables (companies, jobs: one-to-many)
schemas.py           → Pydantic models for requests and responses
main.py              → the FastAPI app and routes
alembic/             → migration files (alembic/versions) and env.py
Dockerfile           → builds the API image
docker-compose.yaml  → the API + PostgreSQL, with a volume for the data
.env.example         → the environment variables you need
test_main.py         → tests, using a separate test database via dependency_overrides
```

## Run with Docker (recommended)

You only need Docker Desktop.

1. Create your `.env` file from the example, and change the values if you want:

```bash
cp .env.example .env
```

(on Windows: `copy .env.example .env`)

2. Start everything:

```bash
docker compose up --build
```

3. Open http://localhost:8000/docs

When the API container starts, it runs `alembic upgrade head` first, so the tables are created automatically. The database data is kept in a Docker volume, so it stays after `docker compose down`. To start again with an empty database, use `docker compose down -v`.

## Run locally (without Docker)

Without `DB_URL`, the app uses a local SQLite file.

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs

## Run the tests

```bash
pytest
```

## Endpoints

| Method | Path                      | Description                          |
|--------|---------------------------|--------------------------------------|
| POST   | `/companies`              | Create a company with its jobs       |
| GET    | `/companies/{company_id}` | Get a company and its jobs           |
| POST   | `/jobs`                   | Create a job for a company           |
| GET    | `/jobs`                   | List jobs (filters + pagination)     |
| GET    | `/jobs/{job_id}`          | Get one job                          |
| PATCH  | `/jobs/{job_id}`          | Update a job                         |

## What I learned

- **Pydantic models and database models are different objects.** The request body is a Pydantic object, but SQLAlchemy can only save its own objects, so I convert each one before adding it to the session.
- **How `Depends` and `yield` manage the database session.** `get_db` opens a session, gives it to the route, and closes it after the response. When I tried `return` instead of `yield`, connections stayed open.
- **Testing with a separate database.** I used `dependency_overrides` to swap `get_db` for a test session, so the tests never touch the real data.
- **`create_all` can't change a table that already exists.** When I added `salary` to the model, the app returned 500 because the real table didn't have the column. I moved to Alembic so every change is a migration file, and I can add columns without losing data.
- **A 201 doesn't prove the data was saved.** Once Postman returned 201 but Postgres was empty. It turned out the file wasn't saved and the app fell back to SQLite. Now I always check the database itself.
- **`depends_on` waits for the database container to start, not to be ready.** The first connection sometimes fails, so the API container restarts on failure until Postgres accepts connections.
- **Secrets don't go in git.** The database password is in a `.env` file that's ignored by git, and `.env.example` shows which variables are needed.
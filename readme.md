# Jobs API

A REST API for managing companies and their job postings, built with FastAPI and SQLAlchemy.

## Features

- Create a company together with its jobs in one request
- Create a single job for an existing company
- Get a job, or a company with all its jobs
- Input validation with Pydantic (clear `422` errors)
- Proper status codes: `201` for created, `404` for not found
- Automated tests with a separate test database

## Tech stack

- **FastAPI** — web framework
- **SQLAlchemy 2.0** — ORM, with SQLite
- **Pydantic** — request validation
- **pytest** — automated tests

## Project structure

```
database.py   → database connection, Base, and the get_db session dependency
models.py     → SQLAlchemy tables (companies, jobs — one-to-many)
schemas.py    → Pydantic models for request bodies
main.py       → the FastAPI app and routes
test_main.py  → tests, using a separate test database via dependency_overrides
```

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs

## Run the tests

```bash
pytest
```

## Endpoints

| Method | Path                     | Description                     |
|--------|--------------------------|---------------------------------|
| POST   | `/companies`             | Create a company with its jobs  |
| GET    | `/companies/{company_id}`| Get a company and its jobs      |
| POST   | `/jobs`                  | Create a job for a company      |
| GET    | `/jobs/{job_id}`         | Get one job                     |



## What I learned

- **Pydantic models and database models are different objects.** The request body is a Pydantic object, but SQLAlchemy can only save its own objects, so I convert each one before adding it to the session.
- **How `Depends` and `yield` manage the database session.** `get_db` opens a session, gives it to the route, and closes it after the response. When I tried `return` instead of `yield`, connections stayed open.
- **Testing with a separate database.** I used `dependency_overrides` to swap `get_db` for a test session, so the tests never touch the real data.

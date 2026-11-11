from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database import Base, get_db
from main import app

# ---------- test database setup ----------

# 1. a SECOND engine → a separate file, only for tests
test_engine = create_engine("sqlite:///test.db")

# 2. start clean every run: erase the tables, then create empty ones
Base.metadata.drop_all(test_engine)
Base.metadata.create_all(test_engine)


# 3. same as get_db, but opens a session on the TEST engine
def get_test_db():
    with Session(test_engine) as session:
        yield session


# 4. the swap: "when a route asks for get_db, give it get_test_db instead"
app.dependency_overrides[get_db] = get_test_db

client = TestClient(app)


# ---------- error cases ----------

def test_get_job_not_found():
    response = client.get("/jobs/99")
    assert response.status_code == 404


def test_get_company_invalid_id():
    response = client.get("/companies/abc")
    assert response.status_code == 422


def test_create_company_with_no_jobs():
    response = client.post(
        "/companies",
        json={"name": "comp1", "city": "amman", "jobs": []},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "jobs"]


# ---------- success cases (they WRITE → test.db only) ----------

def test_create_company():
    response = client.post(
        "/companies",
        json={
            "name": "Aramex",
            "city": "Amman",
            "jobs": [{"title": "Data Analyst"}, {"title": "AI Engineer"}],
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Aramex"
    assert len(response.json()["jobs"]) == 2
    assert response.json()["jobs"][0]["title"] == "Data Analyst"


def test_get_company():
    # runs after test_create_company → the test database has company 1
    response = client.get("/companies/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Aramex"


def test_create_job_for_missing_company():
    response = client.post("/jobs", json={"title": "Ghost Job", "company_id": 999})
    assert response.status_code == 404


# ---------- list: jobs ----------

def test_list_jobs_default():
    response = client.get("/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_jobs_limit():
    response = client.get("/jobs?limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_jobs_bad_limit():
    response = client.get("/jobs?limit=0")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "limit"]


def test_list_jobs_title():
    # test DB has "Data Analyst" + "AI Engineer" → search must return ONLY the engineer
    response = client.get("/jobs?title=Engineer")      # lowercase on purpose
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) >= 1
    assert all("engineer" in j["title"].lower() for j in jobs)


def test_list_jobs_unknown_company():
    response = client.get("/jobs?company_id=999")
    assert response.status_code == 200
    assert response.json() == []


# ---------- list: companies ----------

def test_list_companies_city():
    response = client.get("/companies?city=Amman")
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) >= 1
    assert all(c["city"] == "Amman" for c in companies)


def test_list_companies_unknown_city():
    response = client.get("/companies?city=Cairo")
    assert response.status_code == 200
    assert response.json() == []





# ---------- update + delete ----------

def test_patch_job_title():
    r = client.post("/companies", json={
        "name": "PatchCo", "city": "Zarqa", "jobs": [{"title": "Junior Dev"}],
    })
    job_id = r.json()["jobs"][0]["id"]

    response = client.patch(f"/jobs/{job_id}", json={"title": "Senior Dev"})

    assert response.status_code == 200
    assert response.json()["title"] == "Senior Dev"
    assert client.get(f"/jobs/{job_id}").json()["title"] == "Senior Dev"


def test_patch_job_bad_company():
    r = client.post("/companies", json={
        "name": "MoveCo", "city": "Irbid", "jobs": [{"title": "Tester"}],
    })
    job_id = r.json()["jobs"][0]["id"]

    response = client.patch(f"/jobs/{job_id}", json={"company_id": 999})

    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found"


def test_delete_job():
    r = client.post("/companies", json={
        "name": "DeleteCo", "city": "Aqaba", "jobs": [{"title": "Temp Job"}],
    })
    job_id = r.json()["jobs"][0]["id"]

    response = client.delete(f"/jobs/{job_id}")
    assert response.status_code == 204
    assert client.get(f"/jobs/{job_id}").status_code == 404



def test_delete_missing_job():
    response = client.delete("/jobs/9999")
    assert response.status_code == 404
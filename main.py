from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import CompanyDB, jobDB
from schemas import (
    company_create,
    company_detail_out,
    company_out,
    job_create,
    job_out,
)

# the models are imported above → Base knows both tables → create them
Base.metadata.create_all(engine)

app = FastAPI()


# ---------------- JOBS ----------------
@app.get("/jobs", response_model=list[job_out])
def list_jobs(
    company_id: int | None = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_db),
):
    stmt = select(jobDB)
    if company_id is not None:
        stmt = stmt.where(jobDB.company_id == company_id)
    stmt = stmt.order_by(jobDB.id).offset(offset).limit(limit)
    jobs = session.scalars(stmt).all()
    return [job_out.model_validate(j) for j in jobs]


@app.get("/jobs/{job_id}", response_model=job_out)
def get_job(job_id: int, session: Session = Depends(get_db)):
    job = session.get(jobDB, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job_out.model_validate(job)


@app.post("/jobs", response_model=job_out, status_code=status.HTTP_201_CREATED)
def create_job(job: job_create, session: Session = Depends(get_db)):
    company = session.get(CompanyDB, job.company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    new_job = jobDB(title=job.title, company_id=job.company_id)
    session.add(new_job)
    session.commit()
    return job_out.model_validate(new_job)      # the NEW DB object (has an id)


# ---------------- COMPANIES ----------------
@app.get("/companies", response_model=list[company_out])
def list_companies(
    city: str | None = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_db),
):
    stmt = select(CompanyDB)
    if city is not None:
        stmt = stmt.where(CompanyDB.city == city)
    stmt = stmt.order_by(CompanyDB.id).offset(offset).limit(limit)
    companies = session.scalars(stmt).all()
    return [company_out.model_validate(c) for c in companies]


@app.get("/companies/{company_id}", response_model=company_detail_out)
def get_company(company_id: int, session: Session = Depends(get_db)):
    company = session.get(CompanyDB, company_id)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company_detail_out.model_validate(company)


@app.post("/companies", response_model=company_detail_out, status_code=status.HTTP_201_CREATED)
def create_company(data: company_create, session: Session = Depends(get_db)):
    company = CompanyDB(name=data.name, city=data.city)
    for j in data.jobs:
        company.jobs.append(jobDB(title=j.title))   # Pydantic input → DB object
    session.add(company)
    session.commit()
    return company_detail_out.model_validate(company)
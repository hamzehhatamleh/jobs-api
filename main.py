from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import CompanyDB, jobDB
from schemas import company_create, job_create

# the models are imported above → Base knows both tables → create them
Base.metadata.create_all(engine)

app = FastAPI()


@app.get("/jobs/{job_id}")
def get_job(job_id: int, session: Session = Depends(get_db)):
    job = session.get(jobDB, job_id)

    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    return {"id": job.id, "title": job.title, "company_id": job.company_id}


@app.post("/jobs", status_code=status.HTTP_201_CREATED)
def create_job(job: job_create, session: Session = Depends(get_db)):
    company = session.get(CompanyDB, job.company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {job.company_id} does not exist.",
        )

    new_job = jobDB(title=job.title, company_id=job.company_id)
    session.add(new_job)
    session.commit()

    return {"id": new_job.id, "title": new_job.title, "company_id": new_job.company_id}


@app.post("/companies", status_code=status.HTTP_201_CREATED)
def create_company(comp: company_create, session: Session = Depends(get_db)):
    new_company = CompanyDB(name=comp.name, city=comp.city)

    for job in comp.jobs:
        new_company.jobs.append(jobDB(title=job.title))

    session.add(new_company)
    session.commit()

    return {
        "id": new_company.id,
        "name": new_company.name,
        "city": new_company.city,
        "jobs": [{"id": job.id, "title": job.title} for job in new_company.jobs],
    }


@app.get("/companies/{company_id}")
def get_company(company_id: int, session: Session = Depends(get_db)):
    company = session.get(CompanyDB, company_id)

    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    return {
        "id": company.id,
        "name": company.name,
        "city": company.city,
        "jobs": [{"id": job.id, "title": job.title} for job in company.jobs],
    }
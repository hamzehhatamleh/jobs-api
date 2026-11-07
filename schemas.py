from pydantic import BaseModel, Field

class job_create(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    company_id: int = Field(gt=0)


# a job INSIDE a new company → the company is known from the JSON shape
class job_in_company(BaseModel):
    title: str = Field(min_length=2, max_length=100)


class company_create(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    city: str = Field(min_length=2, max_length=50)
    jobs: list[job_in_company] = Field(min_length=1)

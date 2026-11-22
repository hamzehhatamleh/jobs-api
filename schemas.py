from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- INPUT (what the client sends) ----------
class job_create(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    company_id: int = Field(gt=0)
    salary: int | None = Field(default=None, ge=0)          # ✏️ added ge=0


class job_in_company(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    salary: int | None = Field(default=None, ge=0)


class company_create(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    city: str = Field(min_length=2, max_length=50)
    jobs: list[job_in_company] = Field(min_length=1)


class company_update(BaseModel):
    pass


class job_update(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=100)
    company_id: int | None = Field(default=None, gt=0)
    salary: int | None = Field(default=None, ge=0)          # ✏️ added ge=0


# ---------- OUTPUT (what we send back) ----------
class job_out(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    company_id: int
    salary: int | None = None


class job_in_company_out(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    salary: int | None = None                               # ✏️ new


class company_out(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    city: str


class company_detail_out(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    city: str
    jobs: list[job_in_company_out]
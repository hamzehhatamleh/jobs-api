from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class CompanyDB(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(50))

    # Python only, no column: company.jobs → list of jobs
    jobs: Mapped[list["jobDB"]] = relationship(back_populates="company")


class jobDB(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    # the real link in the database (on the MANY side)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))

    # Python only, no column: job.company → one company
    company: Mapped["CompanyDB"] = relationship(back_populates="jobs")
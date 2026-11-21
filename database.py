import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

# one database = one engine = many tables

db_url = os.getenv("DB_URL", default="sqlite:///companies.db")
engine = create_engine(db_url)

# the shared "notebook" every table class registers in
class Base(DeclarativeBase):
    pass


# one session per request: open → give it to the route → close after the route
def get_db():
    with Session(engine) as session:
        yield session
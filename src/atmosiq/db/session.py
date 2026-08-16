import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Dev default is SQLite so the repo runs out-of-the-box; set DATABASE_URL for PostgreSQL in production.
DEFAULT_URL = "sqlite:///atmosiq.db"


def database_url():
    url = os.getenv("DATABASE_URL", DEFAULT_URL)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def get_engine(url=None):
    return create_engine(url or database_url(), pool_pre_ping=True)


SessionLocal = sessionmaker(expire_on_commit=False)


def get_session(url=None):
    engine = get_engine(url)
    SessionLocal.configure(bind=engine)
    return SessionLocal()

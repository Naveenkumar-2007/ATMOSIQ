import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

load_dotenv()

# Dev default is SQLite so the repo runs out-of-the-box; set DATABASE_URL for PostgreSQL in production.
DEFAULT_URL = "sqlite:///atmosiq.db"
FALLBACK_URL = "sqlite:////tmp/atmosiq.db"


def database_url():
    url = os.getenv("DATABASE_URL", DEFAULT_URL)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _engine_for(url):
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


def _verify_engine(engine):
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def get_engine(url=None):
    selected_url = url or database_url()
    try:
        engine = _engine_for(selected_url)
        _verify_engine(engine)
        return engine
    except Exception:
        if url is not None:
            raise

    fallback_url = os.getenv("ATMOSIQ_FALLBACK_DATABASE_URL", FALLBACK_URL)
    fallback_engine = _engine_for(fallback_url)
    _verify_engine(fallback_engine)
    return fallback_engine


SessionLocal = sessionmaker(expire_on_commit=False)


def get_session(url=None):
    engine = get_engine(url)
    SessionLocal.configure(bind=engine)
    return SessionLocal()

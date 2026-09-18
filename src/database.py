"""
Database connection and session management.

Uses SQLite for local development (zero setup, built into Python).
Swap DATABASE_URL to a Postgres URL when you deploy — the rest of
this file and your models work unchanged either way.
"""
import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import declarative_base

# Local dev default: SQLite file in your project root.
# For production/Postgres later: postgresql://user:password@host:5432/dbname
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./secure_api_dev.db")

_is_sqlite = DATABASE_URL.startswith("sqlite")

_engine_kwargs = {"echo": os.environ.get("SQL_ECHO", "false").lower() == "true"}
if _is_sqlite:
    # SQLite needs this because each request may use a different thread.
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs.update(pool_pre_ping=True, pool_size=5, max_overflow=10)

engine = create_engine(DATABASE_URL, **_engine_kwargs)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()
Base.query = SessionLocal.query_property()


@contextmanager
def get_db_session():
    """
    Context manager for a database session with automatic commit/rollback.

    Usage:
        with get_db_session() as db:
            user = db.query(User).filter_by(username="alice").first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Create all tables directly (dev convenience). Prefer Alembic for real changes."""
    import src.models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def teardown_session(exception=None):
    SessionLocal.remove()
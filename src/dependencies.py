"""
FastAPI dependency for database sessions.

Use this instead of Flask's teardown_appcontext pattern — FastAPI
injects and closes the session per-request via Depends().
"""
from typing import Generator

from src.database import SessionLocal


def get_db() -> Generator:
    """
    Yields a DB session for the duration of a single request,
    then closes it automatically — even if the route raises.

    Usage in a route:

        from fastapi import Depends
        from src.dependencies import get_db
        from sqlalchemy.orm import Session

        @app.post("/login")
        def login(credentials: LoginRequest, db: Session = Depends(get_db)):
            user = db.query(User).filter_by(username=credentials.username).first()
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
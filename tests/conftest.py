import os
import tempfile

# Point at an isolated test database BEFORE any src module is imported,
# so tests never touch your real dev database (secure_api_dev.db).
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db_path}"

from src.database import Base, engine, SessionLocal  # noqa: E402
from src.models import User, UserRole  # noqa: E402

Base.metadata.create_all(bind=engine)

_db = SessionLocal()

_admin = User(username="admin-user", email="admin-user@example.com", role=UserRole.ADMIN)
_admin.set_password("AdminPass@123")
_db.add(_admin)

_analyst = User(username="security-user", email="security-user@example.com", role=UserRole.ANALYST)
_analyst.set_password("DevSecOps@123")
_db.add(_analyst)

_db.commit()
_db.close()
from src.main import limiter
limiter.enabled = False
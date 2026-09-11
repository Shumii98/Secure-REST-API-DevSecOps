"""
Run once to create the first admin user:
    python -m scripts.seed_admin
"""
from src.database import SessionLocal
from src.models import User, UserRole

db = SessionLocal()

existing = db.query(User).filter_by(username="admin").first()
if existing:
    print("Admin user already exists — skipping.")
else:
    admin = User(username="admin", email="admin@example.com", role=UserRole.ADMIN)
    admin.set_password("change-me-immediately")
    db.add(admin)
    db.commit()
    print("Admin user created — username: admin, password: change-me-immediately")
    print("Log in and change this password right away.")

db.close()
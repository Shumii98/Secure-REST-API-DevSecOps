from pwdlib import PasswordHash

from src.database import SessionLocal
from src.models import User

password_hash = PasswordHash.recommended()


def get_user(username: str):
    """
    Looks up a user in the real database instead of the old
    hardcoded USERS dict.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if not user or not user.is_active:
            return None

        return {
            "id": user.id,
            "username": user.username,
            "password_hash": user.password_hash,
            "role": user.role.value,
        }
    finally:
        db.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
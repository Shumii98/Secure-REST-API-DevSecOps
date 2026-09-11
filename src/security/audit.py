from src.database import SessionLocal
from src.models import AuditLog


def log_event(event_type: str, user_id: str = None, ip_address: str = None, detail: str = None):
    """
    Records an auth-related event (login success/failure, logout, etc.)
    into the audit_logs table.
    """
    db = SessionLocal()
    try:
        db.add(AuditLog(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            detail=detail,
        ))
        db.commit()
    finally:
        db.close()
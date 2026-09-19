from src.database import SessionLocal
from src.models import AuditLog


def log_event(
    event_type: str,
    user_id: str | None = None,
    ip_address: str | None = None,
    detail: str | None = None,
    request_id: str | None = None,
):
    """
    Records a security event into the audit_logs table.

    The request_id can be used to correlate the database audit
    record with structured application logs.
    """

    db = SessionLocal()

    try:
        if request_id:
            if detail:
                detail = f"{detail} request_id={request_id}"
            else:
                detail = f"request_id={request_id}"

        db.add(
            AuditLog(
                user_id=user_id,
                event_type=event_type,
                ip_address=ip_address,
                detail=detail,
            )
        )

        db.commit()

    finally:
        db.close()
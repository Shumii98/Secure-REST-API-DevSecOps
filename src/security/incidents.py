
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models import Incident
from src.security.auth import verify_token
from src.security.schemas import IncidentCreate, IncidentResponse


router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incidents"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(
    incident: IncidentCreate,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    owner_id = token.get("sub")

    if not owner_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    db_incident = Incident(
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status="open",
        owner_id=owner_id,
    )

    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    return db_incident


@router.get(
    "",
    response_model=list[IncidentResponse],
)
def list_incidents(
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    owner_id = token.get("sub")

    if not owner_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    incidents = (
        db.query(Incident)
        .filter(Incident.owner_id == owner_id)
        .order_by(Incident.created_at.desc())
        .all()
    )

    return incidents


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident(
    incident_id: str,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    owner_id = token.get("sub")

    if not owner_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id,
            Incident.owner_id == owner_id,
        )
        .first()
    )

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return incident

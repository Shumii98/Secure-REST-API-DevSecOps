from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    severity: str = Field(default="medium", max_length=20)


class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str | None
    severity: str
    status: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
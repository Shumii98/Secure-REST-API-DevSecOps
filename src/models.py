"""
SQLAlchemy models for the Secure REST API.

Uses a plain String(36) for IDs instead of Postgres's native UUID type,
so this works identically on SQLite (dev) and Postgres (prod) without
any changes when you switch DATABASE_URL later.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from pwdlib import PasswordHash

from src.database import Base


_password_hash = PasswordHash.recommended()


def _uuid():
    return str(uuid.uuid4())


def _utcnow():
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    ANALYST = "analyst"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_uuid)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def set_password(self, plain_password: str) -> None:
        self.password_hash = _password_hash.hash(plain_password)

    def check_password(self, plain_password: str) -> bool:
        return _password_hash.verify(
            plain_password,
            self.password_hash,
        )

    def to_dict(self, include_email: bool = True) -> dict:
        data = {
            "id": self.id,
            "username": self.username,
            "role": (
                self.role.value
                if isinstance(self.role, UserRole)
                else self.role
            ),
            "is_active": self.is_active,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }

        if include_email:
            data["email"] = self.email

        return data

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )
    token_hash = Column(
        String(255),
        nullable=False,
        unique=True,
    )
    issued_at = Column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    revoked_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="refresh_tokens",
    )

    __table_args__ = (
        Index(
            "ix_refresh_tokens_user_id_revoked",
            "user_id",
            "revoked",
        ),
    )

    def is_valid(self) -> bool:
        expires_at = self.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        return (
            not self.revoked
            and expires_at > _utcnow()
        )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
    )
    event_type = Column(
        String(50),
        nullable=False,
    )
    ip_address = Column(
        String(45),
        nullable=True,
    )
    detail = Column(
        String(500),
        nullable=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_audit_logs_event_type_created_at",
            "event_type",
            "created_at",
        ),
    )


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=_uuid)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    severity = Column(
        String(20),
        nullable=False,
        default="medium",
    )
    status = Column(
        String(20),
        nullable=False,
        default="open",
    )
    owner_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )

    owner = relationship("User")

    __table_args__ = (
        Index(
            "ix_incidents_owner_id",
            "owner_id",
        ),
        Index(
            "ix_incidents_severity_status",
            "severity",
            "status",
        ),
    )
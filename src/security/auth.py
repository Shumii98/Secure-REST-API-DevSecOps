import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.database import SessionLocal
from src.models import RefreshToken
from src.security.jwt_config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_AUDIENCE,
    JWT_ISSUER,
    JWT_SECRET_KEY,
)

REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()


def create_access_token(data: dict) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = data.copy()
    payload["iat"] = now
    payload["exp"] = expire
    payload["jti"] = str(uuid.uuid4())
    payload["type"] = "access"
    payload["iss"] = JWT_ISSUER
    payload["aud"] = JWT_AUDIENCE

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def _hash_token(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def create_refresh_token(data: dict) -> str:
    """
    Issues a refresh token and records it in the database
    so that it can later be revoked.
    """
    payload = data.copy()
    user_id = payload.pop("user_id")

    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    jti = str(uuid.uuid4())

    payload["iat"] = now
    payload["exp"] = expire
    payload["jti"] = jti
    payload["type"] = "refresh"
    payload["iss"] = JWT_ISSUER
    payload["aud"] = JWT_AUDIENCE

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    db = SessionLocal()

    try:
        db.add(
            RefreshToken(
                user_id=user_id,
                token_hash=_hash_token(jti),
                expires_at=expire,
            )
        )
        db.commit()
    finally:
        db.close()

    return token


def verify_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    jti = payload.get("jti")

    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    db = SessionLocal()

    try:
        record = (
            db.query(RefreshToken)
            .filter_by(token_hash=_hash_token(jti))
            .first()
        )

        if not record or not record.is_valid():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked or expired",
            )
    finally:
        db.close()

    return payload


def revoke_refresh_token(token: str) -> None:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
        )
    except jwt.InvalidTokenError:
        return

    jti = payload.get("jti")

    if not jti:
        return

    db = SessionLocal()

    try:
        record = (
            db.query(RefreshToken)
            .filter_by(token_hash=_hash_token(jti))
            .first()
        )

        if record:
            record.revoked = True
            record.revoked_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def require_role(required_role: str):
    def role_checker(payload: dict = Depends(verify_token)):
        if payload.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return payload

    return role_checker
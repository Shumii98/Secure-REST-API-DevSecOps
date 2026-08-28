from fastapi import Depends, FastAPI, HTTPException, status

from src.security.auth import create_access_token, verify_token
from src.security.middleware import SecurityHeadersMiddleware
from src.security.schemas import LoginRequest, TokenResponse
from src.security.users import (
    DEMO_PASSWORD_HASH,
    DEMO_USERNAME,
    password_hash,
)


app = FastAPI(
    title="Secure REST API",
    description="A security-focused REST API built with DevSecOps practices.",
    version="1.0.0",
)


app.add_middleware(SecurityHeadersMiddleware)


@app.get("/")
def root():
    return {
        "message": "Secure REST API is running",
        "status": "ok",
    }


@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    if request.username != DEMO_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not password_hash.verify(
        request.password,
        DEMO_PASSWORD_HASH,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        {"sub": DEMO_USERNAME}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.get("/health")
def health_check(token=Depends(verify_token)):
    return {
        "status": "healthy",
    }


@app.get("/api/v1/profile")
def get_profile(token=Depends(verify_token)):
    return {
        "username": token.get("sub"),
        "role": "analyst",
        "message": "Authenticated access granted",
    }
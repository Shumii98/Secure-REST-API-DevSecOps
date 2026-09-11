from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Depends, FastAPI, HTTPException, Request, status

from src.security.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    require_role,
    verify_refresh_token,
    revoke_refresh_token,
)
from src.security.schemas import LoginRequest, TokenResponse, RefreshRequest
from src.security.middleware import SecurityHeadersMiddleware
from src.security.users import get_user, verify_password
from src.security.audit import log_event


app = FastAPI(
    title="Secure REST API",
    description="A security-focused REST API built with DevSecOps practices.",
    version="1.0.0",
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/")
def root():
    return {"message": "Secure REST API is running", "status": "ok"}


@app.post("/auth/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, body: LoginRequest):
    user = get_user(body.username)
    client_ip = request.client.host if request.client else None

    if not user or not verify_password(body.password, user["password_hash"]):
        log_event(
            "login_failed",
            ip_address=client_ip,
            detail=f"username={body.username}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        {"sub": user["username"], "role": user["role"]}
    )
    refresh_token = create_refresh_token(
        {"sub": user["username"], "user_id": user["id"]}
    )

    log_event("login_success", user_id=user["id"], ip_address=client_ip)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/auth/refresh", response_model=TokenResponse)
def refresh(request: Request, body: RefreshRequest):
    payload = verify_refresh_token(body.refresh_token)
    user = get_user(payload["sub"])
    client_ip = request.client.host if request.client else None

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    revoke_refresh_token(body.refresh_token)

    access_token = create_access_token(
        {"sub": user["username"], "role": user["role"]}
    )
    new_refresh_token = create_refresh_token(
        {"sub": user["username"], "user_id": user["id"]}
    )

    log_event("token_refreshed", user_id=user["id"], ip_address=client_ip)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@app.post("/auth/logout")
def logout(request: Request, body: RefreshRequest):
    revoke_refresh_token(body.refresh_token)
    client_ip = request.client.host if request.client else None
    log_event("logout", ip_address=client_ip)
    return {"message": "Logged out successfully"}


@app.get("/health")
def health_check(token=Depends(verify_token)):
    return {"status": "healthy"}


@app.get("/api/v1/profile")
def get_profile(token=Depends(verify_token)):
    return {
        "username": token.get("sub"),
        "role": token.get("role"),
        "message": "Authenticated access granted",
    }


@app.get("/api/v1/admin/dashboard")
def admin_dashboard(token=Depends(require_role("admin"))):
    return {
        "message": "Welcome to the admin dashboard",
        "username": token.get("sub"),
    }
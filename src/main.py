from fastapi import Depends, FastAPI, HTTPException, status

from src.security.auth import create_access_token, verify_token, require_role
from src.security.middleware import SecurityHeadersMiddleware
from src.security.schemas import LoginRequest, TokenResponse
from src.security.users import get_user, verify_password


app = FastAPI(
    title="Secure REST API",
    description="A security-focused REST API built with DevSecOps practices.",
    version="1.0.0",
)

app.add_middleware(SecurityHeadersMiddleware)


@app.get("/")
def root():
    return {"message": "Secure REST API is running", "status": "ok"}


@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    user = get_user(request.username)

    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        {"sub": user["username"], "role": user["role"]}
    )

    return {"access_token": access_token, "token_type": "bearer"}


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
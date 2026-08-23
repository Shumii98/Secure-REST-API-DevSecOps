from fastapi import FastAPI, Depends

from src.security.auth import verify_token
from src.security.middleware import SecurityHeadersMiddleware

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


@app.get("/health")
def health_check(token=Depends(verify_token)):
    return {
        "status": "healthy",
    }


@app.get("/api/v1/profile")
def get_profile(token=Depends(verify_token)):
    return {
        "username": "security-user",
        "role": "analyst",
        "message": "Authenticated access granted",
    }
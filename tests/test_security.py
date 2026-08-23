from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


# 1. Health endpoint rejects missing authentication
def test_health_requires_authentication():
    response = client.get("/health")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# 2. Health endpoint rejects invalid token
def test_health_rejects_invalid_token():
    response = client.get(
        "/health",
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401


# 3. Health endpoint accepts valid token
def test_health_accepts_valid_token():
    response = client.get(
        "/health",
        headers={"Authorization": "Bearer dev-secret-token"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# 4. Security headers are present
def test_security_headers():
    response = client.get("/")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Permissions-Policy"] == (
        "geolocation=(), microphone=(), camera=()"
    )


# 5. Profile endpoint rejects missing authentication
def test_profile_requires_authentication():
    response = client.get("/api/v1/profile")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


# 6. Profile endpoint accepts valid token
def test_profile_accepts_valid_token():
    response = client.get(
        "/api/v1/profile",
        headers={"Authorization": "Bearer dev-secret-token"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "security-user"
    assert response.json()["role"] == "analyst"


# 7. Profile endpoint rejects invalid token
def test_profile_rejects_invalid_token():
    response = client.get(
        "/api/v1/profile",
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401


# 8. Root endpoint is publicly accessible
def test_root_is_public():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# 9. Security headers are present on protected endpoint responses
def test_security_headers_on_protected_endpoint():
    response = client.get(
        "/health",
        headers={"Authorization": "Bearer dev-secret-token"},
    )

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Permissions-Policy"] == (
        "geolocation=(), microphone=(), camera=()"
    )
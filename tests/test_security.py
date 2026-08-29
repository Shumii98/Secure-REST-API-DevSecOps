
from fastapi.testclient import TestClient

from src.main import app
from src.security.auth import create_access_token


client = TestClient(app)


def get_valid_token():
    return create_access_token({"sub": "security-user"})


def test_health_requires_authentication():
    response = client.get("/health")

    assert response.status_code == 401


def test_health_rejects_invalid_token():
    response = client.get(
        "/health",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_health_accepts_valid_token():
    token = get_valid_token()

    response = client.get(
        "/health",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_security_headers():
    response = client.get("/")

    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_profile_requires_authentication():
    response = client.get("/api/v1/profile")

    assert response.status_code == 401


def test_profile_accepts_valid_token():
    token = get_valid_token()

    response = client.get(
        "/api/v1/profile",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "security-user"


def test_profile_rejects_invalid_token():
    response = client.get(
        "/api/v1/profile",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_root_is_public():
    response = client.get("/")

    assert response.status_code == 200


def test_security_headers_on_protected_endpoint():
    token = get_valid_token()

    response = client.get(
        "/health",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_analyst_cannot_access_admin_dashboard():
    login_response = client.post(
        "/auth/login",
        json={
            "username": "security-user",
            "password": "DevSecOps@123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_admin_can_access_admin_dashboard():
    login_response = client.post(
        "/auth/login",
        json={
            "username": "admin-user",
            "password": "AdminPass@123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "admin-user"


def test_profile_returns_correct_role():
    login_response = client.post(
        "/auth/login",
        json={
            "username": "security-user",
            "password": "DevSecOps@123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/profile",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "analyst"


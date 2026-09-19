
from fastapi.testclient import TestClient

from src.main import app
from src.security.auth import create_access_token

client = TestClient(app)


def get_valid_token():
    return create_access_token({"sub": "security-user"})



def test_health_is_public():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_ignores_invalid_token():
    response = client.get(
        "/health",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


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


def test_refresh_token_returns_new_tokens():
    login_response = client.post(
        "/auth/login",
        json={
            "username": "admin-user",
            "password": "AdminPass@123",
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_refresh_token_rotation_invalidates_old_token():
    login_response = client.post(
        "/auth/login",
        json={
            "username": "admin-user",
            "password": "AdminPass@123",
        },
    )

    assert login_response.status_code == 200

    old_refresh_token = login_response.json()["refresh_token"]

    client.post(
        "/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )

    assert response.status_code == 401


def test_logout_revokes_refresh_token():
    login_response = client.post(
        "/auth/login",
        json={
            "username": "admin-user",
            "password": "AdminPass@123",
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token},
    )

    assert logout_response.status_code == 200

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 401


def test_login_writes_audit_log():
    from src.database import SessionLocal
    from src.models import AuditLog

    client.post(
        "/auth/login",
        json={
            "username": "admin-user",
            "password": "AdminPass@123",
        },
    )

    db = SessionLocal()

    logs = (
        db.query(AuditLog)
        .filter_by(event_type="login_success")
        .all()
    )

    db.close()

    assert len(logs) >= 1


def test_create_incident_requires_authentication():
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Unauthorized Incident",
            "description": "This should not be created",
            "severity": "high",
        },
    )

    assert response.status_code == 401


def test_authenticated_user_can_create_incident():
    login_response = client.post(
        "/auth/login",
        json={
            "username": "security-user",
            "password": "DevSecOps@123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Suspicious Login Activity",
            "description": "Multiple failed authentication attempts detected.",
            "severity": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Suspicious Login Activity"
    assert data["severity"] == "high"
    assert data["status"] == "open"
    assert data["owner_id"]


def test_incident_owner_can_retrieve_incident():
    login_response = client.post(
        "/auth/login",
        json={
            "username": "security-user",
            "password": "DevSecOps@123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    create_response = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Owner Access Test",
            "description": "Incident owner should be able to retrieve it.",
            "severity": "medium",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/incidents/{incident_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == incident_id


def test_user_cannot_access_another_users_incident():
    owner_login = client.post(
        "/auth/login",
        json={
            "username": "security-user",
            "password": "DevSecOps@123",
        },
    )

    assert owner_login.status_code == 200

    owner_token = owner_login.json()["access_token"]

    create_response = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "title": "BOLA Security Test",
            "description": "This incident belongs to security-user.",
            "severity": "critical",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.json()["id"]

    other_user_token = create_access_token(
        {
            "sub": "admin-user",
            "role": "admin",
        }
    )

    response = client.get(
        f"/api/v1/incidents/{incident_id}",
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert response.status_code == 404


def test_list_incidents_requires_authentication():
    response = client.get("/api/v1/incidents")

    assert response.status_code == 401


def test_authenticated_user_can_list_own_incidents():
    login_response = client.post(
        "/auth/login",
        json={
            "username": "security-user",
            "password": "DevSecOps@123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    create_response = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Incident List Test",
            "description": "Testing authenticated incident listing.",
            "severity": "medium",
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    assert any(
        incident["title"] == "Incident List Test"
        for incident in data
    )


def test_user_only_sees_own_incidents():
    owner_login = client.post(
        "/auth/login",
        json={
            "username": "security-user",
            "password": "DevSecOps@123",
        },
    )

    assert owner_login.status_code == 200

    owner_token = owner_login.json()["access_token"]

    create_response = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "title": "Private Incident",
            "description": "This incident belongs to security-user.",
            "severity": "high",
        },
    )

    assert create_response.status_code == 201

    admin_token = create_access_token(
        {
            "sub": "admin-user",
            "role": "admin",
        }
    )

    response = client.get(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200

    incidents = response.json()

    assert all(
        incident["title"] != "Private Incident"
        for incident in incidents
    )


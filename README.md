# Secure REST API – DevSecOps

A security-focused REST API built with **FastAPI**, demonstrating practical **DevSecOps, application security, authentication, authorization, secure API design, and security testing** practices.

The project implements JWT authentication, refresh-token rotation and revocation, role-based access control (RBAC), password hashing, security headers, rate limiting, audit logging, security incident management, database migrations, automated testing, dependency auditing, and GitHub Actions CI.

---

## Overview

The project demonstrates how security controls can be integrated throughout the software development lifecycle rather than being added only after application development.

### Security Capabilities

* JWT Bearer-token authentication
* Access and refresh token support
* Refresh-token rotation and server-side revocation
* Protected API endpoints
* Role-Based Access Control (RBAC)
* Password hashing with `pwdlib`
* HTTP security headers through custom middleware
* JWT expiration handling
* Authentication rate limiting
* Authentication audit logging
* Security incident management API
* User ownership controls for incidents
* SQLAlchemy database layer
* Alembic database migrations
* Environment-based configuration
* Automated security testing with `pytest`
* Dependency vulnerability scanning with `pip-audit`
* GitHub Actions Security CI
* Versioned API endpoints

The goal is to demonstrate a practical **Secure SDLC / DevSecOps workflow** for a Python REST API.

---

## Security Architecture

```text
                         ┌──────────────────────┐
                         │      API Client      │
                         └──────────┬───────────┘
                                    │
                              HTTP Request
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     FastAPI API      │
                         └──────────┬───────────┘
                                    │
                   ┌────────────────┴────────────────┐
                   │                                 │
                   ▼                                 ▼
          ┌──────────────────┐             ┌──────────────────┐
          │ JWT Authentication│             │ Security Headers │
          │ Bearer Tokens     │             │ Middleware       │
          └────────┬─────────┘             └────────┬─────────┘
                   │                                 │
                   └──────────────┬──────────────────┘
                                  │
                                  ▼
                         ┌──────────────────────┐
                         │ Authorization / RBAC │
                         │ Role Verification    │
                         └──────────┬───────────┘
                                    │
                       ┌────────────┴────────────┐
                       │                         │
                       ▼                         ▼
                ┌───────────────┐         ┌─────────────────┐
                │ Analyst User  │         │   Admin User    │
                │ Standard      │         │ Elevated Access │
                └───────┬───────┘         └────────┬────────┘
                        │                            │
                        ▼                            ▼
                ┌───────────────┐         ┌─────────────────┐
                │ Profile API   │         │ Admin Dashboard │
                └───────┬───────┘         └────────┬────────┘
                        │                            │
                        └────────────┬───────────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │ Incident Management  │
                          │ API + Audit Logging  │
                          └──────────┬───────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │ SQLAlchemy Database  │
                          │ SQLite / Migrations  │
                          └──────────────────────┘
```

---

## DevSecOps CI Pipeline

```text
Git Push / Pull Request
            │
            ▼
   ┌─────────────────────┐
   │   GitHub Actions     │
   │    Security CI       │
   └──────────┬──────────┘
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
   ┌─────────┐   ┌─────────────┐
   │  pytest │   │  pip-audit  │
   │ Security│   │ Dependency  │
   │  Tests  │   │    Scan     │
   └────┬────┘   └──────┬──────┘
        │               │
        └───────┬───────┘
                ▼
        ┌─────────────┐
        │  CI Result  │
        └─────────────┘
```

---

# Security Controls

## 1. JWT Authentication

The API uses **JSON Web Tokens (JWT)** for authentication.

Authentication flow:

```text
Username + Password
        │
        ▼
POST /auth/login
        │
        ▼
Credentials validated
        │
        ▼
Access + Refresh Tokens generated
        │
        ▼
Authorization: Bearer <token>
        │
        ▼
Protected endpoint
```

JWT access tokens contain information such as:

* `sub` — authenticated username
* `role` — authorization role
* `exp` — token expiration timestamp

Protected endpoints reject requests without valid authentication.

Invalid or expired access tokens result in:

```text
401 Unauthorized
```

---

## 2. Refresh Token Security

The API supports refresh tokens to obtain new access tokens without requiring the user to log in again.

The implementation includes:

* Refresh-token generation
* Refresh-token verification
* Token rotation
* Server-side revocation
* Logout-based revocation
* Rejection of previously rotated/revoked refresh tokens

Example flow:

```text
Login
  │
  ├── Access Token
  │
  └── Refresh Token
          │
          ▼
    POST /auth/refresh
          │
          ▼
 Old refresh token revoked
          │
          ▼
 New access + refresh tokens
```

---

## 3. Role-Based Access Control

The API implements role-based authorization using the role contained in the authenticated JWT.

Demonstration roles include:

| Role      | Access                                    |
| --------- | ----------------------------------------- |
| `analyst` | Authenticated profile and incident access |
| `admin`   | Administrative dashboard access           |

Administrator endpoint:

```text
GET /api/v1/admin/dashboard
```

An authenticated analyst attempting to access the administrator endpoint receives:

```text
403 Forbidden
```

An authorized administrator receives:

```text
200 OK
```

This demonstrates the distinction between authentication and authorization:

* **401 Unauthorized** — authentication is missing or invalid.
* **403 Forbidden** — authentication succeeded, but the user lacks the required authorization.

---

## 4. Password Security

User passwords are not stored as plaintext.

The project uses `pwdlib` and Argon2-based password hashing for password protection and verification.

User data is managed through:

* SQLAlchemy ORM
* SQLite for local development
* Alembic database migrations

The database layer can be adapted for a production database such as PostgreSQL.

---

## 5. Public and Protected Endpoints

The health endpoint is intentionally **public** so monitoring systems can verify API availability without authentication.

```text
GET /
GET /health
POST /auth/login
POST /auth/refresh
POST /auth/logout
```

Protected functionality includes:

```text
GET /api/v1/profile
GET /api/v1/admin/dashboard
GET /api/v1/incidents
POST /api/v1/incidents
GET /api/v1/incidents/{incident_id}
```

The admin dashboard additionally requires the `admin` role.

---

## 6. Security Headers

Security-related HTTP response headers are applied through custom middleware.

Current headers include:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Permissions-Policy: geolocation=(),microphone=(),camera=()
```

These controls help reduce risks such as MIME sniffing, clickjacking, unnecessary referrer exposure, and unwanted browser feature access.

---

## 7. Rate Limiting

Authentication requests are rate-limited using `slowapi`.

The login endpoint is protected against excessive authentication attempts:

```text
POST /auth/login
5 requests per minute
```

This provides a basic control against automated credential-guessing attempts.

---

## 8. Audit Logging

Authentication-related security events are recorded through the audit logging component.

Examples include:

```text
login_success
login_failed
token_refreshed
logout
```

Audit records include relevant security context such as the user and client IP where available.

This provides an auditable trail for authentication activity.

---

## 9. Security Incident Management

The API includes a dedicated incident-management component.

Incident functionality includes:

* Creating security incidents
* Retrieving incidents
* Listing authenticated users' incidents
* Incident severity
* Incident status
* Incident ownership
* Authorization checks
* Protection against unauthorized incident access

Example incident endpoint:

```text
POST /api/v1/incidents
```

Example incident structure:

```json
{
  "title": "Suspicious Login Activity",
  "description": "Multiple failed authentication attempts detected.",
  "severity": "high"
}
```

The implementation also tests ownership controls to ensure that one user cannot retrieve another user's incident.

---

# API Endpoints

| Method | Endpoint                          | Authentication | Purpose                                   |
| ------ | --------------------------------- | -------------- | ----------------------------------------- |
| `GET`  | `/`                               | Public         | API status                                |
| `GET`  | `/health`                         | Public         | Health check                              |
| `POST` | `/auth/login`                     | Public         | Authenticate and issue tokens             |
| `POST` | `/auth/refresh`                   | Public         | Rotate refresh token and issue new tokens |
| `POST` | `/auth/logout`                    | Public         | Revoke refresh token                      |
| `GET`  | `/api/v1/profile`                 | Required       | Retrieve authenticated profile            |
| `GET`  | `/api/v1/admin/dashboard`         | Admin          | Administrator dashboard                   |
| `POST` | `/api/v1/incidents`               | Required       | Create security incident                  |
| `GET`  | `/api/v1/incidents`               | Required       | List user's incidents                     |
| `GET`  | `/api/v1/incidents/{incident_id}` | Required       | Retrieve owned incident                   |

---

# Authentication Flow

## Login

```http
POST /auth/login
Content-Type: application/json
```

Example request:

```json
{
  "username": "security-user",
  "password": "DevSecOps@123"
}
```

Successful response:

```json
{
  "access_token": "<JWT_TOKEN>",
  "refresh_token": "<REFRESH_TOKEN>",
  "token_type": "bearer"
}
```

The access token is supplied to protected endpoints using:

```http
Authorization: Bearer <JWT_TOKEN>
```

> The demonstration credentials are intended only for local and educational testing. Never use them in production.

---

# Example API Requests

## Root Endpoint

```http
GET /
```

Example response:

```json
{
  "message": "Secure REST API is running",
  "status": "ok"
}
```

---

## Health Check

```http
GET /health
```

No authentication is required.

Example response:

```json
{
  "status": "healthy"
}
```

---

## Profile

```http
GET /api/v1/profile
Authorization: Bearer <JWT_TOKEN>
```

Example response:

```json
{
  "username": "security-user",
  "role": "analyst",
  "message": "Authenticated access granted"
}
```

---

## Admin Dashboard

```http
GET /api/v1/admin/dashboard
Authorization: Bearer <ADMIN_JWT_TOKEN>
```

Example successful response:

```json
{
  "message": "Welcome to the admin dashboard",
  "username": "admin-user"
}
```

An authenticated analyst attempting to access this endpoint receives:

```text
403 Forbidden
```

---

# Project Structure

```text
Secure-REST-API-DevSecOps/
│
├── .github/
│   └── workflows/
│       └── security.yml
│
├── migrations/
│   ├── env.py
│   └── versions/
│       └── b57bef6b9c97_add_incidents_table.py
│
├── src/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   │
│   └── security/
│       ├── __init__.py
│       ├── auth.py
│       ├── audit.py
│       ├── incidents.py
│       ├── jwt_config.py
│       ├── middleware.py
│       ├── schemas.py
│       └── users.py
│
├── tests/
│   ├── conftest.py
│   └── test_security.py
│
├── pytest.ini
├── .gitignore
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

---

# DevSecOps Pipeline

The project uses **GitHub Actions** to automatically execute security checks on pushes and pull requests targeting the `main` branch.

Workflow:

```text
Git Push / Pull Request
          │
          ▼
   Checkout Repository
          │
          ▼
      Setup Python
          │
          ▼
 Install Dependencies
          │
     ┌────┴────┐
     ▼         ▼
  pytest   pip-audit
     │         │
     ▼         ▼
Security   Dependency
 Tests        Scan
     │         │
     └────┬────┘
          ▼
      CI Result
```

The workflow is defined in:

```text
.github/workflows/security.yml
```

---

# Testing

Security and functional tests are implemented using **pytest** and FastAPI's `TestClient`.

The test suite validates:

* Public health endpoint
* Public root endpoint
* JWT authentication
* Invalid token rejection
* Protected profile endpoint
* Security headers
* RBAC enforcement
* Admin authorization
* Correct user roles
* Refresh-token rotation
* Refresh-token revocation
* Logout behavior
* Authentication audit logging
* Incident authentication requirements
* Incident creation
* Incident ownership
* Unauthorized incident access prevention
* Authenticated incident listing

Run the complete test suite:

```powershell
python -m pytest -q
```

The latest local test run should be used as the authoritative test count because the suite can change as new security controls are added.

---

# Security Test Coverage

```text
Public /health                 → 200 OK
Missing JWT on /profile        → 401 Unauthorized
Invalid JWT                    → 401 Unauthorized
Valid JWT                      → 200 OK
Expired JWT                    → Authentication rejected
Analyst → Admin endpoint       → 403 Forbidden
Admin → Admin endpoint         → 200 OK
Refresh token rotation         → Verified
Refresh token revocation       → Verified
Logout revocation              → Verified
Security headers               → Verified
Incident ownership             → Verified
```

---

# Dependency Security

The project uses **pip-audit** to identify known vulnerabilities in Python packages.

Run locally:

```powershell
python -m pip_audit
```

Or audit application dependencies:

```powershell
python -m pip_audit -r requirements.txt
```

Dependency audit results can change as vulnerability databases are updated. Always use the latest audit result when reporting the current security status.

Application and development dependencies are maintained separately:

```text
requirements.txt
requirements-dev.txt
```

---

# Environment Configuration

Security-sensitive configuration is loaded through environment variables.

Example local configuration:

```env
JWT_SECRET_KEY=your-local-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

The `.env` file should remain excluded from Git through `.gitignore`.

### Never Commit

* API keys
* Passwords
* JWT secrets
* Access tokens
* Private keys
* Production credentials
* Sensitive configuration

---

# Local Installation

## Requirements

* Python 3.12+
* Git
* Windows, Linux, or macOS

## 1. Clone the Repository

```powershell
git clone https://github.com/Shumii98/Secure-REST-API-DevSecOps.git
cd Secure-REST-API-DevSecOps
```

## 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Install Application Dependencies

```powershell
python -m pip install -r requirements.txt
```

## 4. Install Development Dependencies

```powershell
python -m pip install -r requirements-dev.txt
```

## 5. Configure Environment Variables

Create a local `.env` file with the required development configuration.

Do not commit this file to Git.

## 6. Run the API

```powershell
python -m uvicorn src.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# API Documentation

FastAPI automatically provides interactive OpenAPI documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### OpenAPI Specification

```text
http://127.0.0.1:8000/openapi.json
```

Swagger UI can be used to:

* View API endpoints
* Submit login credentials
* Obtain JWT tokens
* Authorize protected requests
* Test authentication
* Test RBAC behavior
* Test incident-management endpoints
* Inspect API responses

---

# Security Testing Workflow

The development workflow follows a security feedback loop:

```text
1. Modify application code
          │
          ▼
2. Run automated tests
          │
          ▼
3. Run dependency audit
          │
          ▼
4. Review security results
          │
          ▼
5. Commit changes
          │
          ▼
6. Push to GitHub
          │
          ▼
7. GitHub Actions runs Security CI
          │
          ▼
8. Review CI result
```

This provides continuous security feedback throughout development.

---

# Technologies

| Technology     | Purpose                           |
| -------------- | --------------------------------- |
| Python         | Application development           |
| FastAPI        | REST API framework                |
| Uvicorn        | ASGI application server           |
| Pydantic       | Request/data validation           |
| PyJWT          | JWT creation and verification     |
| pwdlib         | Password hashing and verification |
| Argon2         | Password hashing algorithm        |
| SQLAlchemy     | Database ORM                      |
| Alembic        | Database migrations               |
| SQLite         | Local development database        |
| pytest         | Automated security testing        |
| HTTPX          | API testing support               |
| pip-audit      | Dependency vulnerability scanning |
| slowapi        | Rate limiting                     |
| python-dotenv  | Environment configuration         |
| Git            | Version control                   |
| GitHub Actions | CI / DevSecOps automation         |

---

# Screenshots

Recommended project evidence includes:

### Swagger / OpenAPI Documentation

Interactive Swagger UI demonstrates the available API endpoints and authentication workflow.

```text
screenshots/swagger-api.png
```

### Public Health Check

The `/health` endpoint is publicly accessible and returns:

```json
{
  "status": "healthy"
}
```

### Security Tests

Test evidence demonstrates authentication, authorization, security headers, refresh-token controls, and incident-management security.

```text
screenshots/security-tests-passed.png
```

---

# Security Results

The project validates the following security behaviors:

### Authentication

```text
Valid credentials        → JWT issued
Missing JWT              → 401 Unauthorized
Invalid JWT              → 401 Unauthorized
Valid JWT                → 200 OK
```

### Authorization

```text
Analyst → Admin endpoint → 403 Forbidden
Admin   → Admin endpoint → 200 OK
```

### Token Security

```text
Refresh token rotation   → Verified
Old refresh token        → Rejected
Logout revocation        → Verified
```

### Security Headers

```text
X-Content-Type-Options → Verified
X-Frame-Options        → Verified
Referrer-Policy        → Verified
Permissions-Policy     → Verified
```

### Incident Security

```text
Unauthenticated create        → 401
Authenticated create          → 201
Owner retrieves incident      → 200
Unauthorized owner access    → 404
Authenticated incident list   → 200
```

---

# Security Notice

This project is intended for **educational, defensive, and authorized security engineering purposes**.

Do not use this project to access systems, APIs, networks, or data without appropriate authorization.

Never commit:

* API keys
* Passwords
* Access tokens
* Private keys
* Production credentials
* Sensitive configuration

Demonstration credentials are intended only for local educational testing and must not be reused in production.

---

# Future Improvements

Potential future enhancements include:

* Request ID / correlation IDs
* HTTPS/TLS deployment
* Container security scanning
* Static Application Security Testing (SAST)
* Secret scanning
* Dynamic Application Security Testing (DAST)
* Security-focused API monitoring
* Production-ready secret management
* OAuth2 / OpenID Connect integration
* Production-grade identity management
* Centralized security event monitoring
* SIEM integration
* Security alerting and dashboards

---

# Author

**Shumaila**

Cybersecurity / Information Security

GitHub: [@Shumii98](https://github.com/Shumii98)

---

# License

This project is released under the **MIT License** for educational and portfolio purposes.

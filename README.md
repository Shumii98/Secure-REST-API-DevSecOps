# Secure REST API – DevSecOps

[![Security CI](https://github.com/Shumii98/Secure-REST-API-DevSecOps/actions/workflows/security.yml/badge.svg)](https://github.com/Shumii98/Secure-REST-API-DevSecOps/actions/workflows/security.yml)

A security-focused REST API built with **FastAPI** and designed around practical **DevSecOps principles**.

The project demonstrates JWT-based authentication, protected API endpoints, HTTP security headers, automated security testing, dependency vulnerability auditing, environment-based configuration, and continuous security checks through GitHub Actions.

---

## Overview

This project demonstrates how security controls can be integrated into the API development lifecycle rather than being added only after application development.

### Security capabilities

* 🔐 JWT Bearer-token authentication
* 🔒 Protected API endpoints
* 🛡️ HTTP security headers through middleware
* ⏱️ JWT expiration handling
* 🌐 Versioned API endpoint
* 🧪 Automated security testing with `pytest`
* 🔍 Dependency vulnerability scanning with `pip-audit`
* ⚙️ GitHub Actions security CI
* 🔑 Environment-based secret configuration
* 📦 Separate application and development dependencies

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
                         │      FastAPI API     │
                         └──────────┬───────────┘
                                    │
                   ┌────────────────┴────────────────┐
                   │                                 │
                   ▼                                 ▼
          ┌──────────────────┐             ┌──────────────────┐
          │ JWT Authentication│             │ Security Headers │
          │ Bearer Token      │             │ Middleware       │
          └────────┬─────────┘             └────────┬─────────┘
                   │                                 │
                   └───────────────┬─────────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │  Protected API      │
                         │     Endpoints       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    JSON Response     │
                         └──────────────────────┘
```

### DevSecOps CI Pipeline

```text
                    Git Push / Pull Request
                              │
                              ▼
                    ┌───────────────────┐
                    │   GitHub Actions  │
                    │    Security CI    │
                    └─────────┬─────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
              ┌──────────┐       ┌─────────────┐
              │  pytest  │       │  pip-audit  │
              │ 9 tests  │       │ Dependency  │
              └────┬─────┘       │    Scan     │
                   │              └──────┬──────┘
                   │                     │
                   └──────────┬──────────┘
                              ▼
                       ┌─────────────┐
                       │  CI Result  │
                       │    PASS     │
                       └─────────────┘
```

---

## Security Controls

### 1. JWT Authentication

The API uses **JSON Web Tokens (JWT)** with the HS256 signing algorithm.

The authentication flow is:

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
JWT access token generated
        │
        ▼
Authorization: Bearer <token>
        │
        ▼
Protected endpoint
```

JWT tokens contain:

* `sub` — authenticated username
* `exp` — token expiration timestamp

Protected endpoints reject requests without valid authentication.

The application returns:

```text
401 Unauthorized
```

when authentication is missing or invalid.

---

### 2. Protected Endpoints

The following endpoints require a valid Bearer token:

```text
GET /health
GET /api/v1/profile
```

Authentication is implemented using FastAPI dependencies and JWT verification.

---

### 3. Security Headers

Security-related HTTP response headers are applied through custom middleware.

Current headers include:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Permissions-Policy: geolocation=(),microphone=(),camera=()
```

These controls help reduce common browser-side security risks such as MIME sniffing, clickjacking, unnecessary referrer exposure, and unwanted browser feature access.

---

### 4. API Versioning

The profile endpoint is exposed under a versioned API path:

```text
/api/v1/
```

Example:

```text
GET /api/v1/profile
```

This provides a foundation for maintaining API compatibility as the application evolves.

---

## API Endpoints

| Method | Endpoint          | Authentication | Purpose                         |
| ------ | ----------------- | -------------- | ------------------------------- |
| `GET`  | `/`               | Public         | API status                      |
| `POST` | `/auth/login`     | Public         | Authenticate user and issue JWT |
| `GET`  | `/health`         | Required       | Protected health check          |
| `GET`  | `/api/v1/profile` | Required       | Retrieve authenticated profile  |

---

### Login

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
  "token_type": "bearer"
}
```

> The demo credentials are intended only for local/educational use. Never use them in production.

---

### Root Endpoint

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

### Health Check

```http
GET /health
Authorization: Bearer <JWT_TOKEN>
```

Example response:

```json
{
  "status": "healthy"
}
```

Requests without authentication are rejected with:

```json
{
  "detail": "Not authenticated"
}
```

---

### Profile

```http
GET /api/v1/profile
Authorization: Bearer <JWT_TOKEN>
```

Example authenticated response:

```json
{
  "username": "security-user",
  "role": "analyst",
  "message": "Authenticated access granted"
}
```

Invalid or forged tokens are rejected with:

```json
{
  "detail": "Invalid or expired authentication token"
}
```

---

## Project Structure

```text
Secure-REST-API-DevSecOps/
│
├── .github/
│   └── workflows/
│       └── security.yml
│
├── src/
│   ├── main.py
│   │
│   └── security/
│       ├── __init__.py
│       ├── auth.py
│       ├── middleware.py
│       ├── schemas.py
│       ├── users.py
│       └── jwt_config.py
│
├── tests/
│   └── test_security.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

---

## DevSecOps Pipeline

The project uses **GitHub Actions** to automatically execute security checks on pushes and pull requests targeting the `main` branch.

### Pipeline workflow

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
          ├─────────────────┐
          ▼                 ▼
       pytest           pip-audit
          │                 │
          ▼                 ▼
   Security Tests     Dependency Scan
          │                 │
          └────────┬────────┘
                   ▼
             CI Result
```

### Automated checks

The CI pipeline performs:

1. Python environment setup
2. Dependency installation
3. Full pytest test-suite execution
4. Dependency vulnerability auditing

The workflow is defined in:

```text
.github/workflows/security.yml
```

---

## Testing

Security tests are implemented using **pytest** and FastAPI's `TestClient`.

The current test suite validates:

* Authentication required for `/health`
* Invalid token rejection
* Valid token acceptance
* Security header validation
* Authentication required for `/api/v1/profile`
* Valid profile authentication
* Invalid profile authentication
* Public root endpoint
* Security headers on protected endpoints

Run the complete test suite locally:

```powershell
python -m pytest -v
```

Current result:

```text
9 passed
```

### Security test coverage

```text
Valid JWT                  → 200 OK
Missing JWT                → 401 Unauthorized
Invalid JWT                → 401 Unauthorized
Protected endpoint access  → Verified
Security headers           → Verified
```

---

## Dependency Security

The project uses **pip-audit** to identify known vulnerabilities in Python packages.

Run the audit locally:

```powershell
python -m pip_audit
```

The CI workflow also performs dependency auditing automatically.

The project separates:

```text
requirements.txt
requirements-dev.txt
```

to distinguish application dependencies from development and security-testing tools.

---

## Environment Configuration

Security-sensitive configuration is loaded through environment variables.

Example local configuration:

```env
API_TOKEN=your-development-token
JWT_SECRET_KEY=your-local-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

The `.env` file should remain excluded from Git through `.gitignore`.

### Never commit:

* API keys
* Passwords
* JWT secrets
* Access tokens
* Private keys
* Production credentials
* Sensitive configuration

For CI, dedicated test-only environment values are configured in the GitHub Actions workflow.

---

## Local Installation

### Requirements

* Python 3.12+
* Git
* Windows, Linux, or macOS

### 1. Clone the repository

```powershell
git clone https://github.com/Shumii98/Secure-REST-API-DevSecOps.git

cd Secure-REST-API-DevSecOps
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install application dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Install development dependencies

```powershell
python -m pip install -r requirements-dev.txt
```

### 5. Configure environment variables

Create a local `.env` file and configure the required development values.

### 6. Run the API

```powershell
python -m uvicorn src.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

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
* Obtain a JWT
* Authorize requests with a Bearer token
* Test protected endpoints
* Inspect API responses

---

## Security Testing Workflow

The development workflow follows a basic security feedback loop:

```text
1. Modify application code
          │
          ▼
2. Run automated security tests
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

## Technologies

| Technology     | Purpose                           |
| -------------- | --------------------------------- |
| Python         | Application development           |
| FastAPI        | REST API framework                |
| Uvicorn        | ASGI application server           |
| Pydantic       | Request/data validation           |
| PyJWT          | JWT creation and verification     |
| pwdlib         | Password hashing and verification |
| pytest         | Automated security testing        |
| HTTPX          | API testing support               |
| pip-audit      | Dependency vulnerability scanning |
| python-dotenv  | Environment configuration         |
| Git            | Version control                   |
| GitHub Actions | CI / DevSecOps automation         |

---

## Screenshots

### Swagger / OpenAPI Documentation

The interactive Swagger UI provides an interface for viewing and testing the API endpoints.

![Swagger API Documentation](screenshots/swagger-api.png)

### Authenticated Health Check

The protected `/health` endpoint returns a successful response when a valid Bearer token is provided.

![Authenticated Health Check](screenshots/authenticated-health.png)

### Automated Security Tests

The security test suite validates authentication, protected endpoints, and security headers.

![Security Tests Passed](screenshots/security-tests-passed.png)

---

## Security Testing Results

### Automated Tests

```text
9 passed
```

### Authentication Testing

```text
Valid credentials       → JWT issued
Missing JWT             → 401 Unauthorized
Invalid JWT             → 401 Unauthorized
Valid JWT               → 200 OK
```

### CI Status

```text
Security CI: PASSING
```

The repository's GitHub Actions workflow automatically executes the security test suite and dependency audit.

---

## Security Notice

This project is intended for **educational, defensive, and authorized security engineering purposes**.

Do not use this project to access systems, APIs, networks, or data without appropriate authorization.

Never commit:

* API keys
* Passwords
* Access tokens
* Private keys
* Production credentials
* Sensitive configuration

The demo credentials included in the source code are for local educational testing only and must not be reused in production.

---

## Future Improvements

Potential future enhancements include:

* Role-based access control (RBAC)
* Rate limiting
* Structured security logging
* Request ID / correlation IDs
* HTTPS/TLS deployment
* Container security scanning
* Static Application Security Testing (SAST)
* Secret scanning
* Dynamic Application Security Testing (DAST)
* Security-focused API monitoring
* Production-ready secret management
* Database-backed user management

---

## Author

**Shumaila**

Cybersecurity / Information Security

GitHub: [@Shumii98](https://github.com/Shumii98)

---

## License

This project is released under the MIT License for educational and portfolio purposes.

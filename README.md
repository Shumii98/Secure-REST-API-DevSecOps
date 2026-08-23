# Secure REST API – DevSecOps

[![Security CI](https://github.com/Shumii98/Secure-REST-API-DevSecOps/actions/workflows/security.yml/badge.svg)](https://github.com/Shumii98/Secure-REST-API-DevSecOps/actions/workflows/security.yml)

A security-focused REST API built with **FastAPI** and designed around practical **DevSecOps principles**. The project implements bearer-token authentication, security headers, automated security testing, dependency vulnerability scanning, and a GitHub Actions CI pipeline.

---

## Overview

This project demonstrates how security controls can be integrated directly into the API development lifecycle.

The application includes:

- 🔐 Bearer-token authentication
- 🛡️ HTTP security headers
- 🔒 Protected API endpoints
- 🌐 API versioning
- 🧪 Automated security testing with `pytest`
- 🔍 Dependency vulnerability scanning with `pip-audit`
- ⚙️ GitHub Actions security CI
- 🔑 Environment-based secret configuration
- 📦 Pinned application dependencies

The goal is to demonstrate a practical **Secure SDLC / DevSecOps workflow**, rather than simply building a REST API.

---

## Security Architecture

```text
                         ┌──────────────────────┐
                         │      API Client      │
                         └──────────┬───────────┘
                                    │
                                    │ HTTP Request
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
          ┌──────────────────┐           ┌──────────────────┐
          │ Authentication   │           │ Security Headers │
          │ Bearer Token     │           │ Middleware       │
          └────────┬─────────┘           └────────┬─────────┘
                   │                              │
                   ▼                              │
          ┌──────────────────┐                    │
          │ Protected API    │◄───────────────────┘
          │ Endpoints        │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ JSON Response    │
          └──────────────────┘


                    DevSecOps Pipeline
                    ==================

          ┌───────────────┐
          │ Git Push / PR │
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────────┐
          │ GitHub Actions    │
          │ Security CI       │
          └─────────┬─────────┘
                    │
             ┌──────┴───────┐
             │              │
             ▼              ▼
        ┌──────────┐   ┌─────────────┐
        │ pytest   │   │ pip-audit   │
        │ 9 tests  │   │ Dependency  │
        └────┬─────┘   │ scanning    │
             │         └──────┬──────┘
             │                │
             └────────┬───────┘
                      ▼
                ┌───────────┐
                │ CI Result │
                │   GREEN   │
                └───────────┘
```

---

## Security Controls

### 1. Authentication

Protected endpoints require a Bearer token.

Example:

```http
Authorization: Bearer <API_TOKEN>
```

The token is loaded from an environment variable rather than being hard-coded into the application.

The authentication layer rejects:

- Missing authentication
- Invalid tokens

Valid authentication allows access to protected endpoints.

---

### 2. Security Headers

The application applies security-related HTTP response headers through middleware.

Current headers include:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

These controls help reduce common browser-side security risks such as MIME sniffing, clickjacking, unnecessary referrer exposure, and unwanted browser feature access.

---

### 3. API Versioning

Protected API functionality is exposed under a versioned path:

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

| Method | Endpoint | Authentication | Purpose |
|--------|----------|----------------|---------|
| GET | `/` | Public | API status |
| GET | `/health` | Required | Health check |
| GET | `/api/v1/profile` | Required | Retrieve authenticated profile |

### Example: Root Endpoint

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

### Example: Health Check

```http
GET /health
Authorization: Bearer <API_TOKEN>
```

Example response:

```json
{
  "status": "healthy"
}
```

### Example: Profile

```http
GET /api/v1/profile
Authorization: Bearer <API_TOKEN>
```

Example response:

```json
{
  "username": "security-user",
  "role": "analyst"
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
│       └── middleware.py
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

The project uses GitHub Actions to automatically perform security checks on pushes and pull requests targeting the `main` branch.

### Pipeline

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
          ├───────────────┐
          ▼               ▼
       pytest         pip-audit
          │               │
          ▼               ▼
    Security Tests    Dependency Scan
          │               │
          └───────┬───────┘
                  ▼
             CI Result
```

### Automated Checks

The CI pipeline performs:

```text
1. Python environment setup
2. Dependency installation
3. Security test execution
4. Dependency vulnerability audit
```

The current pipeline successfully passes:

```text
9 security tests
0 known dependency vulnerabilities
```

---

## Testing

Security tests are implemented using `pytest` and FastAPI's `TestClient`.

Current test coverage includes:

- Authentication required for `/health`
- Invalid token rejection
- Valid token acceptance
- Security header validation
- Authentication required for `/api/v1/profile`
- Valid profile authentication
- Invalid profile authentication
- Public root endpoint
- Security headers on protected endpoints

Run the tests locally:

```powershell
python -m pytest tests\test_security.py -v
```

Expected result:

```text
9 passed
```

---

## Dependency Security

The project uses `pip-audit` to identify known vulnerabilities in Python dependencies.

Run locally:

```powershell
python -m pip_audit -r requirements.txt
```

Current result:

```text
No known vulnerabilities found
```

Dependencies are explicitly version-pinned in:

```text
requirements.txt
```

Development dependencies are maintained separately in:

```text
requirements-dev.txt
```

---

## Environment Configuration

Secrets are loaded from environment variables.

Create a local `.env` file:

```env
API_TOKEN=your-development-token
```

The `.env` file is intentionally excluded from Git through `.gitignore`.

Never commit real credentials, API keys, passwords, or production secrets to the repository.

---

## Local Installation

### Requirements

- Python 3.12+
- Git
- Windows, Linux, or macOS

### 1. Clone the repository

```powershell
git clone https://github.com/Shumii98/Secure-REST-API-DevSecOps.git
cd Secure-REST-API-DevSecOps
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

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

### 5. Configure the API token

Create:

```text
.env
```

Add:

```env
API_TOKEN=dev-secret-token
```

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

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```

---

## Security Testing Workflow

A typical development workflow is:

```text
1. Modify application code
          │
          ▼
2. Run security tests
          │
          ▼
3. Run dependency audit
          │
          ▼
4. Review results
          │
          ▼
5. Commit changes
          │
          ▼
6. Push to GitHub
          │
          ▼
7. GitHub Actions automatically runs security CI
```

This provides an automated security feedback loop during development.

---

## Technologies

| Technology | Purpose |
|------------|---------|
| Python | Application development |
| FastAPI | REST API framework |
| Uvicorn | ASGI application server |
| Pydantic | Data validation |
| pytest | Automated testing |
| HTTPX | API testing support |
| pip-audit | Dependency vulnerability scanning |
| python-dotenv | Environment configuration |
| Git | Version control |
| GitHub Actions | CI / DevSecOps automation |

---
## Screenshots

### Swagger / OpenAPI Documentation

The interactive Swagger UI exposes the available API endpoints and provides an interface for testing the REST API.

![Swagger API Documentation](screenshots/swagger-api.png)

### Authenticated Health Check

The protected `/health` endpoint returns a successful response when a valid Bearer token is provided.

![Authenticated Health Check](screenshots/authenticated-health.png)

### Automated Security Tests

The security test suite validates authentication, authorization behavior, security headers, and protected endpoints.

![Security Tests Passed](screenshots/security-tests-passed.png)
## Security Testing Results

### Local Testing

```text
9 passed
```

### Dependency Audit

```text
No known vulnerabilities found
```

### GitHub Actions

```text
Security CI: PASSING
```

---

## Security Notice

This project is intended for **educational, defensive, and authorized security engineering purposes**.

Do not use this project to access systems, APIs, networks, or data without appropriate authorization.

Never commit:

- API keys
- Passwords
- Access tokens
- Private keys
- Production credentials
- Sensitive configuration

---

## Future Improvements

Potential future enhancements include:

- JWT-based authentication
- Role-based access control (RBAC)
- Rate limiting
- Structured security logging
- Request ID / correlation IDs
- Input validation improvements
- HTTPS/TLS deployment
- Container security scanning
- Static application security testing (SAST)
- Secret scanning
- DAST integration
- Security-focused API monitoring

---

## Author

**Shumaila**

Cybersecurity / Information Security

GitHub: [@Shumii98](https://github.com/Shumii98)

---

## License

This project is intended as a cybersecurity portfolio and educational project.
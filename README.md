# Secure REST API DevSecOps

A security-focused REST API built with **FastAPI** and designed around practical application security, authentication, authorization, auditability, security monitoring, and DevSecOps automation.

The project demonstrates how a modern security-aware API can integrate preventive controls, detection capabilities, security logging, incident management, automated testing, and CI security gates into a single application.

## Project Overview

This project implements a secure REST API with:

* JWT-based authentication
* Access and refresh token architecture
* Refresh token rotation and revocation
* Role-Based Access Control (RBAC)
* Secure password hashing with Argon2
* SQLAlchemy database integration
* Alembic database migrations
* Security audit logging
* Request ID / correlation tracking
* Structured JSON security logging
* Login rate limiting
* HTTP security headers
* Incident management
* Object-level authorization protection
* SIEM-style security event monitoring
* Automated security alert generation
* Machine-readable security reports
* SOC-style monitoring dashboard
* Automated security testing
* Static security analysis
* Dependency vulnerability auditing
* Secret scanning
* GitHub Actions security CI pipeline

---

## Security Architecture

```text
                        Client
                          |
                          v
                +---------------------+
                |    FastAPI API      |
                +---------------------+
                          |
             +------------+------------+
             |                         |
             v                         v
      Request ID Middleware     Security Headers
             |                         |
             +------------+------------+
                          |
                          v
                +---------------------+
                | Authentication      |
                | JWT / RBAC           |
                +---------------------+
                          |
             +------------+------------+
             |                         |
             v                         v
       API Resources            Incident Management
             |                         |
             +------------+------------+
                          |
                          v
                +---------------------+
                | Audit Logging        |
                | Structured JSON Logs |
                +---------------------+
                          |
                          v
                +---------------------+
                | Security Monitoring  |
                +---------------------+
                          |
             +------------+------------+
             |                         |
             v                         v
       Alert Engine             Security Report
             |                         |
             +------------+------------+
                          |
                          v
                +---------------------+
                | SOC Dashboard        |
                | Streamlit            |
                +---------------------+
```

---

## Security Controls

### Authentication

The API uses JWT-based authentication with separate access and refresh tokens.

Security features include:

* Signed JWT access tokens
* Refresh tokens
* Token expiration
* Token type validation
* JWT ID (`jti`)
* Issuer validation
* Audience validation
* Issued-at (`iat`) claims
* Refresh token rotation
* Refresh token revocation

### Authorization

Role-Based Access Control is implemented for protected resources.

Supported roles include:

* `analyst`
* `admin`

Administrative endpoints require the appropriate role.

### Password Security

Passwords are never stored in plaintext.

The project uses:

* `pwdlib`
* Argon2 password hashing
* Password verification before authentication
* Secure password storage practices

### Rate Limiting

Authentication endpoints use request rate limiting through SlowAPI.

Example control:

```text
/auth/login
5 requests per minute
```

This helps reduce automated authentication attacks such as repeated password guessing.

### Security Headers

The application applies security-related HTTP headers through custom middleware.

Implemented controls include:

* `X-Frame-Options`
* `X-Content-Type-Options`
* `Referrer-Policy`
* `Permissions-Policy`
* Content Security Policy
* HTTP Strict Transport Security

### Request Correlation

Every API request receives a unique request ID.

Clients can also provide their own:

```text
X-Request-ID
```

The same identifier can be correlated across:

```text
API Request
     |
     +--> Structured Security Log
     |
     +--> Audit Record
     |
     +--> Security Monitoring
     |
     +--> SOC Alert
```

This provides an investigation-friendly trail for security events.

---

# Incident Management

The API includes security incident management capabilities.

Authenticated users can create and retrieve incidents while object-level authorization prevents users from accessing incidents belonging to other users.

This provides protection against insecure direct object reference / broken object-level authorization scenarios.

Example API resources:

```text
/api/v1/incidents
/api/v1/incidents/{incident_id}
```

Security principles demonstrated:

* Authentication before access
* User ownership validation
* Object-level authorization
* Controlled incident retrieval
* Security-focused API design

---

# SIEM-Style Security Monitoring

The project includes a lightweight security monitoring pipeline that processes structured application security logs.

```text
security.log
     |
     v
Log Parser
     |
     v
Security Events
     |
     v
Alert Engine
     |
     +---- Authentication Failure Burst
     |
     +---- Targeted Account Failure
     |
     v
Security Alerts
     |
     v
JSON Security Report
     |
     v
SOC Dashboard
```

## Detection Rules

### Authentication Failure Burst

Detects repeated failed authentication attempts originating from the same IP address.

Default threshold:

```text
5 failed authentication attempts
```

Generated alert:

```text
AUTHENTICATION_FAILURE_BURST
Severity: HIGH
```

### Targeted Account Failure

Detects repeated authentication failures associated with the same username.

Default threshold:

```text
3 failed authentication events
```

Generated alert:

```text
TARGETED_ACCOUNT_FAILURE
Severity: MEDIUM
```

Alerts include SOC-oriented metadata such as:

* Alert ID
* Alert type
* Detection rule
* Severity
* Detection timestamp
* Source IP
* Target account
* Event count
* Correlated request IDs
* Description

---

# SOC Security Dashboard

The project includes a Streamlit-based SOC monitoring dashboard.

The dashboard provides visibility into:

* Total security events
* Total alerts
* High-severity alerts
* Medium-severity alerts
* Low-severity alerts
* Security alert details
* Detection rules
* Target accounts
* Source IP addresses
* Correlated request IDs
* Latest monitoring report

Example dashboard workflow:

```text
Application Logs
       |
       v
Security Monitoring
       |
       v
Detection Rules
       |
       v
Security Report
       |
       v
SOC Dashboard
```

Run the dashboard with:

```powershell
streamlit run .\src\dashboard\app.py
```

The dashboard is available locally at:

```text
http://localhost:8501
```

---

# Security Monitoring Report

The monitoring engine generates a machine-readable JSON report:

```text
reports/security_report.json
```

Example structure:

```json
{
  "generated_at": "2026-09-19T11:24:08+00:00",
  "summary": {
    "total_events": 355,
    "total_alerts": 1,
    "alerts_by_severity": {
      "MEDIUM": 1
    }
  },
  "alerts": [
    {
      "alert_id": "ALT-XXXXXXXXXXXX",
      "alert_type": "TARGETED_ACCOUNT_FAILURE",
      "rule": "targeted_account_failure",
      "severity": "MEDIUM",
      "event_count": 3
    }
  ]
}
```

Runtime security reports and logs are excluded from version control.

---

# DevSecOps Pipeline

Security checks are integrated into GitHub Actions.

The CI pipeline performs automated:

```text
Code
 |
 +--> Ruff
 |
 +--> Bandit
 |
 +--> Pytest
 |
 +--> Coverage
 |
 +--> pip-audit
 |
 +--> Gitleaks
 |
 v
Security CI
```

## CI Security Gates

The project enforces:

* Automated unit/integration testing
* Minimum **85% test coverage**
* Ruff code quality checks
* Bandit security analysis
* Dependency vulnerability auditing with pip-audit
* Secret detection with Gitleaks

Current project validation:

```text
Tests:       34 passed
Coverage:    88.74%
CI Status:   Passing
```

The Streamlit dashboard is intentionally excluded from the backend coverage calculation because it is a UI layer rather than API/security logic.

---

# Testing

The project uses `pytest` for automated testing.

The test suite covers areas including:

* Public endpoint behavior
* Authentication
* Invalid tokens
* Access tokens
* Refresh tokens
* Refresh token rotation
* Logout and token revocation
* RBAC
* Security headers
* Audit logging
* Incident creation
* Incident ownership
* Object-level authorization
* Request ID correlation
* Failed login detection
* Targeted account detection
* Security log parsing
* Security report generation

Run all tests:

```powershell
python -m pytest -v
```

Run with coverage:

```powershell
python -m pytest -v --cov=src --cov-report=term-missing --cov-fail-under=85
```

Current result:

```text
34 passed
88.74% coverage
```

---

# Technology Stack

| Technology     | Purpose                           |
| -------------- | --------------------------------- |
| Python 3.12    | Application language              |
| FastAPI        | REST API framework                |
| Uvicorn        | ASGI server                       |
| PyJWT          | JWT authentication                |
| pwdlib         | Password hashing                  |
| Argon2         | Password hashing algorithm        |
| SQLAlchemy     | Database ORM                      |
| Alembic        | Database migrations               |
| SlowAPI        | API rate limiting                 |
| Streamlit      | SOC dashboard                     |
| Pytest         | Automated testing                 |
| Ruff           | Code quality                      |
| Bandit         | Python security analysis          |
| pip-audit      | Dependency vulnerability scanning |
| Gitleaks       | Secret detection                  |
| GitHub Actions | CI/CD security automation         |

---

# Project Structure

```text
Secure-REST-API-DevSecOps/
│
├── .github/
│   └── workflows/
│       └── security-ci.yml
│
├── src/
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── app.py
│   │
│   ├── security/
│   │   ├── __init__.py
│   │   ├── audit.py
│   │   ├── auth.py
│   │   ├── incidents.py
│   │   ├── jwt_config.py
│   │   ├── middleware.py
│   │   ├── request_id.py
│   │   ├── schemas.py
│   │   └── users.py
│   │
│   ├── security_monitoring/
│   │   ├── __init__.py
│   │   ├── alert_engine.py
│   │   ├── log_parser.py
│   │   ├── monitor.py
│   │   └── report_generator.py
│   │
│   ├── database.py
│   ├── dependencies.py
│   ├── logging_config.py
│   ├── main.py
│   └── models.py
│
├── tests/
│   ├── test_security.py
│   └── test_security_monitoring.py
│
├── migrations/
│   └── versions/
│
├── reports/
│   └── security_report.json
│
├── logs/
│   └── security.log
│
├── .coveragerc
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

# Installation

Clone the repository:

```powershell
git clone https://github.com/Shumii98/Secure-REST-API-DevSecOps.git
```

Move into the project:

```powershell
cd Secure-REST-API-DevSecOps
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

---

# Running the API

Start the FastAPI application:

```powershell
uvicorn src.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Running Security Monitoring

Generate a security monitoring report:

```powershell
python -m src.security_monitoring.monitor
```

Expected workflow:

```text
Security log
     |
     v
Log parser
     |
     v
Alert engine
     |
     v
Security report
```

Output:

```text
reports/security_report.json
```

---

# Running the SOC Dashboard

After generating the monitoring report:

```powershell
streamlit run .\src\dashboard\app.py
```

Open:

```text
http://localhost:8501
```

---

# Example Security Investigation

A failed authentication event can be traced through the monitoring pipeline:

```text
1. Authentication failure
          |
          v
2. Structured JSON security log
          |
          v
3. Request ID assigned
          |
          v
4. Audit record created
          |
          v
5. Monitoring engine analyzes event
          |
          v
6. Detection threshold reached
          |
          v
7. SOC alert generated
          |
          v
8. Alert displayed in dashboard
```

This demonstrates the relationship between **prevention, logging, detection, and investigation** in an application security environment.

---

# Security Engineering Concepts Demonstrated

This project demonstrates practical knowledge of:

* Secure API development
* Authentication
* Authorization
* RBAC
* JWT security
* Token lifecycle management
* Password security
* Rate limiting
* Security headers
* Audit logging
* Structured logging
* Correlation IDs
* Incident management
* Object-level authorization
* Security monitoring
* Detection engineering
* Alert generation
* SOC workflows
* Security automation
* DevSecOps
* CI security gates
* Dependency management
* Vulnerability scanning
* Secret detection
* Automated security testing

---

# Portfolio Relevance

This project was designed to demonstrate security engineering and SOC-oriented capabilities beyond a basic CRUD API.

It combines:

```text
Secure Development
        +
Application Security
        +
Detection Engineering
        +
Security Monitoring
        +
Incident Management
        +
DevSecOps Automation
```

The result is a practical security-focused application that demonstrates both **preventive security controls** and **security operations capabilities**.

---

# Author

**Shumaila**

M.S. Information Security

Cybersecurity | SOC | Application Security | DevSecOps

GitHub:

https://github.com/Shumii98

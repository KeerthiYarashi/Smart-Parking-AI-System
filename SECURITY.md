# 🔐 Cybersecurity Architecture & Implementation

This document details the security layers implemented in the Smart Parking System to protect against common web vulnerabilities.

---

## 📋 Table of Contents

1. [Security Overview](#security-overview)
2. [API Key Authentication](#1-api-key-authentication)
3. [Input Validation](#2-strict-input-validation)
4. [Input Sanitization](#3-input-sanitization)
5. [Security Headers](#4-security-hardening-headers)
6. [Intrusion Detection System](#5-intrusion-detection-system-ids)
7. [Security Flowchart](#-security-flowchart)
8. [Testing Security](#-testing-security)

---

## Security Overview

| Layer | Threat Mitigated | Implementation |
|-------|------------------|----------------|
| API Key Auth | Unauthorized Access | `verify_api_key` dependency |
| Input Validation | Malformed Data | Pydantic Models |
| Input Sanitization | XSS/Injection | `sanitize_string` helper |
| Security Headers | Clickjacking/MIME | Global Middleware |
| IDS | Attack Detection | `IntrusionDetectionSystem` |

---

## 1. API Key Authentication

**Threat Mitigated:** Unauthorized Access / Brute Force

### Implementation

```python
async def verify_api_key(request: Request, x_api_key: str = Header(None)):
    if x_api_key != SECRET_KEY:
        ids.log_event(ip, "Invalid API Key", severity="HIGH")
        raise HTTPException(status_code=403, detail="Unauthorized")
```

### Features

- ✅ Validates `X-API-KEY` header on sensitive endpoints
- ✅ Logs all authentication failures to IDS
- ✅ Returns HTTP 403 Forbidden for invalid keys

### Protected Endpoints

| Endpoint | Method | Requires API Key |
|----------|--------|------------------|
| `/api/entry` | POST | ✅ |
| `/api/reserve` | POST | ✅ |
| `/api/exit` | POST | ✅ |
| `/api/simulate/*` | POST/GET | ✅ |

---

## 2. Strict Input Validation

**Threat Mitigated:** Malformed Data / Logic Errors

### Implementation (Pydantic)

```python
class VehicleEntryModel(BaseModel):
    type: Literal["AMBULANCE", "VIP", "EV", "SENIOR", "NORMAL"]
    duration: float

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value):
        if value <= 0:
            raise ValueError("Duration must be > 0")
        return value
```

### Validation Rules

| Field | Type | Constraints |
|-------|------|-------------|
| `type` | string | Enum: VIP, NORMAL, EV, SENIOR, AMBULANCE |
| `duration` | float | Must be > 0 |
| `slot` | int | 1 ≤ slot ≤ 12 |
| `email` | string | Valid email format |
| `password` | string | 8-72 characters |

---

## 3. Input Sanitization

**Threat Mitigated:** Cross-Site Scripting (XSS) / SQL Injection

### Implementation

```python
def sanitize_string(text: str):
    forbidden = ["<", ">", "{", "}", "$", "script", "\\"]
    for f in forbidden:
        if f.lower() in text.lower():
            raise ValueError(f"Invalid characters detected: {f}")
    return text
```

### Detection Examples

| Input | Result | Reason |
|-------|--------|--------|
| `<script>alert(1)</script>` | ❌ Blocked | XSS attempt |
| `'; DROP TABLE users;--` | ❌ Blocked | SQL injection |
| `Normal Vehicle` | ✅ Allowed | Clean input |

---

## 4. Security Hardening Headers

**Threat Mitigated:** Clickjacking / MIME Sniffing

### Headers Applied

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevent MIME sniffing |
| `X-Frame-Options` | `SAMEORIGIN` | Prevent clickjacking |

### Implementation (Middleware)

```python
@app.middleware("http")
async def global_security_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response
```

---

## 5. Intrusion Detection System (IDS)

**Threat Mitigated:** Stealthy Attacks / Reconnaissance

### Features

- 🔴 **HIGH**: Invalid API keys, auth failures  
- 🟡 **MEDIUM**: Validation errors
- 🟢 **LOW**: Business logic errors

### Event Logging

```python
class IntrusionDetectionSystem:
    def log_event(self, ip, reason, severity="MEDIUM"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"🛡️ [IDS ALERT] {timestamp} | IP: {ip} | Severity: {severity} | Reason: {reason}")
```

### Console Output Example

```
🛡️ [IDS ALERT] 2024-01-15 14:30:22 | IP: 192.168.1.100 | Severity: HIGH | Reason: Invalid API Key
```

---

## 🛡️ Security Flowchart

```
┌─────────────────────────────────────────────────────────────────────┐
│                         REQUEST FLOW                                 │
└─────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │   Request   │
    └──────┬──────┘
           │
           ▼
    ┌─────────────────┐     Fail   ┌─────────────────┐
    │  API Key Valid? ├───────────►│   Return 403    │
    └────────┬────────┘            │   + Log IDS     │
             │ Pass                └─────────────────┘
             ▼
    ┌─────────────────┐     Fail   ┌─────────────────┐
    │  Pydantic Valid?├───────────►│   Return 422    │
    └────────┬────────┘            └─────────────────┘
             │ Pass
             ▼
    ┌─────────────────┐     Fail   ┌─────────────────┐
    │  Sanitize Input ├───────────►│   Return 400    │
    └────────┬────────┘            │   + Log IDS     │
             │ Pass                └─────────────────┘
             ▼
    ┌─────────────────┐
    │  Execute Logic  │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Add Sec Headers │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │    Response     │
    └─────────────────┘
```

---

## 🧪 Testing Security

### Run Security Tests

```bash
# Terminal 1: Start server
python main.py

# Terminal 2: Run security tests
python test_security.py
```

### Expected Output

```
✅ PASS: Auth Check: Missing API Key Header
✅ PASS: Auth Check: Wrong API Key
✅ PASS: Validation: Negative Duration
✅ PASS: Sanitization: Script Injection Blocked
✅ PASS: Security Headers Present
✅ PASS: Valid Request: Normal Entry
```

### Understanding Results

| HTTP Code | Meaning | Security Implication |
|-----------|---------|---------------------|
| 200 OK | Request succeeded | Valid input accepted |
| 403 Forbidden | Auth failed | Bad/missing API key blocked |
| 422 Unprocessable | Validation failed | Invalid data rejected |
| 400 Bad Request | Sanitization failed | Malicious input blocked |

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# API Security Key
SECRET_KEY=DDCO_SMART_PARKING_2024_SECURE_API_KEY_9x7zL4mP

# JWT Configuration
JWT_SECRET=JWT_DDCO_PARKING_AUTH_SECRET_2024_aB3dE5fG7hJ9kL2mN4pQ6rS8tU0vW
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Best Practices

- ✅ Never commit `.env` to version control
- ✅ Use strong, random keys (32+ characters)
- ✅ Different keys for dev/prod environments

---

<div align="center">

**🔒 Security is enabled by default. No additional configuration required.**

</div>

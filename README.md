# 🚗 Smart Parking AI System - DDCO Project

An intelligent parking management system demonstrating Digital Design and Computer Organization (DDCO) concepts through a real-world application.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [DDCO Concepts Implemented](#-ddco-concepts-implemented)
- [Security Features](#-security-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Testing Security](#-testing-security)
- [Project Structure](#-project-structure)
- [Screenshots](#-screenshots)

---

## ✨ Features

### Core Features
- 🅿️ **Smart Slot Allocation** - Intelligent parking slot assignment based on vehicle type
- 🤖 **Robot Simulation** - FSM-based automated parking with 3 robots
- 🔮 **AI Prediction** - Real-time availability forecasting
- 💳 **Upfront Billing** - Pay-before-park with ALU-based calculations
- 📊 **Real-time Dashboard** - Live status updates and statistics
- 🔔 **Live Notifications** - Instant alerts for booking events

### Vehicle Priority System
| Priority | Vehicle Type | Rate/Hour |
|----------|-------------|-----------|
| 0 (Highest) | 🚑 Ambulance | Free |
| 1 | 👑 VIP | $20 |
| 2 | ⚡ EV | $15 |
| 3 | 👴 Senior | $5 |
| 4 | 🚗 Normal | $10 |

### User Features
- 🔐 **User Authentication** - JWT-based login/register
- 📱 **Personal Dashboard** - Track bookings, history, and notifications
- ⏱️ **Booking Extension** - Extend parking time with additional payment
- 📜 **Activity Logging** - Complete audit trail of user actions

---

## 🔧 DDCO Concepts Implemented

| Concept | Implementation | File |
|---------|---------------|------|
| **ALU (Arithmetic Logic Unit)** | Billing calculations | `controller.py` |
| **FSM (Finite State Machine)** | Robot states: IDLE → MOVING → PARKING → RETURNING | `controller.py` |
| **Priority Encoder** | Vehicle type to priority mapping | `controller.py` |
| **Register File** | Parking slot memory (12 registers) | `controller.py` |
| **FIFO Queue** | Vehicle waiting queue (Shift Register) | `controller.py` |
| **Multiplexer (MUX)** | Best slot selection logic | `controller.py` |
| **Cache Line Locking** | Slot reservation mechanism | `controller.py` |
| **Bus Arbitration** | Priority-based queue sorting | `controller.py` |
| **Interrupt Handler** | Emergency vehicle override | `controller.py` |

---

## 🔐 Security Features

### 6-Layer Security Architecture

| Layer | Threat Mitigated | Implementation |
|-------|------------------|----------------|
| 1. API Key Auth | Unauthorized Access | `verify_api_key` middleware |
| 2. Input Validation | Malformed Data | Pydantic Models |
| 3. Input Sanitization | XSS/SQL Injection | `sanitize_string` helper |
| 4. Security Headers | Clickjacking/MIME | Global Middleware |
| 5. IDS Logging | Attack Detection | `IntrusionDetectionSystem` |
| 6. JWT Auth | Session Security | Token-based user auth |

### Security Headers Applied
```
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-Process-Time: <timing>
```

### Protected Endpoints
All `/api/*` endpoints require `X-API-KEY` header for authentication.

📖 **Full security documentation:** See [SECURITY.md](SECURITY.md)

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/smart-parking-ai.git
cd smart-parking-ai

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python init_db.py

# 5. Start the server
python main.py
```

### Using START.bat (Windows)
```batch
# Double-click START.bat or run:
START.bat
```

This will:
1. Reset the database
2. Start the server on port 8000
3. Open the browser automatically

---

## 📖 Usage

### Access Points
| URL | Description |
|-----|-------------|
| `http://localhost:8000` | Main parking interface |
| `http://localhost:8000/login` | Login/Register page |
| `http://localhost:8000/dashboard` | User dashboard |
| `http://localhost:8000/admin` | Admin panel |
| `http://localhost:8000/docs` | API documentation (Swagger) |

### Quick Actions

#### 1. Register & Login
```
1. Go to http://localhost:8000/login
2. Click "Register" tab
3. Fill in details (password: 8+ characters)
4. Login with your credentials
```

#### 2. Book a Parking Slot
```
1. Select vehicle type (VIP, EV, Normal, etc.)
2. Set duration (hours)
3. Click the vehicle button
4. View confirmation and slot assignment
```

#### 3. Run Robot Simulation
```
1. Go to "Auto Sim Control" section
2. Add vehicles using +Car or +VIP buttons
3. Click "Start" to begin simulation
4. Watch robots park vehicles automatically
```

#### 4. Reset Simulation
```
1. Click "Reset" button in Auto Sim Control
2. Confirms clearing queue and counters
3. Vehicle numbering restarts from #1
```

---

## 📡 API Documentation

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login and get JWT token |

### Parking Endpoints (Require API Key + JWT)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/entry` | POST | Park a vehicle |
| `/api/reserve` | POST | Reserve a slot |
| `/api/exit` | POST | Exit vehicle from slot |
| `/api/status` | GET | Get all slot statuses |
| `/api/predict` | GET | Get AI predictions |

### Simulation Endpoints (Require API Key)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulate/add_vehicle` | POST | Add vehicle to queue |
| `/api/simulate/step` | GET | Execute one simulation tick |
| `/api/simulate/pattern` | POST | Set traffic pattern |
| `/api/simulate/reset` | POST | Reset simulation state |
| `/api/simulate/undo` | POST | Remove last vehicle |

### User Endpoints (Require JWT)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/user/me` | GET | Get current user info |
| `/user/bookings` | GET | Get user's bookings |
| `/user/notifications` | GET | Get notifications |
| `/user/activity` | GET | Get activity log |
| `/user/booking/extend` | POST | Extend active booking |

### Example API Request
```bash
curl -X POST http://localhost:8000/api/entry \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: YOUR_API_KEY" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"type": "NORMAL", "duration": 2.0}'
```

---

## 🧪 Testing Security

### Run Security Test Suite

```bash
# Terminal 1: Start server
python main.py

# Terminal 2: Run tests
python test_security.py
```

### Expected Output
```
============================================================
  🔐 SMART PARKING AI - SECURITY TEST SUITE
============================================================

✅ Server is running

============================================================
  1️⃣ API KEY AUTHENTICATION TESTS
============================================================

✅ PASS: Auth Check: Missing API Key Header
✅ PASS: Auth Check: Wrong API Key
✅ PASS: Simulation Step: Requires API Key

============================================================
  2️⃣ INPUT VALIDATION TESTS
============================================================

✅ PASS: Validation: Negative Duration
✅ PASS: Validation: Invalid Vehicle Type
✅ PASS: Pattern: Invalid Mode Rejected

============================================================
  3️⃣ INPUT SANITIZATION TESTS
============================================================

✅ PASS: Sanitization: Script Injection Blocked
✅ PASS: Sanitization: SQL Injection Blocked

============================================================
  4️⃣ SECURITY HEADERS TEST
============================================================

✅ PASS: Security Headers Present

============================================================
  5️⃣ VALID REQUEST TESTS
============================================================

✅ PASS: Valid Request: Normal Entry
✅ PASS: Pattern Endpoint: Valid Request
✅ PASS: Reset Simulation: Works with API Key

============================================================
  📊 TEST SUMMARY
============================================================

🎉 ALL TESTS PASSED: 12/12
```

### Understanding HTTP Status Codes

| Code | Meaning | Security Implication |
|------|---------|---------------------|
| 200 | OK | Valid request accepted |
| 400 | Bad Request | Sanitization blocked malicious input |
| 403 | Forbidden | API key missing or invalid |
| 422 | Unprocessable | Validation failed (bad data) |

---

## 📁 Project Structure

```
DDCO PROJECT/
├── 📄 main.py                 # FastAPI application entry point
├── 📄 init_db.py              # Database initialization script
├── 📄 test_security.py        # Security test suite
├── 📄 requirements.txt        # Python dependencies
├── 📄 .env                    # Environment variables (secrets)
├── 📄 .gitignore              # Git ignore rules
├── 📄 README.md               # This file
├── 📄 SECURITY.md             # Security documentation
├── 📄 LICENSE                 # MIT License
├── 📄 START.bat               # Windows startup script
│
├── 📁 backend/
│   ├── 📄 __init__.py         # Package init
│   ├── 📄 controller.py       # Core parking logic (DDCO concepts)
│   ├── 📄 database.py         # SQLAlchemy models
│   ├── 📄 auth.py             # JWT authentication
│   └── 📄 scheduler.py        # Background job scheduler
│
├── 📁 templates/
│   ├── 📄 index.html          # Main parking interface
│   ├── 📄 login.html          # Login/Register page
│   ├── 📄 dashboard.html      # Basic dashboard
│   ├── 📄 unified_dashboard.html  # Enhanced user dashboard
│   └── 📄 unified_home.html   # Alternative home layout
│
└── 📄 smart_parking.db        # SQLite database (auto-generated)
```

---

## 🖼️ Screenshots

### Main Interface
- Real-time slot status grid
- AI prediction panel with probability chart
- Robot simulation control panel
- Vehicle entry form with type selection

### User Dashboard
- Active booking with countdown timer
- Booking history table
- Live notifications
- Activity log

### Security Features
- IDS alerts in server console
- API key validation
- Input sanitization blocking

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
# API Security Key (for endpoint authentication)
SECRET_KEY=DDCO_SMART_PARKING_2024_SECURE_API_KEY_9x7zL4mP

# JWT Secret Key (for user authentication tokens)
JWT_SECRET=JWT_DDCO_PARKING_AUTH_SECRET_2024_aB3dE5fG7hJ9kL2mN4pQ6rS8tU0vW

# Database Configuration
DATABASE_URL=sqlite:///./smart_parking.db

# JWT Token Expiry (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

⚠️ **Never commit `.env` to version control!**

---

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Option 1: Use different port
python main.py 8001

# Option 2: Kill existing process (Windows)
Get-Process -Name python | Stop-Process -Force

# Option 3: Use stop script
python stop_server.py
```

### Database Locked
```bash
# Stop all Python processes
Get-Process -Name python | Stop-Process -Force

# Wait 2 seconds, then reinitialize
python init_db.py
```

### Login Issues
1. Make sure you registered a new account
2. Password must be 8-72 characters
3. Check browser console for errors
4. Clear localStorage and try again

---

## 📚 Learning Resources

### DDCO Concepts
- [ALU Design](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Finite State Machines](https://en.wikipedia.org/wiki/Finite-state_machine)
- [Priority Encoders](https://en.wikipedia.org/wiki/Priority_encoder)

### Technologies Used
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Chart.js](https://www.chartjs.org/)

---

## 👥 Contributors

- **Your Name** - *Initial work* - [GitHub](https://github.com/yourusername)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- DDCO Course Faculty
- FastAPI Community
- Open Source Contributors

---

<div align="center">

**⭐ Star this repo if you found it helpful!**

Made with ❤️ for Learning

</div>



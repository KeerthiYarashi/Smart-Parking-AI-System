from fastapi import FastAPI, Request, Form, Depends, HTTPException, Header, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator, EmailStr
from typing import Literal, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import uvicorn
import time
import os
import re
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from jose import jwt

from backend.controller import ParkingLot, ids
from backend.database import init_db, get_db, User, Booking, Notification, ActivityLog
from backend.auth import get_password_hash, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY as JWT_SECRET, ALGORITHM
from backend.scheduler import start_scheduler, stop_scheduler

load_dotenv()

# --- LIFESPAN CONTEXT MANAGER (Replaces on_event) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler(parking)
    print("\n" + "="*60)
    print("⚠️  IMPORTANT: If you ran START.bat, the database was RESET.")
    print("👉  You MUST register a new account before logging in.")
    print("="*60 + "\n")
    yield
    stop_scheduler()

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

# --- ADD CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL MIDDLEWARE ---
@app.middleware("http")
async def global_security_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response

parking = ParkingLot(total_slots=12)
SECRET_KEY = os.getenv("SECRET_KEY", "SECRET123") # Load from ENV with fallback

# --- SECURITY & VALIDATION MODULES ---

async def verify_api_key(request: Request, x_api_key: str = Header(None)):
    """
    Feature 1: API Key Authentication Middleware
    """
    if x_api_key != SECRET_KEY:
        client_ip = request.client.host if request.client else "Unknown"
        ids.log_event(client_ip, "Invalid API Key", severity="HIGH")
        # Returns HTTP 403 (Forbidden) to the client
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API Key")
    return x_api_key

def sanitize_string(text: str):
    """
    Feature 2: Input Sanitization Helper
    """
    forbidden = ["<", ">", "{", "}", "$", "script", "\\"]
    for f in forbidden:
        if f.lower() in text.lower():
            raise ValueError(f"Invalid characters detected: {f}")
    return text

def _get_authenticated_user(auth_header: Optional[str], db: Session) -> User:
    """Extract and validate user from Authorization header"""
    if not auth_header:
        print("❌ No Authorization header provided")
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not auth_header.startswith("Bearer "):
        print(f"❌ Invalid auth format")
        raise HTTPException(status_code=401, detail="Invalid authentication format")
    
    token = auth_header.split(" ", 1)[1]
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        print(f"🔐 Token decoded: sub={user_id_str}, type={type(user_id_str)}")
        
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        
        # Convert string to int
        user_id = int(user_id_str)
        
    except jwt.ExpiredSignatureError:
        print("❌ Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError as e:
        print(f"❌ JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        print(f"❌ Invalid user_id format: {user_id_str}")
        raise HTTPException(status_code=401, detail="Invalid user ID format")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        print(f"❌ User {user_id} not found")
        raise HTTPException(status_code=401, detail="User not found")
    
    print(f"✅ Authenticated: {user.email}")
    return user

# --- PYDANTIC MODELS (Updated to V2) ---

class VehicleEntryModel(BaseModel):
    type: Literal["AMBULANCE", "VIP", "EV", "SENIOR", "NORMAL"]
    duration: float

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value):
        if value <= 0:
            raise ValueError("Duration must be > 0")
        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        return sanitize_string(value)

class ReserveModel(BaseModel):
    type: Literal["VIP", "EV", "NORMAL"] # Restricted types for reservation
    duration: float

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value):
        if value <= 0:
            raise ValueError("Duration must be > 0")
        return value

class ExitModel(BaseModel):
    slot: int

    @field_validator("slot")
    @classmethod
    def validate_slot(cls, v):
        if v < 1 or v > 12:
            raise ValueError("Invalid slot ID: Must be between 1 and 12")
        return v

class SimVehicleModel(BaseModel):
    type: str
    duration: float
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        return sanitize_string(v)

class PatternModel(BaseModel):
    mode: Literal["MANUAL", "PEAK", "EVENT"]

class UserRegisterModel(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    
    @field_validator("name", "phone")
    @classmethod
    def validate_strings(cls, v):
        return sanitize_string(v)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        # Length validation (8-72 characters for bcrypt compatibility)
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 72:
            raise ValueError("Password must be less than 72 characters (bcrypt limit)")
        return v

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str

class ExtendBookingModel(BaseModel):
    booking_id: int
    additional_hours: float
    
    @field_validator("additional_hours")
    @classmethod
    def validate_hours(cls, v):
        if v <= 0 or v > 4:
            raise ValueError("Can only extend by 0.5 to 4 hours")
        return v

# --- ROUTES ---

# Update root route to serve index.html directly (Bypassing broken unified_home)
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "status": parking.get_status(),
        "message": "System Ready. Waiting for Input...",
        "api_key": SECRET_KEY
    })

# Keep admin panel accessible via /admin
@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "status": parking.get_status(),
        "message": "System Ready. Waiting for Input...",
        "api_key": SECRET_KEY
    })

@app.get("/api/predict")
def get_prediction():
    """
    API Endpoint for AI Prediction Module
    Returns JSON data for the frontend dashboard.
    """
    data = parking.get_ai_prediction()
    return JSONResponse(content=data)


@app.get("/api/status")
def get_status_api():
    """
    Returns the current status of all slots as JSON
    Used for dynamic frontend updates without page reload.
    """
    # jsonable_encoder converts datetime objects to ISO strings
    return JSONResponse(content=jsonable_encoder(parking.get_status()))


# --- UPDATED API ENDPOINTS (With Security & Validation) ---

@app.post("/api/simulate/add_vehicle")
def add_sim_vehicle(data: SimVehicleModel, api_key: str = Depends(verify_api_key)):
    """
    Adds a vehicle to the simulation queue (Protected)
    """
    msg = parking.add_vehicle_to_queue(data.type, data.duration)
    return JSONResponse(content={"message": msg})


@app.post("/api/simulate/pattern")
def set_pattern(data: PatternModel, api_key: str = Depends(verify_api_key)):
    """
    Sets the traffic generation pattern (Protected)
    """
    msg = parking.set_traffic_mode(data.mode)
    return JSONResponse(content={"message": msg})


@app.post("/api/simulate/undo")
def undo_sim_vehicle(api_key: str = Depends(verify_api_key)):
    """
    Removes the last added vehicle from the queue (Protected)
    """
    msg = parking.remove_last_vehicle()
    return JSONResponse(content={"message": msg})


@app.post("/api/entry")
def api_entry(data: VehicleEntryModel, request: Request, api_key: str = Depends(verify_api_key), db: Session = Depends(get_db)):
    user = _get_authenticated_user(request.headers.get('Authorization'), db)
    try:
        msg = parking.process_vehicle(data.type, data.duration)
        slot_match = re.search(r'Slot (\d+)', msg)
        if slot_match:
            slot_id = int(slot_match.group(1))
            cost = parking.alu.calculate_upfront_cost(data.type, data.duration)
            booking = Booking(
                user_id=user.user_id,
                slot_id=slot_id,
                vehicle_type=data.type,
                duration_hours=data.duration,
                entry_time=datetime.utcnow(),
                estimated_end_time=datetime.utcnow() + timedelta(hours=data.duration),
                billing_cost=cost,
                status="ACTIVE"
            )
            db.add(booking)
            db.flush()
            
            db.add(Notification(
                user_id=user.user_id,
                booking_id=booking.booking_id,
                message=f"✅ Slot {slot_id} booked successfully! ({data.type})",
                type="SUCCESS"
            ))
            
            db.add(ActivityLog(
                user_id=user.user_id,
                action=f"Booked Slot {slot_id} ({data.type}) for {data.duration}h",
                timestamp=datetime.utcnow()
            ))
            
            db.commit()
        return JSONResponse(content={"message": msg})
    except ValueError as e:
        db.rollback()
        ids.log_event(request.client.host, f"Validation Error: {str(e)}", "MEDIUM")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/reserve")
def api_reserve(data: ReserveModel, request: Request, api_key: str = Depends(verify_api_key), db: Session = Depends(get_db)):
    user = _get_authenticated_user(request.headers.get('Authorization'), db)
    try:
        msg = parking.reserve_slot(data.type, data.duration)
        slot_match = re.search(r'Slot (\d+)', msg)
        if slot_match:
            slot_id = int(slot_match.group(1))
            cost = parking.alu.calculate_upfront_cost(data.type, data.duration)
            booking = Booking(
                user_id=user.user_id,
                slot_id=slot_id,
                vehicle_type=data.type,
                duration_hours=data.duration,
                entry_time=datetime.utcnow(),
                estimated_end_time=datetime.utcnow() + timedelta(hours=data.duration),
                billing_cost=cost,
                status="ACTIVE"
            )
            db.add(booking)
            db.flush()
            
            db.add(Notification(
                user_id=user.user_id,
                booking_id=booking.booking_id,
                message=f"🔒 Slot {slot_id} reserved successfully!",
                type="SUCCESS"
            ))
            
            db.add(ActivityLog(
                user_id=user.user_id,
                action=f"Reserved Slot {slot_id} for {data.duration}h",
                timestamp=datetime.utcnow()
            ))
            
            db.commit()
        return JSONResponse(content={"message": msg})
    except Exception as e:
        db.rollback()
        ids.log_event(request.client.host, "Reserve Error", "LOW")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/exit")
def api_exit(data: ExitModel, request: Request, api_key: str = Depends(verify_api_key), db: Session = Depends(get_db)):
    user = _get_authenticated_user(request.headers.get('Authorization'), db)
    msg = parking.exit_vehicle(data.slot)
    try:
        booking = db.query(Booking).filter(
            Booking.slot_id == data.slot,
            Booking.user_id == user.user_id,
            Booking.status == "ACTIVE"
        ).first()
        if booking:
            booking.status = "COMPLETED"
            booking.exit_time = datetime.utcnow()
            
            db.add(Notification(
                user_id=user.user_id,
                booking_id=booking.booking_id,
                message=f"👋 Vehicle exited Slot {data.slot}. Thank you!",
                type="INFO"
            ))
            
            db.add(ActivityLog(
                user_id=user.user_id,
                action=f"Released Slot {data.slot}",
                timestamp=datetime.utcnow()
            ))
            
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Exit DB update error: {e}")
    return JSONResponse(content={"message": msg})


@app.get("/api/simulate/step")
def simulate_step(api_key: str = Depends(verify_api_key)):
    """
    Executes one clock cycle of the robot simulation (Protected)
    """
    result = parking.simulation_step()
    return JSONResponse(content=result)


@app.post("/reserve", response_class=HTMLResponse)
def reserve_entry(request: Request, type: str = Form(...), duration: float = Form(...)):
    """
    Handles Slot Reservation with Upfront Billing
    """
    msg = parking.reserve_slot(type, duration)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "status": parking.get_status(),
        "message": msg,
        "api_key": SECRET_KEY # Inject Key
    })


@app.post("/entry", response_class=HTMLResponse)
def vehicle_entry(request: Request, type: str = Form(...), duration: float = Form(...)):
    """
    Handles Vehicle Entry with Upfront Billing
    """
    msg = parking.process_vehicle(type, duration)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "status": parking.get_status(),
        "message": msg,
        "api_key": SECRET_KEY # Inject Key
    })


@app.post("/exit", response_class=HTMLResponse)
def vehicle_exit(request: Request, slot: int = Form(...)):
    msg = parking.exit_vehicle(slot)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "status": parking.get_status(),
        "message": msg,
        "api_key": SECRET_KEY # Inject Key
    })


# --- AUTHENTICATION ENDPOINTS ---

@app.post("/auth/register")
def register_user(data: UserRegisterModel, db: Session = Depends(get_db)):
    try:
        # Check if email exists
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        print(f"📝 Attempting to register user: {data.email}")
        hashed_pwd = get_password_hash(data.password)
        
        new_user = User(
            name=data.name,
            email=data.email,
            phone=data.phone,
            password_hash=hashed_pwd
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log the registration activity
        db.add(ActivityLog(
            user_id=new_user.user_id,
            action="Account created",
            timestamp=datetime.utcnow()
        ))
        db.commit()
        
        print(f"✅ User registered successfully: ID={new_user.user_id}, Email={new_user.email}")
        
        return {
            "message": "Registration successful",
            "user_id": new_user.user_id,
            "email": new_user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Registration error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/auth/login")
def login_user(data: UserLoginModel, db: Session = Depends(get_db)):
    print(f"🔐 Login attempt: {data.email}")
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        print(f"❌ User not found: {data.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(data.password, user.password_hash):
        print(f"❌ Password mismatch for: {data.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    print(f"✅ Login success: {data.email}, user_id={user.user_id}")
    
    # Log the login activity
    db.add(ActivityLog(
        user_id=user.user_id,
        action="Logged in",
        timestamp=datetime.utcnow()
    ))
    db.commit()
    
    # IMPORTANT: Convert user_id to string for JWT consistency
    access_token = create_access_token(data={"sub": str(user.user_id)}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    print(f"🎫 Token created for user_id={user.user_id}")
    return {"access_token": access_token, "token_type": "bearer", "user": {"user_id": user.user_id, "name": user.name, "email": user.email}}

# --- USER DASHBOARD ENDPOINTS ---

@app.get("/user/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "created_at": current_user.created_at
    }

@app.get("/user/bookings")
def get_user_bookings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.user_id == current_user.user_id).order_by(Booking.entry_time.desc()).all()
    now = datetime.utcnow()
    payload = []
    for booking in bookings:
        remaining = None
        if booking.estimated_end_time:
            remaining = int((booking.estimated_end_time - now).total_seconds())
        payload.append({
            "booking_id": booking.booking_id,
            "slot_id": booking.slot_id,
            "vehicle_type": booking.vehicle_type,
            "status": booking.status,
            "entry_time": booking.entry_time,
            "estimated_end_time": booking.estimated_end_time,
            "billing_cost": booking.billing_cost,
            "remaining_seconds": max(0, remaining) if remaining is not None else None
        })
    return jsonable_encoder(payload)

@app.get("/user/notifications")
def get_user_notifications(current_user: User = Depends(get_current_user), unread_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(Notification).filter(Notification.user_id == current_user.user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    notifications = query.order_by(Notification.timestamp.desc()).limit(20).all()
    if unread_only:
        for notif in notifications:
            notif.is_read = True
        db.commit()
    return jsonable_encoder(notifications)

@app.get("/user/notifications/unread")
def get_unread_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.user_id,
        Notification.is_read == False
    ).order_by(Notification.timestamp.asc()).all()
    payload = jsonable_encoder(notifications)
    for notif in notifications:
        notif.is_read = True
    db.commit()
    return payload

@app.post("/user/booking/extend")
def extend_booking(data: ExtendBookingModel, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(
        Booking.booking_id == data.booking_id,
        Booking.user_id == current_user.user_id,
        Booking.status == "ACTIVE"
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Active booking not found")
    
    booking.duration_hours += data.additional_hours
    booking.estimated_end_time += timedelta(hours=data.additional_hours)
    additional_cost = parking.alu.calculate_upfront_cost(booking.vehicle_type, data.additional_hours)
    booking.billing_cost += additional_cost
    parking.extend_slot(booking.slot_id, data.additional_hours)
    
    db.add(Notification(
        user_id=current_user.user_id,
        booking_id=booking.booking_id,
        message=f"✅ Slot {booking.slot_id} extended by {data.additional_hours}h. New end: {booking.estimated_end_time.strftime('%H:%M')}",
        type="SUCCESS"
    ))
    
    db.add(ActivityLog(
        user_id=current_user.user_id,
        action=f"Extended Slot {booking.slot_id} by {data.additional_hours}h",
        timestamp=datetime.utcnow()
    ))
    
    db.commit()
    return {"message": f"Booking extended. Additional cost: ${additional_cost}"}

# Add Activity Log endpoint
@app.get("/user/activity")
def get_user_activity(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.user_id
    ).order_by(ActivityLog.timestamp.desc()).limit(50).all()
    return jsonable_encoder(logs)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    # Check if user is logged in by looking for token
    # This is a soft check - actual auth happens in API calls
    return templates.TemplateResponse("unified_dashboard.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# --- ENTRY POINT ---
if __name__ == "__main__":
    import sys
    
    # Check if port argument provided
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default 8000")
    
    print(f"\n{'='*60}")
    print(f"🚀 Starting Smart Parking AI Server")
    print(f"{'='*60}")
    print(f"📡 Server URL: http://localhost:{port}")
    print(f"🔐 Login Page: http://localhost:{port}/login")
    print(f"📊 Dashboard: http://localhost:{port}/dashboard")
    print(f"{'='*60}\n")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except OSError as e:
        if "10048" in str(e) or "address already in use" in str(e).lower():
            print(f"\n❌ ERROR: Port {port} is already in use!")
            print("\n🔧 Quick Fix Options:")
            print(f"   1. Run: python stop_server.py")
            print(f"   2. Use different port: python main.py 8001")
            print(f"   3. Manually kill the process in Task Manager\n")
        else:
            raise
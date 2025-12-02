from fastapi import FastAPI, Request, Form, Depends, HTTPException, Header, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, validator
from typing import Literal
import uvicorn
import time
import os
from dotenv import load_dotenv

from controller import ParkingLot, ids

load_dotenv() # Load environment variables from .env file

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- GLOBAL MIDDLEWARE ---
@app.middleware("http")
async def global_security_middleware(request: Request, call_next):
    """
    Intercepts every request to:
    1. Measure processing time (Performance)
    2. Add Security Headers (Hardening)
    """
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Calculate execution time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    
    # Add Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    
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

# --- PYDANTIC MODELS ---

class VehicleEntryModel(BaseModel):
    type: Literal["AMBULANCE", "VIP", "EV", "SENIOR", "NORMAL"]
    duration: float

    @validator("duration")
    def validate_duration(cls, value):
        if value <= 0:
            raise ValueError("Duration must be > 0")
        return value

    @validator("type")
    def validate_type(cls, value):
        return sanitize_string(value)

class ReserveModel(BaseModel):
    type: Literal["VIP", "EV", "NORMAL"] # Restricted types for reservation
    duration: float

    @validator("duration")
    def validate_duration(cls, value):
        if value <= 0:
            raise ValueError("Duration must be > 0")
        return value

class ExitModel(BaseModel):
    slot: int

    @validator("slot")
    def validate_slot(cls, v):
        if v < 1 or v > 12:
            raise ValueError("Invalid slot ID: Must be between 1 and 12")
        return v

class SimVehicleModel(BaseModel):
    type: str
    duration: float
    
    @validator("type")
    def validate_type(cls, v):
        return sanitize_string(v)

class PatternModel(BaseModel):
    mode: Literal["MANUAL", "PEAK", "EVENT"]

# -------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "status": parking.get_status(),
        "message": "System Ready. Waiting for Input...",
        "api_key": SECRET_KEY # Inject Key into Template
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
def api_entry(data: VehicleEntryModel, request: Request, api_key: str = Depends(verify_api_key)):
    try:
        msg = parking.process_vehicle(data.type, data.duration)
        return JSONResponse(content={"message": msg})
    except ValueError as e:
        ids.log_event(request.client.host, f"Validation Error: {str(e)}", "MEDIUM")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/reserve")
def api_reserve(data: ReserveModel, request: Request, api_key: str = Depends(verify_api_key)):
    try:
        msg = parking.reserve_slot(data.type, data.duration)
        return JSONResponse(content={"message": msg})
    except Exception as e:
        ids.log_event(request.client.host, "Reserve Error", "LOW")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/exit")
def api_exit(data: ExitModel, request: Request, api_key: str = Depends(verify_api_key)):
    msg = parking.exit_vehicle(data.slot)
    return JSONResponse(content={"message": msg})

# ---------------------------------------------

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


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

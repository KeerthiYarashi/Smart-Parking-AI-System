from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
import uvicorn

from controller import ParkingLot

app = FastAPI()
templates = Jinja2Templates(directory="templates")

parking = ParkingLot(total_slots=12)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "status": parking.get_status(),
        "message": "System Ready. Waiting for Input..."
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


@app.post("/api/simulate/add_vehicle")
def add_sim_vehicle(type: str = Form(...), duration: float = Form(...)):
    """
    Adds a vehicle to the simulation queue
    """
    msg = parking.add_vehicle_to_queue(type, duration)
    return JSONResponse(content={"message": msg})


@app.post("/api/simulate/pattern")
def set_pattern(mode: str = Form(...)):
    """
    Sets the traffic generation pattern (MANUAL, PEAK, EVENT)
    """
    msg = parking.set_traffic_mode(mode)
    return JSONResponse(content={"message": msg})


@app.post("/api/simulate/undo")
def undo_sim_vehicle():
    """
    Removes the last added vehicle from the queue
    """
    msg = parking.remove_last_vehicle()
    return JSONResponse(content={"message": msg})


# --- NEW API ENDPOINTS FOR AJAX (NO RELOAD) ---

@app.post("/api/entry")
def api_entry(type: str = Form(...), duration: float = Form(...)):
    msg = parking.process_vehicle(type, duration)
    return JSONResponse(content={"message": msg})

@app.post("/api/reserve")
def api_reserve(type: str = Form(...), duration: float = Form(...)):
    msg = parking.reserve_slot(type, duration)
    return JSONResponse(content={"message": msg})

@app.post("/api/exit")
def api_exit(slot: int = Form(...)):
    msg = parking.exit_vehicle(slot)
    return JSONResponse(content={"message": msg})

# ---------------------------------------------

@app.get("/api/simulate/step")
def simulate_step():
    """
    Executes one clock cycle of the robot simulation
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
        "message": msg
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
        "message": msg
    })


@app.post("/exit", response_class=HTMLResponse)
def vehicle_exit(request: Request, slot: int = Form(...)):
    msg = parking.exit_vehicle(slot)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "status": parking.get_status(),
        "message": msg
    })


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

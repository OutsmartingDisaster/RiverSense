import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from database.models import GNSSData, Base
from database.session import get_db_session, engine
from worker.tasks import process_raw_data

Base.metadata.create_all(bind=engine)

app = FastAPI()

security = HTTPBearer()

# Environment variable for the bearer token
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
if not BEARER_TOKEN:
    raise ValueError("BEARER_TOKEN environment variable not set")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme != "Bearer" or credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    return credentials.credentials

# Pydantic Models based on api.md

class RawData(BaseModel):
    UTCTimeMillis: int
    TimeNanos: int
    FullBiasNanos: int
    Svid: int
    Cn0DbHz: float
    # Allow any other fields
    class Config:
        extra = "allow"

class NmeaData(BaseModel):
    timestamp: int
    message: str

class StatusData(BaseModel):
    TimeMillis: int
    Svid: int
    Cn0DbHz: float
    ConstellationType: int
    ElevationDegrees: float
    AzimuthDegrees: float
    UsedInFix: bool

class DataPayload(BaseModel):
    raw: List[RawData]
    nmea: List[NmeaData]
    status: List[StatusData]

class UploadPayload(BaseModel):
    station_id: str
    timestamp: str
    data: DataPayload

@app.post("/api/v1/upload", dependencies=[Depends(verify_token)])
async def upload_data(request: Request):
    """
    Accepts raw GNSS data, enqueues a processing task.
    """
    raw_data = await request.body()
    task = process_raw_data.delay(raw_data.decode('utf-8'))
    return {"message": "Data received and is being processed", "task_id": task.id}

@app.get("/")
def read_root():
    return {"message": "Welcome to the RiverSense API"}

# Placeholder data
fake_station_data = {
    "station_A": {"name": "Station A", "location": "Location A", "status": "Active"},
    "station_B": {"name": "Station B", "location": "Location B", "status": "Inactive"},
}

fake_height_data = {
    "station_A": [
        {"timestamp": "2025-08-17T10:00:00Z", "height": 10.5},
        {"timestamp": "2025-08-17T11:00:00Z", "height": 10.6},
    ],
    "station_B": [
        {"timestamp": "2025-08-17T10:00:00Z", "height": 5.2},
        {"timestamp": "2025-08-17T11:00:00Z", "height": 5.3},
    ],
}

@app.get("/api/v1/stations", dependencies=[Depends(verify_token)])
async def get_stations():
    """
    Returns a list of all stations.
    """
    return list(fake_station_data.keys())

@app.get("/api/v1/station/{station_id}", dependencies=[Depends(verify_token)])
async def get_station_details(station_id: str):
    """
    Returns detailed metadata for a specific station.
    """
    if station_id not in fake_station_data:
        raise HTTPException(status_code=404, detail="Station not found")
    return fake_station_data[station_id]

@app.get("/api/v1/download/rinex/{data_id}", dependencies=[Depends(verify_token)])
async def download_rinex_file(data_id: int):
    """
    Downloads the RINEX file for a given data ID.
    """
    with get_db_session() as db_session:
        gnss_data = db_session.query(GNSSData).filter_by(id=data_id).first()
        if not gnss_data or gnss_data.processing_status != "completed":
            raise HTTPException(status_code=404, detail="RINEX file not found or processing not complete.")
        
        if not gnss_data.rinex_file_path or not os.path.exists(gnss_data.rinex_file_path):
            raise HTTPException(status_code=404, detail="RINEX file not found on disk.")

        return FileResponse(gnss_data.rinex_file_path, media_type='application/octet-stream', filename=os.path.basename(gnss_data.rinex_file_path))

@app.get("/api/v1/height/{station_id}", dependencies=[Depends(verify_token)])
async def get_station_height(station_id: str):
    """
    Returns time-series height data for a specific station.
    """
    if station_id not in fake_height_data:
        raise HTTPException(status_code=404, detail="Station not found")
    return fake_height_data[station_id]

class HeightOverridePayload(BaseModel):
    station_id: str
    timestamp: str
    height: float
    user_id: str # For security/auditing

@app.post("/api/v1/height/override", dependencies=[Depends(verify_token)])
async def override_height(payload: HeightOverridePayload):
    """
    Allows manual override of a height measurement.
    This is a secure endpoint and should be protected.
    """
    # Placeholder for authentication/authorization logic
    print(f"User {payload.user_id} is overriding height for station {payload.station_id} at {payload.timestamp} with value {payload.height}")

    # Placeholder for database logic
    # 1. Fetch the original record
    # 2. Archive the original record (e.g., set an 'overridden' flag)
    # 3. Insert the new, corrected record with a 'manual_override' flag
    print("Database logic placeholder: Original value preserved, new value inserted.")

    return {"status": "success", "message": f"Height for {payload.station_id} at {payload.timestamp} overridden by user {payload.user_id}."}
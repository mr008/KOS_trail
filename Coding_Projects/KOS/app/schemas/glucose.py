from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class SensorData(BaseModel):
    red: float = Field(..., ge=0)
    infrared: float = Field(..., ge=0)
    green: float = Field(..., ge=0)
    temperature: float = Field(..., ge=30, le=45)  # Reasonable body temperature range
    motionArtifact: bool

class GlucoseReadingCreate(BaseModel):
    deviceId: str = Field(..., min_length=1)
    userId: str = Field(..., min_length=1)
    timestamp: datetime
    glucoseValue: int = Field(..., ge=40, le=400)  # Valid glucose range from config
    confidence: float = Field(..., ge=0, le=1)
    sensorData: SensorData
    batteryLevel: int = Field(..., ge=0, le=100)
    signalQuality: str = Field(..., pattern="^(excellent|good|fair|poor)$")

class GlucoseReadingResponse(BaseModel):
    status: str
    id: Optional[str] = None
    message: Optional[str] = None

class CurrentGlucoseReading(BaseModel):
    id: str
    userId: str
    deviceId: str
    timestamp: datetime
    glucoseValue: int
    confidence: float
    sensorData: dict
    batteryLevel: int
    signalQuality: str
    createdAt: Optional[datetime] = None 
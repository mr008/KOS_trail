from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from enum import Enum

class SignalQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good" 
    FAIR = "fair"
    POOR = "poor"

class SensorData(BaseModel):
    red: float = Field(..., ge=0, description="Red light sensor reading")
    infrared: float = Field(..., ge=0, description="Infrared sensor reading")
    green: float = Field(..., ge=0, description="Green light sensor reading")
    temperature: float = Field(..., ge=30, le=45, description="Temperature in Celsius (30-45°C)")
    motionArtifact: bool = Field(..., description="Whether motion artifact was detected")

class GlucoseReadingCreate(BaseModel):
    deviceId: str = Field(..., min_length=1, max_length=50, description="Device identifier")
    userId: str = Field(..., min_length=1, max_length=50, description="User identifier")
    timestamp: datetime = Field(..., description="Reading timestamp")
    glucoseValue: int = Field(..., ge=40, le=400, description="Glucose value in mg/dL (40-400)")
    confidence: float = Field(..., ge=0, le=1, description="Reading confidence (0.0-1.0)")
    sensorData: SensorData
    batteryLevel: int = Field(..., ge=0, le=100, description="Battery level percentage")
    signalQuality: SignalQuality = Field(..., description="Signal quality level")

    @validator('timestamp')
    def validate_timestamp_not_future_or_too_old(cls, v):
        """Ensure timestamp is not in the future and not too old - handle both naive and aware datetimes"""
        from datetime import timezone, timedelta
        
        # Convert both timestamps to UTC naive for comparison
        if v.tzinfo is not None:
            # If timezone-aware, convert to UTC then make naive
            v_naive = v.astimezone(timezone.utc).replace(tzinfo=None)
        else:
            # If naive, assume it's already in UTC
            v_naive = v
            
        current_time = datetime.utcnow()
        
        # Check if timestamp is in the future (allowing small buffer for clock skew)
        if v_naive > (current_time + timedelta(minutes=5)):
            raise ValueError(f'timestamp {v_naive} cannot be in the future (current UTC: {current_time})')
        
        # Check if timestamp is too old (older than 72 hours)
        oldest_allowed = current_time - timedelta(hours=72)
        if v_naive < oldest_allowed:
            raise ValueError(f'timestamp {v_naive} is too old. Readings older than 72 hours are not accepted (oldest allowed: {oldest_allowed})')
        
        return v_naive  # Return naive datetime for database compatibility
    
    @validator('glucoseValue')
    def validate_glucose_range(cls, v):
        """Enhanced glucose value validation with medical context"""
        if v < 40:
            raise ValueError('glucose value below 40 mg/dL is dangerously low and likely invalid')
        if v > 400:
            raise ValueError('glucose value above 400 mg/dL is dangerously high and likely invalid')
        return v

    @validator('confidence')
    def validate_confidence_precision(cls, v):
        """Ensure confidence is reasonable precision"""
        if round(v, 3) != v:
            raise ValueError('confidence should not have more than 3 decimal places')
        return v

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

class AnalyticsSummary(BaseModel):
    """Analytics summary response model"""
    period: str
    averageGlucose: float
    timeInRange: dict
    totalReadings: int
    alertsTriggered: int 
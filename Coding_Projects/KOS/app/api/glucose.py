from fastapi import APIRouter, HTTPException, Path, Query
from datetime import datetime
import uuid
from typing import List

from app.schemas.glucose import GlucoseReadingCreate, GlucoseReadingResponse, CurrentGlucoseReading
from app.core.database import database

router = APIRouter()

@router.post("/devices/{device_id}/readings", response_model=GlucoseReadingResponse, status_code=201)
async def create_glucose_reading(
    device_id: str = Path(..., description="Device ID"),
    reading: GlucoseReadingCreate = None
):
    """
    Submit a glucose reading from an ARGUS device
    """
    try:
        # Validate device_id matches the one in the request body
        if reading.deviceId != device_id:
            raise HTTPException(
                status_code=400, 
                detail="Device ID in URL must match deviceId in request body"
            )
        
        # Let the database generate the UUID (since it has gen_random_uuid() as default)
        # reading_id = str(uuid.uuid4())
        
        # Insert into database
        import json
        sensor_data_json = {
            "red": reading.sensorData.red,
            "infrared": reading.sensorData.infrared,
            "green": reading.sensorData.green,
            "temperature": reading.sensorData.temperature,
            "motionArtifact": reading.sensorData.motionArtifact
        }
        
        insert_query = """
            INSERT INTO glucose_readings (
                user_id, device_id, timestamp, glucose_value, 
                confidence, sensor_data, battery_level, signal_quality
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """
        
        # Convert timestamp to naive datetime (remove timezone info for PostgreSQL)
        timestamp_naive = reading.timestamp.replace(tzinfo=None)
        
        async with database.pool.acquire() as connection:
            result = await connection.fetchval(
                insert_query,
                reading.userId,
                reading.deviceId,
                timestamp_naive,
                reading.glucoseValue,
                reading.confidence,
                json.dumps(sensor_data_json),
                reading.batteryLevel,
                reading.signalQuality
            )
            reading_id = str(result)
        
        return GlucoseReadingResponse(
            status="processed",
            id=reading_id,
            message="Glucose reading saved successfully"
        )
        
    except Exception as e:
        print(f"Error saving glucose reading: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to save glucose reading: {str(e)}")

@router.get("/devices/{device_id}/readings", response_model=List[CurrentGlucoseReading])
async def get_device_readings(
    device_id: str = Path(..., description="Device ID"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of readings to return"),
    offset: int = Query(default=0, ge=0, description="Number of readings to skip")
):
    """
    Get all glucose readings for a specific device, ordered by timestamp (newest first)
    """
    try:
        # Query to get all glucose readings for the device
        query = """
            SELECT id, user_id, device_id, timestamp, glucose_value, 
                   confidence, sensor_data, battery_level, signal_quality, created_at
            FROM glucose_readings 
            WHERE device_id = $1 
            ORDER BY timestamp DESC 
            LIMIT $2 OFFSET $3
        """
        
        async with database.pool.acquire() as connection:
            rows = await connection.fetch(query, device_id, limit, offset)
            
            if not rows:
                # Return empty array if no readings found
                return []
            
            # Convert the rows to our response model
            import json
            readings = []
            for row in rows:
                sensor_data = json.loads(row['sensor_data']) if row['sensor_data'] else {}
                
                reading = CurrentGlucoseReading(
                    id=str(row['id']),
                    userId=row['user_id'],
                    deviceId=row['device_id'],
                    timestamp=row['timestamp'],
                    glucoseValue=row['glucose_value'],
                    confidence=float(row['confidence']),
                    sensorData=sensor_data,
                    batteryLevel=row['battery_level'],
                    signalQuality=row['signal_quality'],
                    createdAt=row['created_at']
                )
                readings.append(reading)
            
            return readings
            
    except Exception as e:
        print(f"Error getting device readings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get device readings: {str(e)}")

@router.get("/users/{user_id}/glucose/current", response_model=CurrentGlucoseReading)
async def get_current_glucose(
    user_id: str = Path(..., description="User ID")
):
    """
    Get the most recent glucose reading for a user
    """
    try:
        # Query to get the most recent glucose reading for the user
        query = """
            SELECT id, user_id, device_id, timestamp, glucose_value, 
                   confidence, sensor_data, battery_level, signal_quality, created_at
            FROM glucose_readings 
            WHERE user_id = $1 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        async with database.pool.acquire() as connection:
            row = await connection.fetchrow(query, user_id)
            
            if not row:
                raise HTTPException(
                    status_code=404, 
                    detail=f"No glucose readings found for user {user_id}"
                )
            
            # Convert the row to our response model
            import json
            sensor_data = json.loads(row['sensor_data']) if row['sensor_data'] else {}
            
            return CurrentGlucoseReading(
                id=str(row['id']),
                userId=row['user_id'],
                deviceId=row['device_id'],
                timestamp=row['timestamp'],
                glucoseValue=row['glucose_value'],
                confidence=float(row['confidence']),
                sensorData=sensor_data,
                batteryLevel=row['battery_level'],
                signalQuality=row['signal_quality'],
                createdAt=row['created_at']
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        print(f"Error getting current glucose: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get current glucose: {str(e)}") 
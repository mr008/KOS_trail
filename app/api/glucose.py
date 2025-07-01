from fastapi import APIRouter, HTTPException, Path, Query, Depends
from datetime import datetime
import uuid
from typing import List
import json

from app.schemas.glucose import GlucoseReadingCreate, GlucoseReadingResponse, CurrentGlucoseReading
from app.core.database import database
from app.core.redis_client import redis_client
from app.core.auth import verify_api_key, verify_jwt

router = APIRouter()

@router.post("/devices/{device_id}/readings", response_model=GlucoseReadingResponse, status_code=201)
async def create_glucose_reading(
    device_id: str = Path(..., description="Device ID"),
    reading: GlucoseReadingCreate = None,
    api_key: str = Depends(verify_api_key)
):
    """
    Submit a glucose reading from an ARGUS device
    Includes rate limiting (30 seconds between readings per device)
    Validates foreign key constraints for users and devices
    """
    try:
        # Validate device_id matches the one in the request body
        if reading.deviceId != device_id:
            raise HTTPException(
                status_code=400, 
                detail="Device ID in URL must match deviceId in request body"
            )
        
        # Check if user and device exist (foreign key validation)
        async with database.pool.acquire() as connection:
            # Check if user exists
            user_exists = await connection.fetchval(
                "SELECT 1 FROM users WHERE user_id = $1", 
                reading.userId
            )
            if not user_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"User {reading.userId} does not exist. Please ensure user is registered."
                )
            
            # Check if device exists and belongs to user
            device_exists = await connection.fetchval(
                "SELECT 1 FROM devices WHERE device_id = $1 AND user_id = $2", 
                reading.deviceId, reading.userId
            )
            if not device_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Device {reading.deviceId} does not exist or does not belong to user {reading.userId}"
                )
        
        # Rate limiting check using Redis
        rate_limit_key = f"rate_limit:{device_id}"
        
        # Check if device has submitted a reading recently
        if redis_client.client:
            existing_limit = await redis_client.client.get(rate_limit_key)
            if existing_limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Device {device_id} can only submit one reading every 30 seconds."
                )
            
            # Set rate limit for 30 seconds
            await redis_client.client.setex(rate_limit_key, 30, "1")
        else:
            # If Redis is not available, log warning but continue
            print("⚠️ Warning: Redis not available for rate limiting")
        
        # Prepare sensor data JSON
        sensor_data_json = {
            "red": reading.sensorData.red,
            "infrared": reading.sensorData.infrared,
            "green": reading.sensorData.green,
            "temperature": reading.sensorData.temperature,
            "motionArtifact": reading.sensorData.motionArtifact
        }
        
        # Insert into database using optimized query
        insert_query = """
            INSERT INTO glucose_readings (
                user_id, device_id, timestamp, glucose_value, 
                confidence, sensor_data, battery_level, signal_quality
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """
        
        # Timestamp is already converted to naive by the validator
        async with database.pool.acquire() as connection:
            result = await connection.fetchval(
                insert_query,
                reading.userId,
                reading.deviceId,
                reading.timestamp,  # Already naive from validator
                reading.glucoseValue,
                reading.confidence,
                json.dumps(sensor_data_json),
                reading.batteryLevel,
                reading.signalQuality.value  # Use .value for Enum
            )
            reading_id = str(result)
        
        return GlucoseReadingResponse(
            status="processed",
            id=reading_id,
            message="Glucose reading saved successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 400, 429)
        raise
    except Exception as e:
        print(f"Error saving glucose reading: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        
        # Handle specific database errors
        error_message = str(e)
        if "duplicate key value violates unique constraint" in error_message:
            if "glucose_readings_device_id_timestamp_key" in error_message:
                raise HTTPException(
                    status_code=409, 
                    detail=f"A reading for device {device_id} at timestamp {reading.timestamp} already exists. Duplicate readings are not allowed."
                )
        
        raise HTTPException(status_code=500, detail=f"Failed to save glucose reading: {str(e)}")

@router.get("/devices/{device_id}/readings", response_model=List[CurrentGlucoseReading])
async def get_device_readings(
    device_id: str = Path(..., description="Device ID"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of readings to return"),
    offset: int = Query(default=0, ge=0, description="Number of readings to skip"),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all glucose readings for a specific device, ordered by timestamp (newest first)
    Uses optimized index: idx_glucose_readings_device_timestamp
    """
    try:
        # Query optimized to use idx_glucose_readings_device_timestamp index
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
    user_id: str = Path(..., description="User ID"),
    token: str = Depends(verify_jwt)
):
    """
    Get the most recent glucose reading for a user
    Uses optimized index: idx_glucose_readings_user_timestamp
    """
    try:
        # Query optimized to use idx_glucose_readings_user_timestamp index
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
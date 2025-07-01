from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

from app.core.config import settings
from app.core.database import database
from app.core.redis_client import redis_client
from app.api.glucose import router as glucose_router

# Create FastAPI app
app = FastAPI(
    title="KOS Glucose Monitoring API",
    description="Backend API for glucose monitoring with ARGUS devices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(glucose_router, prefix="/api/v1", tags=["glucose"])

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    print("🚀 Starting KOS Glucose Monitoring API...")
    
    # Connect to database
    db_connected = await database.connect()
    if not db_connected:
        print("❌ Failed to connect to database. Exiting...")
        raise Exception("Database connection failed")
    
    # Test database connection
    await database.test_connection()
    
    # Connect to Redis
    redis_connected = await redis_client.connect()
    if not redis_connected:
        print("❌ Failed to connect to Redis. Exiting...")
        raise Exception("Redis connection failed")
    
    # Test Redis connection
    await redis_client.test_connection()
    
    print("✅ All services connected successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown"""
    print("🔄 Shutting down...")
    await database.disconnect()
    await redis_client.disconnect()
    print("👋 Goodbye!")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "KOS Glucose Monitoring API",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "KOS Glucose Monitoring API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "api": "/api/v1"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 
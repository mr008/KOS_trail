"""
KOS Glucose Monitoring API - Main Application Module

This is the main FastAPI application for the KOS (Keep Operating System) Glucose 
Monitoring backend. It provides enterprise-grade REST API endpoints for glucose 
monitoring devices and user applications.

Key Features:
- Real-time glucose data ingestion from ARGUS devices
- Multi-layer authentication (API keys for devices, JWT for users)
- Rate limiting and data validation
- PostgreSQL database with connection pooling
- Redis caching for performance
- Comprehensive error handling and logging

Author: Backend Engineer Work Trial
Version: 1.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

from app.core.config import settings
from app.core.database import database
from app.core.redis_client import redis_client
from app.api.glucose import router as glucose_router

# Create FastAPI app with comprehensive metadata
app = FastAPI(
    title="KOS Glucose Monitoring API",
    description="Backend API for glucose monitoring with ARGUS devices",
    version="1.0.0",
    docs_url="/docs",         # Swagger UI documentation
    redoc_url="/redoc"        # ReDoc documentation
)

# Configure CORS middleware for cross-origin requests
# Note: In production, restrict allow_origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API route modules
app.include_router(glucose_router, prefix="/api/v1", tags=["glucose"])

@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler
    
    Initializes all required services and connections:
    1. PostgreSQL database connection pool
    2. Redis cache connection
    3. Connection health checks
    
    Raises:
        Exception: If any critical service fails to connect
    """
    print("🚀 Starting KOS Glucose Monitoring API...")
    
    # Initialize PostgreSQL connection pool
    db_connected = await database.connect()
    if not db_connected:
        print("❌ Failed to connect to database. Exiting...")
        raise Exception("Database connection failed")
    
    # Verify database connectivity with test query
    await database.test_connection()
    
    # Initialize Redis connection for caching and rate limiting
    redis_connected = await redis_client.connect()
    if not redis_connected:
        print("❌ Failed to connect to Redis. Exiting...")
        raise Exception("Redis connection failed")
    
    # Verify Redis connectivity
    await redis_client.test_connection()
    
    print("✅ All services connected successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler
    
    Gracefully closes all connections and cleans up resources:
    1. Closes database connection pool
    2. Closes Redis connection
    3. Logs shutdown completion
    """
    print("🔄 Shutting down...")
    await database.disconnect()
    await redis_client.disconnect()
    print("👋 Goodbye!")

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    
    Returns:
        dict: Service status information including timestamp and version
    """
    return {
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "KOS Glucose Monitoring API",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """
    Root endpoint providing API information and available endpoints
    
    Returns:
        dict: API metadata and endpoint discovery information
    """
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

# Development server configuration
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 
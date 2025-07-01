"""
Authentication and authorization dependencies for the KOS API
"""
from fastapi import HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os

# Security scheme for JWT Bearer tokens
security = HTTPBearer()

# Valid API keys (in production, these would be in a database)
VALID_API_KEYS = {
    "dev-api-key-12345": "development",
    "prod-api-key-67890": "production",
    "test-api-key-abcde": "testing"
}

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Verify API key for device endpoints
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Raises:
        HTTPException: 401 if API key is missing or invalid
        
    Returns:
        str: The validated API key
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Please include X-API-Key header."
        )
    
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key. Please check your X-API-Key header."
        )
    
    return x_api_key

async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify JWT token for user endpoints (placeholder implementation)
    
    Args:
        credentials: Bearer token from Authorization header
        
    Raises:
        HTTPException: 401 if token is missing or malformed
        
    Returns:
        str: The validated token
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization token. Please include Authorization: Bearer <token> header."
        )
    
    if not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization token format. Please use 'Bearer <token>' format."
        )
    
    # In production, this would validate the JWT signature, expiration, etc.
    # For now, we just check that it's present and properly formatted
    token = credentials.credentials
    
    if len(token) < 10:  # Basic check for reasonable token length
        raise HTTPException(
            status_code=401,
            detail="Invalid token format. Token too short."
        )
    
    return token

# Optional: Helper function to get current user from JWT (placeholder)
async def get_current_user(token: str = Depends(verify_jwt)):
    """
    Extract user information from JWT token (placeholder)
    
    Args:
        token: Validated JWT token
        
    Returns:
        dict: User information (placeholder)
    """
    # In production, this would decode the JWT and return user info
    return {
        "user_id": "extracted_from_jwt",
        "token": token
    } 
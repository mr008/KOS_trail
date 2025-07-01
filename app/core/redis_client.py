import redis.asyncio as redis
from typing import Optional
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Create Redis connection"""
        try:
            self.client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={},
            )
            # Test the connection
            await self.client.ping()
            print("✅ Redis connected successfully")
            return True
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            print("🔌 Redis disconnected")
    
    async def test_connection(self):
        """Test Redis connection"""
        if not self.client:
            return False
        try:
            result = await self.client.ping()
            print(f"✅ Redis test successful: PONG = {result}")
            return True
        except Exception as e:
            print(f"❌ Redis test failed: {e}")
            return False

# Global Redis instance
redis_client = RedisClient() 
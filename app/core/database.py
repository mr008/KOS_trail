import asyncpg
import asyncio
from typing import Optional
from app.core.config import settings

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=settings.db_host,
                port=settings.db_port,
                database=settings.db_name,
                user=settings.db_user,
                password=settings.db_password,
                min_size=1,
                max_size=10,
            )
            print("✅ Database connected successfully")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            print("🔌 Database disconnected")
    
    async def test_connection(self):
        """Test database connection"""
        if not self.pool:
            return False
        try:
            async with self.pool.acquire() as connection:
                result = await connection.fetchval("SELECT NOW()")
                print(f"✅ Database test successful: {result}")
                return True
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return False

# Global database instance
database = Database() 
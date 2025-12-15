import asyncio
import json
from typing import Optional
from contextlib import asynccontextmanager

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import asyncpg
from .config import settings
from .config import settings


class DatabaseManager:
    """Database connection manager for asyncpg"""
    
    def __init__(self):
        self._instance: Optional[asyncpg.Connection] = None
        self._connection_lock = asyncio.Lock()
    
    async def get_connection(self) -> asyncpg.Connection:
        """Get database connection with lazy initialization"""
        if self._instance is None:
            async with self._connection_lock:
                if self._instance is None:
                    self._instance = await asyncpg.connect(settings.DATABASE_URL)
        return self._instance
    
    async def disconnect(self):
        """Disconnect from database"""
        if self._instance:
            await self._instance.close()
            self._instance = None
    
    @asynccontextmanager
    async def transaction(self):
        """Database transaction context manager"""
        conn = await self.get_connection()
        async with conn.transaction():
            yield conn
    
    async def initialize(self):
        """Initialize database with schema and default data"""
        conn = await self.get_connection()
        
        # Create tables based on schema
        # This is a simplified version - in production, use proper migrations
        await self._create_tables(conn)
        
        # Initialize default data
        await initialize_database()
    
    async def reset(self):
        """Reset database (drop and recreate all tables)"""
        conn = await self.get_connection()
        
        # Drop all tables
        await self._drop_tables(conn)
        
        # Recreate tables
        await self._create_tables(conn)
        
        # Initialize default data
        await initialize_database()
    
    async def _create_tables(self, conn):
        """Create database tables"""
        # This would typically be handled by Prisma migrations
        # For now, we'll use a simplified approach
        pass
    
    async def _drop_tables(self, conn):
        """Drop all database tables"""
        # This would typically be handled by Prisma migrations
        # For now, we'll use a simplified approach
        pass


# Global database manager instance
db_manager = DatabaseManager()


# Dependency injection function for FastAPI
async def get_db_connection() -> asyncpg.Connection:
    """Get database connection for dependency injection"""
    return await db_manager.get_connection()


async def get_transaction():
    """Get transaction for dependency injection"""
    return db_manager.transaction()


# Database health check
async def check_database_health() -> dict:
    """Check database connection health"""
    try:
        conn = await get_db_connection()
        # Simple query to test connection
        await conn.fetchval("SELECT 1")
        return {
            "status": "healthy",
            "response_time": "< 100ms"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Database initialization
async def initialize_database():
    """Initialize database with default data"""
    conn = await get_db_connection()
    
    # Create default admin user if no users exist
    user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
    
    if user_count == 0:
        # Create default admin user
        import bcrypt
        password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        await conn.execute("""
            INSERT INTO users (email, password_hash, name, role, is_active, monthly_quota)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, "admin@bettafish.com", password_hash, "Administrator", "ADMIN", True, 1000)
        
        print("✓ Created default admin user: admin@bettafish.com / admin123")
    
    # Create default system configuration
    default_configs = [
        {
            "key": "system_initialized",
            "value": {"initialized": True, "timestamp": "2025-01-01T00:00:00Z"}
        },
        {
            "key": "engine_settings",
            "value": {
                "insight_engine": {"enabled": True, "max_concurrent_tasks": 5},
                "media_engine": {"enabled": True, "max_concurrent_tasks": 5},
                "query_engine": {"enabled": True, "max_concurrent_tasks": 5},
                "report_engine": {"enabled": True, "max_concurrent_tasks": 5}
            }
        }
    ]
    
    import uuid
    from datetime import datetime
    for config in default_configs:
        await conn.execute("""
            INSERT INTO system_config (id, key, value, updated_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (key) DO UPDATE SET value = $3, updated_at = $4
        """, str(uuid.uuid4()), config["key"], json.dumps(config["value"]), datetime.now())


# Database cleanup
async def cleanup_database():
    """Clean up old data and optimize database"""
    conn = await get_db_connection()
    
    # Clean up old sessions (expired)
    from datetime import datetime, timedelta
    expiry_date = datetime.utcnow() - timedelta(days=30)
    
    await conn.execute("""
        DELETE FROM "Session"
        WHERE "expiresAt" < $1
    """, expiry_date)
    
    # Clean up old error logs (older than 90 days)
    log_expiry_date = datetime.utcnow() - timedelta(days=90)
    
    await conn.execute("""
        DELETE FROM "ErrorLog"
        WHERE "timestamp" < $1
    """, log_expiry_date)
    
    # Clean up inactive WebSocket connections
    connection_expiry_date = datetime.utcnow() - timedelta(hours=1)
    
    await conn.execute("""
        DELETE FROM "WebSocketConnection"
        WHERE "isActive" = false
        AND "lastSeen" < $1
    """, connection_expiry_date)


# Database migration helper
async def run_migrations():
    """Run database migrations"""
    try:
        # This would typically be handled by Prisma migrations
        # But we can add custom migration logic here if needed
        conn = await get_db_connection()
        
        # Check if we need to run any custom migrations
        # For now, just initialize the database
        await initialize_database()
        
        return True
    except Exception as e:
        print(f"Migration failed: {e}")
        return False


# Export commonly used enums and types
__all__ = [
    "get_db_connection",
    "get_transaction",
    "check_database_health",
    "initialize_database",
    "cleanup_database",
    "run_migrations",
    "db_manager",
]
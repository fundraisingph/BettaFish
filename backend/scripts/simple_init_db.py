#!/usr/bin/env python3
"""
Simple database initialization script for BettaFish FastAPI backend.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path to import from backend
sys.path.append(str(Path(__file__).parent.parent))

from core.database import get_db_connection
from core.config import settings

async def init_database():
    """Initialize database with basic schema and default data"""
    print("Initializing BettaFish database...")
    
    try:
        # Get database connection
        conn = await get_db_connection()
        
        # Create basic users table
        print("Creating users table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(255),
                organization VARCHAR(255),
                role VARCHAR(50) DEFAULT 'USER',
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create default admin user
        print("Creating default admin user...")
        import bcrypt
        
        admin_password = bcrypt.hashpw(
            "admin123".encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Check if admin user already exists
        existing_admin = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1", "admin@bettafish.com"
        )
        
        if not existing_admin:
            await conn.execute(
                """
                    INSERT INTO users (email, password_hash, name, role, is_active)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                "admin@bettafish.com", admin_password, "System Administrator", "ADMIN", True
            )
            print("✓ Admin user created (admin@bettafish.com / admin123)")
        else:
            print("✓ Admin user already exists")
        
        print("\n✅ Database initialization completed successfully!")
        print("\nDefault admin credentials:")
        print("  Email: admin@bettafish.com")
        print("  Password: admin123")
        print("\nPlease change admin password after first login.")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python simple_init_db.py [init]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        await init_database()
    else:
        print("Invalid command. Use: init")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
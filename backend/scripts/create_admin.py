#!/usr/bin/env python3
"""
Simple admin user creation script for BettaFish FastAPI backend.
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import bcrypt
import uuid

# Load environment variables
load_dotenv()

# Add parent directory to path to import backend modules
sys.path.append(str(Path(__file__).parent.parent))

async def main():
    """Create default admin user"""
    print("Creating default admin user...")
    
    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    print(f"Database URL: {database_url}")
    
    # Try to connect to database
    try:
        import asyncpg
        
        # Connect to database
        conn = await asyncpg.connect(database_url)
        print("✓ Database connection successful")
        
        # Check if users table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'users'
            )
        """)
        
        if not table_exists:
            print("❌ Users table does not exist. Please run Prisma migrations first.")
            await conn.close()
            sys.exit(1)
        
        # Check if admin user already exists
        admin_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM users
                WHERE email = $1
            )
        """, "admin@bettafish.com")
        
        if admin_exists:
            print("✓ Admin user already exists")
            await conn.close()
            return
        
        # Create password hash
        password = "admin123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin user
        await conn.execute("""
            INSERT INTO users (
                id,
                email,
                password_hash,
                name,
                organization,
                role,
                is_active,
                api_key,
                monthly_quota,
                created_at,
                updated_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW()
            )
        """,
        str(uuid.uuid4()),
        "admin@bettafish.com",
        password_hash,
        "System Administrator",
        "BettaFish",
        "ADMIN",
        True,
        "bettafish-admin-api-key",
        100
        )
        
        print("✓ Admin user created successfully")
        print("  Email: admin@bettafish.com")
        print("  Password: admin123")
        print("  Role: ADMIN")
        
        # Close connection
        await conn.close()
        print("✓ Database connection closed")
        
        print("\n✅ Admin user creation completed successfully!")
        
    except Exception as e:
        print(f"❌ Admin user creation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
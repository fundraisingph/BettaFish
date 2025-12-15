#!/usr/bin/env python3
"""
Simple database connection test for BettaFish FastAPI backend.
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

# Add parent directory to path to import backend modules
sys.path.append(str(Path(__file__).parent.parent))

async def main():
    """Test database connection"""
    print("Testing BettaFish database connection...")
    
    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    print(f"Database URL: {database_url}")
    
    # Try to connect to database using raw SQL
    try:
        import asyncpg
        
        # Test connection
        conn = await asyncpg.connect(database_url)
        print("✓ Database connection successful")
        
        # Test simple query
        result = await conn.fetchval("SELECT 1 as test")
        print(f"✓ Query result: {result}")
        
        # Close connection
        await conn.close()
        print("✓ Database connection closed")
        
        print("\n✅ Database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Simple database initialization script for BettaFish FastAPI backend.
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import backend modules
sys.path.append(str(Path(__file__).parent.parent))

async def main():
    """Initialize database with basic setup"""
    print("Initializing BettaFish database...")
    
    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    print(f"Database URL: {database_url}")
    
    # Try to connect to database
    try:
        # Import database connection
        import sys
        from pathlib import Path
        
        # Add backend directory to Python path
        backend_path = Path(__file__).parent.parent
        sys.path.insert(0, str(backend_path))
        
        # Import database manager
        from core.database import get_db_connection
        
        # Test connection
        print("Testing database connection...")
        conn = await get_db_connection()
        await conn.execute("SELECT 1")
        print("✓ Database connection successful")
        
        # Initialize database with basic data
        from core.database import initialize_database
        print("Initializing database with default data...")
        await initialize_database()
        print("✓ Database data initialization completed")
        
        print("\n✅ Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
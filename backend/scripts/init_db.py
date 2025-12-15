#!/usr/bin/env python3
"""
Database initialization script for BettaFish FastAPI backend.
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
    """Initialize database with schema and default data"""
    print("Initializing BettaFish database...")
    
    try:
        # Get Prisma client
        conn = await get_db_connection()
        
        # Initialize basic database schema
        print("Initializing basic database schema...")
        
        # Create basic users table
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
        
        print("✓ Basic database schema created")
        
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
        
        # Create default system settings
        print("Creating default system settings...")
        
        # Skip system settings for now as table doesn't exist in schema
        print("✓ System settings skipped (table not in schema)")
        
        print("\n✅ Database initialization completed successfully!")
        print("\nDefault admin credentials:")
        print("  Email: admin@bettafish.com")
        print("  Password: admin123")
        print("\nPlease change the admin password after first login.")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

async def reset_database():
    """Reset database (drop and recreate all tables)"""
    print("⚠️  WARNING: This will delete all data in the database!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("Database reset cancelled.")
        return
    
    try:
        # Reset database
        print("Resetting database...")
        from core.database import db_manager
        await db_manager.reset()
        
        # Reinitialize
        await init_database()
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        sys.exit(1)

async def seed_database():
    """Seed database with sample data for development"""
    print("Seeding database with sample data...")
    
    try:
        conn = await get_db_connection()
        
        # Create sample users
        print("Creating sample users...")
        import bcrypt
        
        sample_users = [
            {
                "email": "user@example.com",
                "password": "user123",
                "name": "Sample User",
                "organization": "Example Organization"
            },
            {
                "email": "researcher@example.com",
                "password": "research123",
                "name": "Research User",
                "organization": "Research Institute"
            }
        ]
        
        for user_data in sample_users:
            existing_user = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1", user_data["email"]
            )
            
            if not existing_user:
                password_hash = bcrypt.hashpw(
                    user_data["password"].encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                await conn.execute(
                    """
                    INSERT INTO users (email, password_hash, name, organization, role, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    user_data["email"], password_hash, user_data["name"], user_data["organization"], "USER", True
                )
                print(f"✓ Created user: {user_data['email']}")
        
        # Create sample analysis task
        print("Creating sample analysis task...")
        
        user_id = (await conn.fetchrow("SELECT id FROM users WHERE email = $1", "user@example.com"))["id"]
        
        await conn.execute(
            """
            INSERT INTO analysis_tasks (user_id, title, description, query, status, progress, engines, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            user_id, "Sample Public Opinion Analysis", "This is a sample analysis task for demonstration purposes.",
            "Sample query for testing", "COMPLETED", 100,
            '["InsightEngine", "MediaEngine", "QueryEngine"]',
            "2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z"
        )
        
        sample_task = await conn.fetchrow("SELECT id FROM analysis_tasks WHERE title = $1", "Sample Public Opinion Analysis")
        
        # Create sample agent outputs
        print("Creating sample agent outputs...")
        
        for engine_type in ["InsightEngine", "MediaEngine", "QueryEngine"]:
            await conn.execute(
                """
                INSERT INTO agent_outputs (task_id, engine_type, output_type, content, metadata, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                sample_task["id"], engine_type, "result", f"Sample output from {engine_type}",
                '{"sample": true}', "2024-01-01T00:30:00Z"
            )
        
        # Create sample report
        print("Creating sample report...")
        
        await conn.execute(
            """
            INSERT INTO reports (task_id, title, content, format, file_path, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            sample_task["id"], "Sample Analysis Report", "# Sample Report\n\nThis is a sample report generated from the analysis task.",
            "HTML", "/reports/sample_report.html", "2024-01-01T02:00:00Z"
        )
        
        print("\n✅ Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Database seeding failed: {e}")
        sys.exit(1)

async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python init_db.py [init|reset|seed]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        await init_database()
    elif command == "reset":
        await reset_database()
    elif command == "seed":
        await seed_database()
    else:
        print("Invalid command. Use: init, reset, or seed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
"""
ReportEngine Database Manager
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from core.database import get_db_connection
from ..utils.config import report_config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for ReportEngine"""
    
    def __init__(self):
        self.config = report_config
    
    async def create_tables(self):
        """Create ReportEngine tables"""
        db = await get_db_connection()
        
        # Create report_tasks table
        await db.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.config.db_table_prefix}tasks (
                id VARCHAR(255) PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                title VARCHAR(500) NOT NULL,
                template_type VARCHAR(50) NOT NULL DEFAULT 'comprehensive',
                engine_outputs JSONB,
                include_charts BOOLEAN NOT NULL DEFAULT FALSE,
                output_format VARCHAR(50) NOT NULL DEFAULT 'markdown',
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                error TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create report_states table
        await db.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.config.db_table_prefix}states (
                session_id VARCHAR(255) PRIMARY KEY,
                state_data JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create report_templates table
        await db.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.config.db_table_prefix}templates (
                id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(50) NOT NULL DEFAULT 'general',
                engine_types JSONB,
                template_data JSONB,
                is_custom BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create report_sessions table
        await db.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.config.db_table_prefix}sessions (
                session_id VARCHAR(255) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create indexes
        await db.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.config.db_table_prefix}tasks_session_id 
            ON {self.config.db_table_prefix}tasks (session_id)
        """)
        
        await db.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.config.db_table_prefix}tasks_user_id 
            ON {self.config.db_table_prefix}tasks (user_id)
        """)
        
        await db.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.config.db_table_prefix}tasks_status 
            ON {self.config.db_table_prefix}tasks (status)
        """)
        
        await db.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.config.db_table_prefix}tasks_created_at 
            ON {self.config.db_table_prefix}tasks (created_at)
        """)
        
        await db.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.config.db_table_prefix}states_updated_at 
            ON {self.config.db_table_prefix}states (updated_at)
        """)
        
        logger.info("ReportEngine database tables created successfully")
    
    async def drop_tables(self):
        """Drop ReportEngine tables"""
        db = await get_db_connection()
        
        tables = [
            f"{self.config.db_table_prefix}tasks",
            f"{self.config.db_table_prefix}states",
            f"{self.config.db_table_prefix}templates",
            f"{self.config.db_table_prefix}sessions"
        ]
        
        for table in tables:
            await db.execute(f"DROP TABLE IF EXISTS {table}")
        
        # Drop indexes
        indexes = [
            f"idx_{self.config.db_table_prefix}tasks_session_id",
            f"idx_{self.config.db_table_prefix}tasks_user_id",
            f"idx_{self.config.db_table_prefix}tasks_status",
            f"idx_{self.config.db_table_prefix}tasks_created_at",
            f"idx_{self.config.db_table_prefix}states_updated_at"
        ]
        
        for index in indexes:
            await db.execute(f"DROP INDEX IF EXISTS {index}")
        
        logger.info("ReportEngine database tables dropped successfully")
    
    async def save_task(self, task_data: Dict[str, Any]) -> str:
        """Save a task to database"""
        db = await get_db_connection()
        
        await db.execute(f"""
            INSERT INTO {self.config.db_table_prefix}tasks (
                id, session_id, user_id, title, template_type, 
                engine_outputs, include_charts, output_format, status, created_at, updated_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10
            )
        """,
            task_data["id"],
            task_data["session_id"],
            task_data["user_id"],
            task_data["title"],
            task_data["template_type"],
            json.dumps(task_data.get("engine_outputs", {})),
            task_data.get("include_charts", False),
            task_data.get("output_format", "markdown"),
            "pending",
            datetime.now(),
            datetime.now()
        )
        
        return task_data["id"]
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task from database"""
        db = await get_db_connection()
        
        task = await db.fetchrow(
            f"SELECT * FROM {self.config.db_table_prefix}tasks WHERE id = $1",
            task_id
        )
        
        if not task:
            return None
        
        task_dict = dict(task)
        
        # Parse JSON fields
        if task_dict.get("engine_outputs"):
            task_dict["engine_outputs"] = json.loads(task_dict["engine_outputs"])
        
        return task_dict
    
    async def update_task_status(self, task_id: str, status: str, error: Optional[str] = None) -> bool:
        """Update task status"""
        db = await get_db_connection()
        
        await db.execute(
            f"""
            UPDATE {self.config.db_table_prefix}tasks 
            SET status = $1, error = $2, updated_at = $3 
            WHERE id = $4
            """,
            status, error, datetime.now(), task_id
        )
        
        return True
    
    async def save_state(self, state_data: Dict[str, Any]) -> bool:
        """Save report state to database"""
        db = await get_db_connection()
        
        await db.execute(
            f"""
            INSERT INTO {self.config.db_table_prefix}states (
                session_id, state_data, created_at, updated_at
            ) VALUES ($1, $2, $3, $3)
            ON CONFLICT (session_id) DO UPDATE SET
                state_data = $2, updated_at = $3
            """,
            state_data["session_id"],
            json.dumps(state_data),
            datetime.now(),
            datetime.now()
        )
        
        return True
    
    async def get_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get report state from database"""
        db = await get_db_connection()
        
        state = await db.fetchrow(
            f"SELECT * FROM {self.config.db_table_prefix}states WHERE session_id = $1",
            session_id
        )
        
        if not state:
            return None
        
        state_dict = dict(state)
        
        # Parse state data
        if state_dict.get("state_data"):
            state_dict["state_data"] = json.loads(state_dict["state_data"])
        
        return state_dict
    
    async def update_state(self, session_id: str, state_data: Dict[str, Any]) -> bool:
        """Update report state"""
        db = await get_db_connection()
        
        await db.execute(
            f"""
            UPDATE {self.config.db_table_prefix}states 
            SET state_data = $1, updated_at = $2 
            WHERE session_id = $3
            """,
            json.dumps(state_data), datetime.now(), session_id
        )
        
        return True
    
    async def save_template(self, template_data: Dict[str, Any]) -> str:
        """Save a template to database"""
        db = await get_db_connection()
        
        template_id = template_data["id"]
        
        await db.execute(f"""
            INSERT INTO {self.config.db_table_prefix}templates (
                id, name, description, category, engine_types, 
                template_data, is_custom, created_at, updated_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8
            )
        """,
            template_id,
            template_data["name"],
            template_data["description"],
            template_data.get("category", "general"),
            json.dumps(template_data.get("engine_types", [])),
            json.dumps(template_data.get("template_data", {})),
            template_data.get("is_custom", False),
            datetime.now(),
            datetime.now()
        )
        
        return template_id
    
    async def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a template from database"""
        db = await get_db_connection()
        
        template = await db.fetchrow(
            f"SELECT * FROM {self.config.db_table_prefix}templates WHERE id = $1",
            template_id
        )
        
        if not template:
            return None
        
        template_dict = dict(template)
        
        # Parse JSON fields
        if template_dict.get("template_data"):
            template_dict["template_data"] = json.loads(template_dict["template_data"])
        
        if template_dict.get("engine_types"):
            template_dict["engine_types"] = json.loads(template_dict["engine_types"])
        
        return template_dict
    
    async def get_templates(self, category: str = "all", engine_type: str = "all") -> List[Dict[str, Any]]:
        """Get templates from database"""
        db = await get_db_connection()
        
        query = f"SELECT * FROM {self.config.db_table_prefix}templates"
        params = []
        
        if category != "all":
            query += " WHERE category = $1"
            params.append(category)
        
        if engine_type != "all":
            if category != "all":
                query += " AND engine_types::jsonb ? $1"
            else:
                query += " WHERE engine_types::jsonb ? $1"
            params.append(engine_type)
        
        templates = await db.fetch(query, *params)
        
        result = []
        for template in templates:
            template_dict = dict(template)
            
            # Parse JSON fields
            if template_dict.get("template_data"):
                template_dict["template_data"] = json.loads(template_dict["template_data"])
            
            if template_dict.get("engine_types"):
                template_dict["engine_types"] = json.loads(template_dict["engine_types"])
            
            result.append(template_dict)
        
        return result
    
    async def save_session(self, session_data: Dict[str, Any]) -> bool:
        """Save a report session"""
        db = await get_db_connection()
        
        await db.execute(f"""
            INSERT INTO {self.config.db_table_prefix}sessions (
                session_id, title, status, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $4)
        """,
            session_data["session_id"],
            session_data["title"],
            "pending",
            datetime.now(),
            datetime.now()
        )
        
        return True
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a report session"""
        db = await get_db_connection()
        
        session = await db.fetchrow(
            f"SELECT * FROM {self.config.db_table_prefix}sessions WHERE session_id = $1",
            session_id
        )
        
        return dict(session) if session else None
    
    async def update_session_status(self, session_id: str, status: str) -> bool:
        """Update session status"""
        db = await get_db_connection()
        
        await db.execute(
            f"""
            UPDATE {self.config.db_table_prefix}sessions 
            SET status = $1, updated_at = $2 
            WHERE session_id = $3
            """,
            status, datetime.now(), session_id
        )
        
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a report session"""
        db = await get_db_connection()
        
        # Delete related records
        await db.execute(f"DELETE FROM {self.config.db_table_prefix}states WHERE session_id = $1", session_id)
        await db.execute(f"DELETE FROM {self.config.db_table_prefix}sessions WHERE session_id = $1", session_id)
        
        return True
    
    async def cleanup_old_records(self, days: int = 30):
        """Clean up old records"""
        db = await get_db_connection()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Clean up old tasks
        await db.execute(
            f"""
            DELETE FROM {self.config.db_table_prefix}tasks 
            WHERE updated_at < $1
            """,
            cutoff_date
        )
        
        # Clean up old states
        await db.execute(
            f"""
            DELETE FROM {self.config.db_table_prefix}states 
            WHERE updated_at < $1
            """,
            cutoff_date
        )
        
        logger.info(f"Cleaned up records older than {days} days")
    
    async def get_user_sessions(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user sessions"""
        db = await get_db_connection()
        
        sessions = await db.fetch(
            f"""
            SELECT session_id, title, status, created_at, updated_at
            FROM {self.config.db_table_prefix}sessions
            WHERE user_id = $1
            ORDER BY updated_at DESC
            LIMIT $2 OFFSET $3
            """,
            user_id, limit, offset
        )
        
        return [dict(session) for session in sessions]
    
    async def get_task_count_by_status(self, status: str) -> int:
        """Get task count by status"""
        db = await get_db_connection()
        
        count = await db.fetchval(
            f"SELECT COUNT(*) FROM {self.config.db_table_prefix}tasks WHERE status = $1",
            status
        )
        
        return count
    
    async def get_session_count(self) -> int:
        """Get total session count"""
        db = await get_db_connection()
        
        count = await db.fetchval(
            f"SELECT COUNT(*) FROM {self.config.db_table_prefix}sessions"
        )
        
        return count
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        db = await get_db_connection()
        
        stats = {}
        
        # Task stats
        stats["tasks"] = {
            "total": await db.fetchval(f"SELECT COUNT(*) FROM {self.config.db_table_prefix}tasks"),
            "by_status": {
                "pending": await self.get_task_count_by_status("pending"),
                "running": await self.get_task_count_by_status("running"),
                "completed": await self.get_task_count_by_status("completed"),
                "failed": await self.get_task_count_by_status("failed")
            }
        }
        
        # Session stats
        stats["sessions"] = {
            "total": await self.get_session_count(),
            "by_status": {
                "pending": await db.fetchval(f"SELECT COUNT(*) FROM {self.config.db_table_prefix}sessions WHERE status = 'pending'"),
                "running": await db.fetchval(f"SELECT COUNT(*) FROM {self.config.db_table_prefix}sessions WHERE status = 'running'"),
                "completed": await db.fetchval(f"SELECT COUNT(*) FROM {self.config.db_table_prefix}sessions WHERE status = 'completed'")
            }
        }
        
        # Template stats
        stats["templates"] = {
            "total": await db.fetchval(f"SELECT COUNT(*) FROM {self.config.db_table_prefix}templates"),
            "custom": await db.fetchval(f"SELECT COUNT(*) FROM {self.config.db_table_prefix}templates WHERE is_custom = TRUE"),
            "builtin": await db.fetchval(f"SELECT COUNT(*) FROM {self.config.db_table_prefix}templates WHERE is_custom = FALSE")
        }
        
        return stats

# Global database manager instance
db_manager = DatabaseManager()
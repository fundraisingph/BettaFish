"""
QueryEngine Database Manager
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from core.database import get_db_connection
from ..utils.config import query_config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for QueryEngine"""
    
    def __init__(self):
        self.config = query_config
    
    async def create_tables(self):
        """Create QueryEngine tables"""
        db = await get_db_connection()
        
        # Create query_tasks table
        await db.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.config.get_db_table_name('tasks')} (
                id VARCHAR(255) PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                query TEXT NOT NULL,
                search_type VARCHAR(50) NOT NULL DEFAULT 'comprehensive',
                max_results INTEGER NOT NULL DEFAULT 10,
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                results JSONB,
                error TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create query_optimization_tasks table
        await db.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.config.get_db_table_name('optimization_tasks')} (
                id VARCHAR(255) PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                query TEXT NOT NULL,
                optimization_type VARCHAR(50) NOT NULL DEFAULT 'keyword',
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                results JSONB,
                error TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create query_research_tasks table
        await db.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.config.get_db_table_name('research_tasks')} (
                id VARCHAR(255) PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                query TEXT NOT NULL,
                research_type VARCHAR(50) NOT NULL DEFAULT 'comprehensive',
                max_iterations INTEGER NOT NULL DEFAULT 3,
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                results JSONB,
                error TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create query_research_states table
        await db.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.config.get_db_table_name('research_states')} (
                session_id VARCHAR(255) PRIMARY KEY,
                state_data JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create indexes
        await db.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.config.get_db_table_name('tasks')}_session_id 
            ON {self.config.get_db_table_name('tasks')} (session_id)
        """)
        
        await db.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.config.get_db_table_name('tasks')}_user_id 
            ON {self.config.get_db_table_name('tasks')} (user_id)
        """)
        
        await db.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.config.get_db_table_name('tasks')}_status 
            ON {self.config.get_db_table_name('tasks')} (status)
        """)
        
        await db.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.config.get_db_table_name('optimization_tasks')}_session_id 
            ON {self.config.get_db_table_name('optimization_tasks')} (session_id)
        """)
        
        await db.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.config.get_db_table_name('optimization_tasks')}_user_id 
            ON {self.config.get_db_table_name('optimization_tasks')} (user_id)
        """)
        
        await db.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.config.get_db_table_name('research_tasks')}_session_id 
            ON {self.config.get_db_table_name('research_tasks')} (session_id)
        """)
        
        await db.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_{self.config.get_db_table_name('research_tasks')}_user_id 
            ON {self.config.get_db_table_name('research_tasks')} (user_id)
        """)
        
        logger.info("QueryEngine database tables created successfully")
    
    async def drop_tables(self):
        """Drop QueryEngine tables"""
        db = await get_db_connection()
        
        await db.execute(f"DROP TABLE IF EXISTS {self.config.get_db_table_name('tasks')}")
        await db.execute(f"DROP TABLE IF EXISTS {self.config.get_db_table_name('optimization_tasks')}")
        await db.execute(f"DROP TABLE IF EXISTS {self.config.get_db_table_name('research_tasks')}")
        await db.execute(f"DROP TABLE IF EXISTS {self.config.get_db_table_name('research_states')}")
        
        logger.info("QueryEngine database tables dropped successfully")
    
    async def save_task(self, task_data: Dict[str, Any]) -> str:
        """Save a task to database"""
        db = await get_db_connection()
        
        # Determine table based on task type
        if task_data.get('optimization_type'):
            table_name = self.config.get_db_table_name('optimization_tasks')
        elif task_data.get('research_type'):
            table_name = self.config.get_db_table_name('research_tasks')
        else:
            table_name = self.config.get_db_table_name('tasks')
        
        await db.execute(f"""
            INSERT INTO {table_name} (
                id, session_id, user_id, query, search_type, max_results, 
                optimization_type, research_type, max_iterations, 
                status, results, error, created_at, updated_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $13
            )
            ON CONFLICT (id) DO UPDATE SET
                session_id = $2, user_id = $3, query = $4, search_type = $5, max_results = $6,
                optimization_type = $7, research_type = $8, max_iterations = $9,
                status = $10, results = $11, error = $12, updated_at = $13
        """, 
            task_data.get('id'),
            task_data.get('session_id'),
            task_data.get('user_id'),
            task_data.get('query'),
            task_data.get('search_type'),
            task_data.get('max_results'),
            task_data.get('optimization_type'),
            task_data.get('research_type'),
            task_data.get('max_iterations'),
            task_data.get('status'),
            json.dumps(task_data.get('results')) if task_data.get('results') else None,
            task_data.get('error'),
            datetime.now()
        )
        
        return task_data.get('id')
    
    async def get_task(self, task_id: str, task_type: str = 'search') -> Optional[Dict[str, Any]]:
        """Get a task from database"""
        db = await get_db_connection()
        
        # Determine table based on task type
        if task_type == 'optimization':
            table_name = self.config.get_db_table_name('optimization_tasks')
        elif task_type == 'research':
            table_name = self.config.get_db_table_name('research_tasks')
        else:
            table_name = self.config.get_db_table_name('tasks')
        
        task = await db.fetchrow(f"""
            SELECT * FROM {table_name} WHERE id = $1
        """, task_id)
        
        if task:
            task_dict = dict(task)
            # Parse JSON fields
            if task_dict.get('results'):
                task_dict['results'] = json.loads(task_dict['results'])
            return task_dict
        
        return None
    
    async def update_task_status(self, task_id: str, status: str, task_type: str = 'search', 
                               results: Optional[Dict[str, Any]] = None, 
                               error: Optional[str] = None) -> bool:
        """Update task status"""
        db = await get_db_connection()
        
        # Determine table based on task type
        if task_type == 'optimization':
            table_name = self.config.get_db_table_name('optimization_tasks')
        elif task_type == 'research':
            table_name = self.config.get_db_table_name('research_tasks')
        else:
            table_name = self.config.get_db_table_name('tasks')
        
        await db.execute(f"""
            UPDATE {table_name} 
            SET status = $1, results = $2, error = $3, updated_at = $4
            WHERE id = $5
        """, 
            status,
            json.dumps(results) if results else None,
            error,
            datetime.now(),
            task_id
        )
        
        return True
    
    async def get_user_tasks(self, user_id: str, task_type: str = 'search', 
                           limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get tasks for a user"""
        db = await get_db_connection()
        
        # Determine table based on task type
        if task_type == 'optimization':
            table_name = self.config.get_db_table_name('optimization_tasks')
        elif task_type == 'research':
            table_name = self.config.get_db_table_name('research_tasks')
        else:
            table_name = self.config.get_db_table_name('tasks')
        
        tasks = await db.fetch(f"""
            SELECT * FROM {table_name} 
            WHERE user_id = $1 
            ORDER BY updated_at DESC 
            LIMIT $2 OFFSET $3
        """, user_id, limit, offset)
        
        result = []
        for task in tasks:
            task_dict = dict(task)
            # Parse JSON fields
            if task_dict.get('results'):
                task_dict['results'] = json.loads(task_dict['results'])
            result.append(task_dict)
        
        return result
    
    async def get_session_tasks(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a session"""
        db = await get_db_connection()
        
        tasks = []
        
        # Get search tasks
        search_tasks = await db.fetch(f"""
            SELECT * FROM {self.config.get_db_table_name('tasks')} 
            WHERE session_id = $1 
            ORDER BY created_at ASC
        """, session_id)
        
        for task in search_tasks:
            task_dict = dict(task)
            task_dict['task_type'] = 'search'
            if task_dict.get('results'):
                task_dict['results'] = json.loads(task_dict['results'])
            tasks.append(task_dict)
        
        # Get optimization tasks
        optimization_tasks = await db.fetch(f"""
            SELECT * FROM {self.config.get_db_table_name('optimization_tasks')} 
            WHERE session_id = $1 
            ORDER BY created_at ASC
        """, session_id)
        
        for task in optimization_tasks:
            task_dict = dict(task)
            task_dict['task_type'] = 'optimization'
            if task_dict.get('results'):
                task_dict['results'] = json.loads(task_dict['results'])
            tasks.append(task_dict)
        
        # Get research tasks
        research_tasks = await db.fetch(f"""
            SELECT * FROM {self.config.get_db_table_name('research_tasks')} 
            WHERE session_id = $1 
            ORDER BY created_at ASC
        """, session_id)
        
        for task in research_tasks:
            task_dict = dict(task)
            task_dict['task_type'] = 'research'
            if task_dict.get('results'):
                task_dict['results'] = json.loads(task_dict['results'])
            tasks.append(task_dict)
        
        # Sort by creation time
        tasks.sort(key=lambda x: x['created_at'])
        
        return tasks
    
    async def save_research_state(self, session_id: str, state_data: Dict[str, Any]) -> bool:
        """Save research state"""
        db = await get_db_connection()
        
        await db.execute(f"""
            INSERT INTO {self.config.get_db_table_name('research_states')} 
            (session_id, state_data, created_at, updated_at)
            VALUES ($1, $2, $3, $3)
            ON CONFLICT (session_id) DO UPDATE SET
                state_data = $2, updated_at = $3
        """, 
            session_id, 
            json.dumps(state_data), 
            datetime.now()
        )
        
        return True
    
    async def get_research_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get research state"""
        db = await get_db_connection()
        
        state = await db.fetchrow(f"""
            SELECT * FROM {self.config.get_db_table_name('research_states')} 
            WHERE session_id = $1
        """, session_id)
        
        if state:
            state_dict = dict(state)
            # Parse JSON fields
            if state_dict.get('state_data'):
                state_dict['state_data'] = json.loads(state_dict['state_data'])
            return state_dict
        
        return None
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete all data for a session"""
        db = await get_db_connection()
        
        # Delete from all tables
        await db.execute(f"""
            DELETE FROM {self.config.get_db_table_name('tasks')} 
            WHERE session_id = $1
        """, session_id)
        
        await db.execute(f"""
            DELETE FROM {self.config.get_db_table_name('optimization_tasks')} 
            WHERE session_id = $1
        """, session_id)
        
        await db.execute(f"""
            DELETE FROM {self.config.get_db_table_name('research_tasks')} 
            WHERE session_id = $1
        """, session_id)
        
        await db.execute(f"""
            DELETE FROM {self.config.get_db_table_name('research_states')} 
            WHERE session_id = $1
        """, session_id)
        
        return True
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        db = await get_db_connection()
        
        sessions = await db.fetch(f"""
            SELECT DISTINCT session_id, query, status, created_at, updated_at
            FROM {self.config.get_db_table_name('research_tasks')}
            WHERE user_id = $1
            ORDER BY updated_at DESC
        """, user_id)
        
        return [dict(session) for session in sessions]

# Global database manager instance
db_manager = DatabaseManager()
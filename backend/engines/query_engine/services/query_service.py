"""
QueryEngine Service Implementation
"""
import json
import uuid
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

from core.database import get_db_connection
from api.websocket import manager
from ..models.schemas import (
    QuerySearchRequest,
    QuerySearchResponse,
    QueryOptimizeRequest,
    QueryOptimizeResponse,
    QueryResearchRequest,
    QueryResearchResponse,
    ProgressResponse,
    QuerySearchResult,
    QueryOptimizationResult,
    QueryResearchResult
)
from ..state.state import ResearchState
from ..nodes.search_node import SearchNode
from ..nodes.summary_node import SummaryNode
from ..nodes.report_structure_node import ReportStructureNode
from ..nodes.formatting_node import FormattingNode
from ..llms.base import LLMClient
from ..utils.config import QueryEngineConfig

class QueryService:
    """Service for handling query operations"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.config = QueryEngineConfig()
    
    async def create_search_task(
        self,
        session_id: str,
        user_id: str,
        query: str,
        search_type: str = "comprehensive",
        max_results: int = 10
    ) -> str:
        """Create a search task"""
        task_id = str(uuid.uuid4())
        
        # Save task to database
        db = await get_db_connection()
        await db.execute(
            """
            INSERT INTO query_tasks (id, session_id, user_id, query, search_type, max_results, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8)
            """,
            task_id, session_id, user_id, query, search_type, max_results, "pending", datetime.now()
        )
        
        return task_id
    
    async def execute_search(self, task_id: str) -> Dict[str, Any]:
        """Execute search task"""
        db = await get_db_connection()
        
        # Get task details
        task = await db.fetchrow(
            "SELECT * FROM query_tasks WHERE id = $1",
            task_id
        )
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update task status
        await db.execute(
            "UPDATE query_tasks SET status = $1, updated_at = $2 WHERE id = $3",
            "running", datetime.now(), task_id
        )
        
        try:
            # Create search node
            search_node = SearchNode(self.llm_client)
            
            # Execute search
            results = await search_node.run(
                query=task["query"],
                search_type=task["search_type"],
                max_results=task["max_results"]
            )
            
            # Update task status
            await db.execute(
                "UPDATE query_tasks SET status = $1, updated_at = $2, results = $3 WHERE id = $4",
                "completed", datetime.now(), json.dumps(results), task_id
            )
            
            return results
            
        except Exception as e:
            # Update task status with error
            await db.execute(
                "UPDATE query_tasks SET status = $1, updated_at = $2, error = $3 WHERE id = $4",
                "failed", datetime.now(), str(e), task_id
            )
            raise
    
    async def create_optimize_task(
        self,
        session_id: str,
        user_id: str,
        query: str,
        optimization_type: str = "keyword"
    ) -> str:
        """Create an optimization task"""
        task_id = str(uuid.uuid4())
        
        # Save task to database
        db = await get_db_connection()
        await db.execute(
            """
            INSERT INTO query_optimization_tasks (id, session_id, user_id, query, optimization_type, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $7)
            """,
            task_id, session_id, user_id, query, optimization_type, "pending", datetime.now()
        )
        
        return task_id
    
    async def execute_optimize(self, task_id: str) -> Dict[str, Any]:
        """Execute optimization task"""
        db = await get_db_connection()
        
        # Get task details
        task = await db.fetchrow(
            "SELECT * FROM query_optimization_tasks WHERE id = $1",
            task_id
        )
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update task status
        await db.execute(
            "UPDATE query_optimization_tasks SET status = $1, updated_at = $2 WHERE id = $3",
            "running", datetime.now(), task_id
        )
        
        try:
            # Import keyword optimizer
            from ..tools.keyword_optimizer import KeywordOptimizer
            
            # Create optimizer
            optimizer = KeywordOptimizer(self.llm_client)
            
            # Execute optimization
            results = await optimizer.optimize_query(
                query=task["query"],
                optimization_type=task["optimization_type"]
            )
            
            # Update task status
            await db.execute(
                "UPDATE query_optimization_tasks SET status = $1, updated_at = $2, results = $3 WHERE id = $4",
                "completed", datetime.now(), json.dumps(results), task_id
            )
            
            return results
            
        except Exception as e:
            # Update task status with error
            await db.execute(
                "UPDATE query_optimization_tasks SET status = $1, updated_at = $2, error = $3 WHERE id = $4",
                "failed", datetime.now(), str(e), task_id
            )
            raise
    
    async def create_research_task(
        self,
        session_id: str,
        user_id: str,
        query: str,
        research_type: str = "comprehensive",
        max_iterations: int = 3
    ) -> str:
        """Create a research task"""
        task_id = str(uuid.uuid4())
        
        # Save task to database
        db = await get_db_connection()
        await db.execute(
            """
            INSERT INTO query_research_tasks (id, session_id, user_id, query, research_type, max_iterations, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8)
            """,
            task_id, session_id, user_id, query, research_type, max_iterations, "pending", datetime.now()
        )
        
        return task_id
    
    async def execute_research(self, task_id: str, session_id: str):
        """Execute research task in background"""
        db = await get_db_connection()
        
        # Get task details
        task = await db.fetchrow(
            "SELECT * FROM query_research_tasks WHERE id = $1",
            task_id
        )
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update task status
        await db.execute(
            "UPDATE query_research_tasks SET status = $1, updated_at = $2 WHERE id = $3",
            "running", datetime.now(), task_id
        )
        
        try:
            # Create research state
            state = ResearchState(
                session_id=session_id,
                query=task["query"],
                research_type=task["research_type"],
                max_iterations=task["max_iterations"]
            )
            
            # Save initial state
            await db.execute(
                """
                INSERT INTO query_research_states (session_id, state_data, created_at, updated_at)
                VALUES ($1, $2, $3, $3)
                ON CONFLICT (session_id) DO UPDATE SET
                state_data = $2, updated_at = $3
                """,
                session_id, json.dumps(state.to_dict()), datetime.now()
            )
            
            # Execute research iterations
            for iteration in range(task["max_iterations"]):
                # Update progress
                progress = {
                    "task_id": task_id,
                    "session_id": session_id,
                    "status": "running",
                    "current_iteration": iteration + 1,
                    "total_iterations": task["max_iterations"],
                    "message": f"Executing research iteration {iteration + 1}/{task['max_iterations']}"
                }
                
                await manager.broadcast(
                    json.dumps(progress),
                    f"query_research_{session_id}"
                )
                
                # Execute search
                search_node = SearchNode(self.llm_client)
                search_results = await search_node.run(
                    query=state.query,
                    search_type="comprehensive",
                    max_results=20
                )
                
                # Execute summary
                summary_node = SummaryNode(self.llm_client)
                summary = await summary_node.run(
                    query=state.query,
                    search_results=search_results,
                    iteration=iteration + 1
                )
                
                # Update state
                state.add_iteration_results(search_results, summary)
                
                # Save state
                await db.execute(
                    """
                    UPDATE query_research_states
                    SET state_data = $1, updated_at = $2
                    WHERE session_id = $3
                    """,
                    json.dumps(state.to_dict()), datetime.now(), session_id
                )
                
                # Check if we should continue
                if iteration < task["max_iterations"] - 1:
                    # Reflection step
                    reflection_query = f"Based on the research so far: {summary}, what additional aspects should be investigated for: {state.query}?"
                    reflection_search = await search_node.run(
                        query=reflection_query,
                        search_type="targeted",
                        max_results=10
                    )
                    
                    # Update query for next iteration
                    state.query = f"{state.query} (additional focus: {reflection_query})"
            
            # Generate final report
            report_structure_node = ReportStructureNode(self.llm_client)
            report_structure = await report_structure_node.run(
                query=task["query"],
                research_results=state.get_all_results()
            )
            
            # Generate formatted report
            formatting_node = FormattingNode(self.llm_client)
            formatted_report = await formatting_node.run(
                report_structure=report_structure,
                research_results=state.get_all_results()
            )
            
            # Update task status
            await db.execute(
                """
                UPDATE query_research_tasks
                SET status = $1, updated_at = $2, results = $3
                WHERE id = $4
                """,
                "completed", datetime.now(), json.dumps({
                    "report_structure": report_structure,
                    "formatted_report": formatted_report,
                    "iterations": state.iterations
                }), task_id
            )
            
            # Final progress update
            final_progress = {
                "task_id": task_id,
                "session_id": session_id,
                "status": "completed",
                "current_iteration": task["max_iterations"],
                "total_iterations": task["max_iterations"],
                "message": "Research completed successfully",
                "results": {
                    "report_structure": report_structure,
                    "formatted_report": formatted_report
                }
            }
            
            await manager.broadcast(
                json.dumps(final_progress),
                f"query_research_{session_id}"
            )
            
        except Exception as e:
            # Update task status with error
            await db.execute(
                "UPDATE query_research_tasks SET status = $1, updated_at = $2, error = $3 WHERE id = $4",
                "failed", datetime.now(), str(e), task_id
            )
            
            # Broadcast error
            error_progress = {
                "task_id": task_id,
                "session_id": session_id,
                "status": "failed",
                "message": f"Research failed: {str(e)}"
            }
            
            await manager.broadcast(
                json.dumps(error_progress),
                f"query_research_{session_id}"
            )
    
    async def get_task_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get task status for a session"""
        db = await get_db_connection()
        
        # Get research task
        task = await db.fetchrow(
            """
            SELECT * FROM query_research_tasks
            WHERE session_id = $1
            ORDER BY created_at DESC
            LIMIT 1
            """,
            session_id
        )
        
        if not task:
            return None
        
        # Get state
        state = await db.fetchrow(
            "SELECT * FROM query_research_states WHERE session_id = $1",
            session_id
        )
        
        return {
            "task": dict(task),
            "state": dict(state) if state else None
        }
    
    async def stream_progress(self, session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream progress updates"""
        # Get initial status
        status = await self.get_task_status(session_id)
        if status:
            yield status
        
        # In a real implementation, you would subscribe to updates
        # For now, we'll poll the database
        import asyncio
        
        while True:
            await asyncio.sleep(1)
            
            new_status = await self.get_task_status(session_id)
            if new_status and new_status != status:
                status = new_status
                yield status
                
                # Stop if completed or failed
                if status["task"]["status"] in ["completed", "failed"]:
                    break
    
    async def get_progress(self, session_id: str) -> Optional[ProgressResponse]:
        """Get current progress for a session"""
        status = await self.get_task_status(session_id)
        
        if not status:
            return None
        
        task = status["task"]
        state = status["state"]
        
        # Parse state data if available
        state_data = {}
        if state and state["state_data"]:
            state_data = json.loads(state["state_data"])
        
        return ProgressResponse(
            session_id=session_id,
            task_id=task["id"],
            status=task["status"],
            current_iteration=state_data.get("current_iteration", 0) if state_data else 0,
            total_iterations=task.get("max_iterations", 0),
            message=f"Query research {task['status']}",
            created_at=task["created_at"],
            updated_at=task["updated_at"]
        )
    
    async def verify_session_ownership(self, session_id: str, user_id: str) -> bool:
        """Verify that a session belongs to the current user"""
        db = await get_db_connection()
        
        # Check research task
        result = await db.fetchval(
            """
            SELECT COUNT(*) FROM query_research_tasks
            WHERE session_id = $1 AND user_id = $2
            """,
            session_id, user_id
        )
        
        return result > 0
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a research session"""
        db = await get_db_connection()
        
        # Delete related records
        await db.execute("DELETE FROM query_research_states WHERE session_id = $1", session_id)
        await db.execute("DELETE FROM query_research_tasks WHERE session_id = $1", session_id)
        await db.execute("DELETE FROM query_tasks WHERE session_id = $1", session_id)
        await db.execute("DELETE FROM query_optimization_tasks WHERE session_id = $1", session_id)
        
        return True
    
    async def list_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """List all sessions for a user"""
        db = await get_db_connection()
        
        sessions = await db.fetch(
            """
            SELECT DISTINCT session_id, query, status, created_at, updated_at
            FROM query_research_tasks
            WHERE user_id = $1
            ORDER BY updated_at DESC
            """,
            user_id
        )
        
        return [dict(session) for session in sessions]
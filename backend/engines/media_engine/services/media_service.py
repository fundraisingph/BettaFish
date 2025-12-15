"""
MediaEngine Service
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncGenerator

from api.websocket import manager
from core.database import get_db_connection
from ..agent import DeepSearchAgent
from ..state.state import State as ResearchState
from ..models.schemas import ProgressResponse

class MediaService:
    """Service for managing MediaEngine operations"""
    
    def __init__(self):
        self.active_tasks: Dict[str, Dict] = {}
        self.agent = None
    
    async def create_search_task(
        self,
        session_id: str,
        user_id: int,
        query: str,
        search_type: str = "multimodal",
        time_range: Optional[str] = None,
        max_results: int = 10
    ) -> str:
        """Create a new media search task"""
        task_id = str(uuid.uuid4())
        
        # Store task info
        self.active_tasks[task_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "query": query,
            "search_type": search_type,
            "time_range": time_range,
            "max_results": max_results,
            "status": "created",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        return task_id
    
    async def execute_search(self, task_id: str) -> Dict[str, Any]:
        """Execute a media search task"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.active_tasks[task_id]
        task["status"] = "running"
        task["updated_at"] = datetime.now()
        
        try:
            # Initialize agent if not already done
            if not self.agent:
                self.agent = DeepSearchAgent()
            
            # Execute search
            search_results = await self._perform_media_search(
                query=task["query"],
                search_type=task["search_type"],
                time_range=task["time_range"],
                max_results=task["max_results"]
            )
            
            # Update task status
            task["status"] = "completed"
            task["updated_at"] = datetime.now()
            task["results"] = search_results
            
            return search_results
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            task["updated_at"] = datetime.now()
            raise e
    
    async def create_analysis_task(
        self,
        session_id: str,
        user_id: int,
        content: Dict[str, Any],
        analysis_type: str = "multimodal"
    ) -> str:
        """Create a new media analysis task"""
        task_id = str(uuid.uuid4())
        
        # Store task info
        self.active_tasks[task_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "content": content,
            "analysis_type": analysis_type,
            "status": "created",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        return task_id
    
    async def execute_analysis(self, task_id: str) -> Dict[str, Any]:
        """Execute a media analysis task"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.active_tasks[task_id]
        task["status"] = "running"
        task["updated_at"] = datetime.now()
        
        try:
            # Initialize agent if not already done
            if not self.agent:
                self.agent = DeepSearchAgent()
            
            # Execute analysis
            analysis_results = await self._perform_media_analysis(
                content=task["content"],
                analysis_type=task["analysis_type"]
            )
            
            # Update task status
            task["status"] = "completed"
            task["updated_at"] = datetime.now()
            task["results"] = analysis_results
            
            return analysis_results
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            task["updated_at"] = datetime.now()
            raise e
    
    async def create_research_task(
        self,
        session_id: str,
        user_id: int,
        query: str,
        research_type: str = "comprehensive",
        max_iterations: int = 3
    ) -> str:
        """Create a new media research task"""
        task_id = str(uuid.uuid4())
        
        # Store task info
        self.active_tasks[task_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "query": query,
            "research_type": research_type,
            "max_iterations": max_iterations,
            "status": "created",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        return task_id
    
    async def execute_research(self, task_id: str, session_id: str):
        """Execute a media research task in the background"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.active_tasks[task_id]
        task["status"] = "running"
        task["updated_at"] = datetime.now()
        
        try:
            # Initialize agent if not already done
            if not self.agent:
                self.agent = DeepSearchAgent()
            
            # Create research state
            research_state = ResearchState(
                session_id=session_id,
                query=task["query"],
                max_iterations=task["max_iterations"]
            )
            
            # Execute research iterations
            for iteration in range(task["max_iterations"]):
                # Update progress
                progress = ProgressResponse(
                    session_id=session_id,
                    task_id=task_id,
                    status="running",
                    progress=(iteration + 1) / task["max_iterations"] * 100,
                    message=f"Research iteration {iteration + 1}/{task['max_iterations']}",
                    created_at=task["created_at"],
                    updated_at=datetime.now()
                )
                
                # Broadcast progress via WebSocket
                await manager.broadcast(
                    json.dumps(progress.dict()),
                    session_id
                )
                
                # Perform research iteration
                await self._perform_research_iteration(
                    research_state,
                    iteration
                )
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(1)
            
            # Final update
            task["status"] = "completed"
            task["updated_at"] = datetime.now()
            task["results"] = research_state.to_dict()
            
            # Final progress update
            final_progress = ProgressResponse(
                session_id=session_id,
                task_id=task_id,
                status="completed",
                progress=100,
                message="Research completed successfully",
                created_at=task["created_at"],
                updated_at=datetime.now()
            )
            
            await manager.broadcast(
                json.dumps(final_progress.dict()),
                session_id
            )
            
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            task["updated_at"] = datetime.now()
            
            # Error progress update
            error_progress = ProgressResponse(
                session_id=session_id,
                task_id=task_id,
                status="failed",
                progress=0,
                message=f"Research failed: {str(e)}",
                created_at=task["created_at"],
                updated_at=datetime.now()
            )
            
            await manager.broadcast(
                json.dumps(error_progress.dict()),
                session_id
            )
    
    async def stream_progress(self, session_id: str) -> AsyncGenerator[ProgressResponse, None]:
        """Stream progress updates for a session"""
        # Find active task for this session
        task_id = None
        for tid, task in self.active_tasks.items():
            if task["session_id"] == session_id and task["status"] in ["created", "running"]:
                task_id = tid
                break
        
        if not task_id:
            yield ProgressResponse(
                session_id=session_id,
                task_id="",
                status="not_found",
                progress=0,
                message="No active task found for this session",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            return
        
        # Stream progress updates
        while task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            
            progress = ProgressResponse(
                session_id=session_id,
                task_id=task_id,
                status=task["status"],
                progress=self._calculate_progress(task),
                message=self._get_status_message(task),
                created_at=task["created_at"],
                updated_at=task["updated_at"]
            )
            
            yield progress
            
            # If task is completed or failed, stop streaming
            if task["status"] in ["completed", "failed"]:
                break
            
            # Wait before next update
            await asyncio.sleep(1)
    
    async def get_task_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get task status for a session"""
        for task_id, task in self.active_tasks.items():
            if task["session_id"] == session_id:
                return task
        return None
    
    async def get_progress(self, session_id: str) -> Optional[ProgressResponse]:
        """Get current progress for a session"""
        task = await self.get_task_status(session_id)
        if not task:
            return None
        
        return ProgressResponse(
            session_id=session_id,
            task_id=task.get("task_id", ""),
            status=task["status"],
            progress=self._calculate_progress(task),
            message=self._get_status_message(task),
            created_at=task["created_at"],
            updated_at=task["updated_at"]
        )
    
    async def verify_session_ownership(self, session_id: str, user_id: int) -> bool:
        """Verify that a session belongs to a user"""
        for task in self.active_tasks.values():
            if task["session_id"] == session_id and task["user_id"] == user_id:
                return True
        return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and its associated tasks"""
        tasks_to_delete = []
        for task_id, task in self.active_tasks.items():
            if task["session_id"] == session_id:
                tasks_to_delete.append(task_id)
        
        for task_id in tasks_to_delete:
            del self.active_tasks[task_id]
        
        return len(tasks_to_delete) > 0
    
    async def list_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """List all sessions for a user"""
        sessions = {}
        for task in self.active_tasks.values():
            if task["user_id"] == user_id:
                session_id = task["session_id"]
                if session_id not in sessions:
                    sessions[session_id] = {
                        "session_id": session_id,
                        "created_at": task["created_at"],
                        "updated_at": task["updated_at"],
                        "status": task["status"],
                        "tasks": []
                    }
                sessions[session_id]["tasks"].append({
                    "task_id": task.get("task_id", ""),
                    "type": task.get("search_type", task.get("analysis_type", task.get("research_type", "unknown"))),
                    "status": task["status"],
                    "created_at": task["created_at"]
                })
        
        return list(sessions.values())
    
    # Helper methods
    async def _perform_media_search(
        self,
        query: str,
        search_type: str,
        time_range: Optional[str],
        max_results: int
    ) -> Dict[str, Any]:
        """Perform media search"""
        # This would integrate with the actual MediaEngine search functionality
        # For now, return a mock response
        return {
            "query": query,
            "search_type": search_type,
            "time_range": time_range,
            "max_results": max_results,
            "results": [
                {
                    "id": "1",
                    "title": f"Search result for: {query}",
                    "content": "Mock search content",
                    "source": "web",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    async def _perform_media_analysis(
        self,
        content: Dict[str, Any],
        analysis_type: str
    ) -> Dict[str, Any]:
        """Perform media analysis"""
        # This would integrate with the actual MediaEngine analysis functionality
        # For now, return a mock response
        return {
            "content": content,
            "analysis_type": analysis_type,
            "results": {
                "sentiment": "positive",
                "topics": ["technology", "innovation"],
                "confidence": 0.85
            }
        }
    
    async def _perform_research_iteration(
        self,
        research_state: ResearchState,
        iteration: int
    ):
        """Perform a single research iteration"""
        # This would integrate with the actual MediaEngine research functionality
        # For now, just update the state
        research_state.add_iteration_result(
            iteration=iteration,
            data={"mock": f"research_iteration_{iteration}"}
        )
    
    def _calculate_progress(self, task: Dict[str, Any]) -> float:
        """Calculate progress percentage for a task"""
        if task["status"] == "completed":
            return 100.0
        elif task["status"] == "failed":
            return 0.0
        elif task["status"] == "running":
            # Estimate progress based on task type
            if "max_iterations" in task:
                # Research task with iterations
                current_iteration = task.get("current_iteration", 0)
                return (current_iteration / task["max_iterations"]) * 100
            else:
                # Simple running task, estimate 50%
                return 50.0
        else:
            return 0.0
    
    def _get_status_message(self, task: Dict[str, Any]) -> str:
        """Get status message for a task"""
        if task["status"] == "completed":
            return "Task completed successfully"
        elif task["status"] == "failed":
            return f"Task failed: {task.get('error', 'Unknown error')}"
        elif task["status"] == "running":
            if "max_iterations" in task:
                current_iteration = task.get("current_iteration", 0)
                return f"Research iteration {current_iteration + 1}/{task['max_iterations']}"
            else:
                return "Task in progress..."
        else:
            return "Task created"
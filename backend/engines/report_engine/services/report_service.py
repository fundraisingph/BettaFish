"""
ReportEngine Service Implementation
"""
import json
import uuid
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

from core.database import get_db_connection
from api.websocket import manager
from ..models.schemas import (
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportTemplateRequest,
    ReportTemplateResponse,
    ReportStreamRequest,
    ProgressResponse
)
from ..state.state import ReportState
from ..llms.base import LLMClient
from ..utils.config import report_config

class ReportService:
    """Service for handling report operations"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.config = report_config
    
    async def create_report_task(
        self,
        session_id: str,
        user_id: str,
        title: str,
        template_type: str = "comprehensive",
        engine_outputs: Dict[str, Any] = None,
        include_charts: bool = False,
        output_format: str = "markdown"
    ) -> str:
        """Create a report generation task"""
        task_id = str(uuid.uuid4())
        
        # Save task to database
        db = await get_db_connection()
        await db.execute(
            """
            INSERT INTO report_tasks (id, session_id, user_id, title, template_type, 
            engine_outputs, include_charts, output_format, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $9)
            """,
            task_id, session_id, user_id, title, template_type,
            json.dumps(engine_outputs) if engine_outputs else None,
            include_charts, output_format, "pending", datetime.now(), datetime.now()
        )
        
        return task_id
    
    async def execute_report_generation(self, task_id: str, session_id: str):
        """Execute report generation in background"""
        db = await get_db_connection()
        
        # Get task details
        task = await db.fetchrow(
            "SELECT * FROM report_tasks WHERE id = $1",
            task_id
        )
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update task status
        await db.execute(
            "UPDATE report_tasks SET status = $1, updated_at = $2 WHERE id = $3",
            "running", datetime.now(), task_id
        )
        
        try:
            # Create report state
            state = ReportState(
                session_id=session_id,
                title=task["title"],
                template_type=task["template_type"],
                engine_outputs=json.loads(task["engine_outputs"]) if task["engine_outputs"] else {},
                include_charts=task["include_charts"],
                output_format=task["output_format"]
            )
            
            # Save initial state
            await db.execute(
                """
                INSERT INTO report_states (session_id, state_data, created_at, updated_at)
                VALUES ($1, $2, $3, $3)
                ON CONFLICT (session_id) DO UPDATE SET
                state_data = $2, updated_at = $3
                """,
                session_id, json.dumps(state.to_dict()), datetime.now(), datetime.now()
            )
            
            # Execute report generation steps
            await self._execute_report_steps(state, task_id)
            
            # Update task status
            await db.execute(
                "UPDATE report_tasks SET status = $1, updated_at = $2 WHERE id = $3",
                "completed", datetime.now(), task_id
            )
            
        except Exception as e:
            # Update task status with error
            await db.execute(
                "UPDATE report_tasks SET status = $1, error = $2, updated_at = $3 WHERE id = $4",
                "failed", str(e), datetime.now(), task_id
            )
            
            # Broadcast error
            error_progress = {
                "task_id": task_id,
                "session_id": session_id,
                "status": "failed",
                "message": f"Report generation failed: {str(e)}"
            }
            
            await manager.broadcast(
                json.dumps(error_progress),
                f"report_generation_{session_id}"
            )
    
    async def _execute_report_steps(self, state: ReportState, task_id: str):
        """Execute the report generation steps"""
        # Step 1: Collect engine outputs
        await self._collect_engine_outputs(state)
        
        # Step 2: Generate report structure
        await self._generate_report_structure(state)
        
        # Step 3: Generate report content
        await self._generate_report_content(state)
        
        # Step 4: Apply formatting
        await self._apply_formatting(state)
        
        # Step 5: Generate charts if requested
        if state.include_charts:
            await self._generate_charts(state)
        
        # Update final state
        await self._save_report_state(state)
    
    async def _collect_engine_outputs(self, state: ReportState):
        """Collect outputs from all engines"""
        # Broadcast progress
        await self._broadcast_progress(
            state.session_id,
            "collecting_engine_outputs",
            "Collecting outputs from InsightEngine, MediaEngine, and QueryEngine...",
            10
        )
        
        # In a real implementation, this would fetch outputs from all engines
        # For now, we'll use placeholder data
        engine_outputs = {
            "insight": {
                "summary": "InsightEngine analysis summary placeholder",
                "insights": ["Insight 1", "Insight 2", "Insight 3"]
            },
            "media": {
                "summary": "MediaEngine analysis summary placeholder",
                "insights": ["Media Insight 1", "Media Insight 2"]
            },
            "query": {
                "summary": "QueryEngine analysis summary placeholder",
                "insights": ["Query Insight 1", "Query Insight 2"]
            }
        }
        
        state.set_engine_outputs(engine_outputs)
        await self._save_report_state(state)
    
    async def _generate_report_structure(self, state: ReportState):
        """Generate report structure"""
        # Broadcast progress
        await self._broadcast_progress(
            state.session_id,
            "generating_structure",
            "Generating report structure...",
            30
        )
        
        # Import report structure node
        from ..nodes.report_structure_node import ReportStructureNode
        
        # Create structure node
        structure_node = ReportStructureNode(self.llm_client)
        
        # Generate structure
        structure = await structure_node.run_with_template(
            query=state.title,
            research_results=[],
            template_type=state.template_type
        )
        
        state.set_report_structure(structure)
        await self._save_report_state(state)
    
    async def _generate_report_content(self, state: ReportState):
        """Generate report content"""
        # Broadcast progress
        await self._broadcast_progress(
            state.session_id,
            "generating_content",
            "Generating report content...",
            50
        )
        
        # Import formatting node
        from ..nodes.formatting_node import FormattingNode
        
        # Create formatting node
        formatting_node = FormattingNode(self.llm_client)
        
        # Generate formatted content
        content = await formatting_node.run(
            report_structure=state.report_structure,
            research_results=state.engine_outputs
        )
        
        state.set_report_content(content)
        await self._save_report_state(state)
    
    async def _apply_formatting(self, state: ReportState):
        """Apply formatting to the report"""
        # Broadcast progress
        await self._broadcast_progress(
            state.session_id,
            "applying_formatting",
            "Applying formatting...",
            70
        )
        
        # Apply format-specific processing
        if state.output_format == "html":
            await self._apply_html_formatting(state)
        elif state.output_format == "pdf":
            await self._apply_pdf_formatting(state)
        
        await self._save_report_state(state)
    
    async def _apply_html_formatting(self, state: ReportState):
        """Apply HTML formatting"""
        from ..nodes.formatting_node import FormattingNode
        
        formatting_node = FormattingNode(self.llm_client)
        html_content = await formatting_node._convert_to_html(state.report_content)
        
        state.set_html_content(html_content)
        await self._save_report_state(state)
    
    async def _apply_pdf_formatting(self, state: ReportState):
        """Apply PDF formatting"""
        from ..nodes.formatting_node import FormattingNode
        
        formatting_node = FormattingNode(self.llm_client)
        pdf_content = await formatting_node._convert_to_pdf(state.report_content)
        
        state.set_pdf_content(pdf_content)
        await self._save_report_state(state)
    
    async def _generate_charts(self, state: ReportState):
        """Generate charts for the report"""
        # Broadcast progress
        await self._broadcast_progress(
            state.session_id,
            "generating_charts",
            "Generating charts...",
            90
        )
        
        # In a real implementation, this would generate actual charts
        # For now, we'll use placeholder data
        charts = {
            "sentiment_chart": {
                "type": "pie",
                "data": {"Positive": 60, "Neutral": 30, "Negative": 10}
            },
            "timeline_chart": {
                "type": "line",
                "data": {"labels": ["Day 1", "Day 2", "Day 3"], "values": [10, 25, 40]}
            }
        }
        
        state.set_charts(charts)
        await self._save_report_state(state)
    
    async def _save_report_state(self, state: ReportState):
        """Save report state to database"""
        db = await get_db_connection()
        await db.execute(
            """
            UPDATE report_states 
            SET state_data = $1, updated_at = $2
            WHERE session_id = $3
            """,
            json.dumps(state.to_dict()), datetime.now(), state.session_id
        )
    
    async def _broadcast_progress(self, session_id: str, step: str, message: str, percentage: int):
        """Broadcast progress update"""
        progress = {
            "task_id": session_id,
            "session_id": session_id,
            "status": "running",
            "current_step": step,
            "message": message,
            "progress_percentage": percentage,
            "timestamp": datetime.now().isoformat()
        }
        
        await manager.broadcast(
            json.dumps(progress),
            f"report_generation_{session_id}"
        )
    
    async def get_templates(
        self,
        engine_type: str = "all",
        category: str = "all"
    ) -> List[Dict[str, Any]]:
        """Get available report templates"""
        # In a real implementation, this would fetch from database
        # For now, return placeholder templates
        templates = [
            {
                "id": "comprehensive",
                "name": "Comprehensive Report",
                "description": "Detailed report covering all aspects",
                "category": "general",
                "engine_types": ["insight", "media", "query"]
            },
            {
                "id": "executive",
                "name": "Executive Summary",
                "description": "High-level summary for executives",
                "category": "business",
                "engine_types": ["insight", "media", "query"]
            },
            {
                "id": "technical",
                "name": "Technical Analysis",
                "description": "Detailed technical report",
                "category": "technical",
                "engine_types": ["insight", "media", "query"]
            },
            {
                "id": "academic",
                "name": "Academic Report",
                "description": "Scholarly report with citations",
                "category": "academic",
                "engine_types": ["insight", "media", "query"]
            }
        ]
        
        # Filter by engine type and category
        if engine_type != "all":
            templates = [t for t in templates if engine_type in t["engine_types"]]
        
        if category != "all":
            templates = [t for t in templates if t["category"] == category]
        
        return templates
    
    async def get_task_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get task status for a session"""
        db = await get_db_connection()
        
        # Get task
        task = await db.fetchrow(
            """
            SELECT * FROM report_tasks 
            WHERE session_id = $1 
            ORDER BY created_at DESC 
            LIMIT 1
            """,
            session_id
        )
        
        # Get state
        state = await db.fetchrow(
            "SELECT * FROM report_states WHERE session_id = $1",
            session_id
        )
        
        if not task or not state:
            return None
        
        return {
            "task": dict(task),
            "state": dict(state)
        }
    
    async def get_progress(self, session_id: str) -> Optional[ProgressResponse]:
        """Get current progress for a session"""
        status = await self.get_task_status(session_id)
        
        if not status:
            return None
        
        task = status["task"]
        state = status["state"]
        
        # Parse state data
        state_data = json.loads(state["state_data"]) if state["state_data"] else {}
        
        return ProgressResponse(
            session_id=session_id,
            task_id=task["id"],
            status=task["status"],
            current_step=state_data.get("current_step", "pending"),
            progress_percentage=state_data.get("progress_percentage", 0),
            message=state_data.get("message", "Report generation in progress"),
            created_at=task["created_at"],
            updated_at=task["updated_at"]
        )
    
    async def stream_progress(self, session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream progress updates"""
        # Get initial status
        status = await self.get_task_status(session_id)
        if status:
            yield {
                "task_id": status["task"]["id"],
                "session_id": session_id,
                "status": status["task"]["status"],
                "message": "Progress streaming started",
                "timestamp": datetime.now().isoformat()
            }
        
        # In a real implementation, this would subscribe to database changes
        # For now, we'll poll the database
        import asyncio
        
        while True:
            await asyncio.sleep(1)
            
            new_status = await self.get_task_status(session_id)
            if new_status and new_status != status:
                status = new_status
                yield {
                    "task_id": status["task"]["id"],
                    "session_id": session_id,
                    "status": status["task"]["status"],
                    "message": status["state"].get("message", "Processing..."),
                    "progress_percentage": status["state"].get("progress_percentage", 0),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Stop if completed or failed
                if status["task"]["status"] in ["completed", "failed"]:
                    break
    
    async def get_report_file(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get generated report file"""
        db = await get_db_connection()
        
        # Get state
        state = await db.fetchrow(
            "SELECT * FROM report_states WHERE session_id = $1",
            session_id
        )
        
        if not state:
            return None
        
        # Parse state data
        state_data = json.loads(state["state_data"]) if state["state_data"] else {}
        
        # Determine content and media type
        content = state_data.get("report_content", "")
        filename = f"report_{session_id}.md"
        media_type = "text/markdown"
        
        if state_data.get("html_content"):
            content = state_data["html_content"]
            filename = f"report_{session_id}.html"
            media_type = "text/html"
        elif state_data.get("pdf_content"):
            content = state_data["pdf_content"]
            filename = f"report_{session_id}.pdf"
            media_type = "application/pdf"
        
        # In a real implementation, this would save to file system
        # For now, return the content directly
        return {
            "content": content,
            "filename": filename,
            "media_type": media_type,
            "path": f"/tmp/{filename}"  # Placeholder path
        }
    
    async def verify_session_ownership(self, session_id: str, user_id: str) -> bool:
        """Verify that a session belongs to the current user"""
        db = await get_db_connection()
        
        result = await db.fetchval(
            """
            SELECT COUNT(*) FROM report_tasks 
            WHERE session_id = $1 AND user_id = $2
            """,
            session_id, user_id
        )
        
        return result > 0
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a report generation session"""
        db = await get_db_connection()
        
        # Delete related records
        await db.execute("DELETE FROM report_states WHERE session_id = $1", session_id)
        await db.execute("DELETE FROM report_tasks WHERE session_id = $1", session_id)
        
        return True
    
    async def list_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """List all report generation sessions for a user"""
        db = await get_db_connection()
        
        sessions = await db.fetch(
            """
            SELECT DISTINCT session_id, title, status, created_at, updated_at
            FROM report_tasks
            WHERE user_id = $1
            ORDER BY updated_at DESC
            """,
            user_id
        )
        
        return [dict(session) for session in sessions]
    
    async def preview_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Preview a report template"""
        templates = await self.get_templates()
        
        for template in templates:
            if template["id"] == template_id:
                return template
        
        return None
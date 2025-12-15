"""
Analysis API endpoints - Managing analysis tasks and results.
"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel

from core.database import get_db_connection
from core.exceptions import BusinessLogicException, ResourceNotFoundException
from services.auth_service import get_current_user
from services.websocket_manager import manager

router = APIRouter()

# Request/Response models
class AnalysisRequest(BaseModel):
    query: str
    engines: List[str] = []
    options: Dict[str, Any] = {}

class AnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    query: str
    engines: List[str]
    status: str
    message: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

# In-memory storage for analysis tasks (in production, use database)
ANALYSIS_TASKS = {}

async def create_analysis_task(
    query: str,
    engines: List[str],
    options: Dict[str, Any],
    user_id: str
) -> str:
    """Create a new analysis task"""
    analysis_id = f"analysis_{int(time.time())}_{user_id}"
    
    ANALYSIS_TASKS[analysis_id] = {
        "id": analysis_id,
        "query": query,
        "engines": engines,
        "options": options,
        "user_id": user_id,
        "status": "pending",
        "results": {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    return analysis_id

async def update_analysis_status(
    analysis_id: str,
    status: str,
    results: Optional[Dict[str, Any]] = None
):
    """Update analysis task status"""
    if analysis_id in ANALYSIS_TASKS:
        ANALYSIS_TASKS[analysis_id]["status"] = status
        ANALYSIS_TASKS[analysis_id]["updated_at"] = datetime.utcnow()
        
        if results:
            ANALYSIS_TASKS[analysis_id]["results"].update(results)
        
        # Broadcast status update
        await manager.broadcast_to_frontend({
            "type": "analysis_status",
            "data": {
                "analysis_id": analysis_id,
                "status": status,
                "results": ANALYSIS_TASKS[analysis_id]["results"],
                "timestamp": datetime.utcnow().isoformat()
            }
        })

async def run_analysis_task(analysis_id: str):
    """Run analysis in background"""
    try:
        await update_analysis_status(analysis_id, "running")
        
        # Simulate analysis work
        await asyncio.sleep(5)
        
        # Mock results
        task = ANALYSIS_TASKS[analysis_id]
        mock_results = {
            "insight": {"summary": "Insight analysis completed", "sentiment": "positive"},
            "media": {"summary": "Media analysis completed", "sources": 15},
            "query": {"summary": "Query analysis completed", "results": 25}
        }
        
        # Filter results based on requested engines
        filtered_results = {
            engine: mock_results.get(engine, {})
            for engine in task["engines"]
            if engine in mock_results
        }
        
        await update_analysis_status(analysis_id, "completed", filtered_results)
        
    except Exception as e:
        await update_analysis_status(analysis_id, "failed", {"error": str(e)})

# API Endpoints

@router.post("/start", response_model=AnalysisResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Start a new analysis task"""
    try:
        if not request.query.strip():
            raise BusinessLogicException("Analysis query cannot be empty")
        
        # Use provided engines or default to all
        engines = request.engines if request.engines else ["insight", "media", "query"]
        
        # Create analysis task
        analysis_id = await create_analysis_task(
            request.query,
            engines,
            request.options,
            str(user.get("id", "anonymous"))
        )
        
        # Start analysis in background
        background_tasks.add_task(run_analysis_task, analysis_id)
        
        task = ANALYSIS_TASKS[analysis_id]
        
        return AnalysisResponse(
            success=True,
            analysis_id=analysis_id,
            query=request.query,
            engines=engines,
            status="started",
            message="Analysis started successfully",
            created_at=task["created_at"].isoformat(),
            updated_at=task["updated_at"].isoformat()
        )
        
    except BusinessLogicException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start analysis: {str(e)}"
        )

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_status(
    analysis_id: str,
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Get analysis task status"""
    try:
        if analysis_id not in ANALYSIS_TASKS:
            raise ResourceNotFoundException("Analysis task")
        
        task = ANALYSIS_TASKS[analysis_id]
        
        return AnalysisResponse(
            success=True,
            analysis_id=analysis_id,
            query=task["query"],
            engines=task["engines"],
            status=task["status"],
            results=task["results"] if task["results"] else None,
            created_at=task["created_at"].isoformat(),
            updated_at=task["updated_at"].isoformat()
        )
        
    except ResourceNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis status: {str(e)}"
        )

@router.get("/{analysis_id}/results")
async def get_analysis_results(
    analysis_id: str,
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Get detailed analysis results"""
    try:
        if analysis_id not in ANALYSIS_TASKS:
            raise ResourceNotFoundException("Analysis task")
        
        task = ANALYSIS_TASKS[analysis_id]
        
        if task["status"] != "completed":
            return {
                "success": False,
                "message": "Analysis not completed yet",
                "status": task["status"]
            }
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "query": task["query"],
            "engines": task["engines"],
            "results": task["results"],
            "created_at": task["created_at"].isoformat(),
            "completed_at": task["updated_at"].isoformat()
        }
        
    except ResourceNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis results: {str(e)}"
        )

@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Delete analysis task"""
    try:
        if analysis_id not in ANALYSIS_TASKS:
            raise ResourceNotFoundException("Analysis task")
        
        # Check ownership (in production, verify user_id matches)
        task = ANALYSIS_TASKS[analysis_id]
        
        del ANALYSIS_TASKS[analysis_id]
        
        return {
            "success": True,
            "message": f"Analysis {analysis_id} deleted successfully"
        }
        
    except ResourceNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete analysis: {str(e)}"
        )

@router.get("/")
async def list_analyses(
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection,
    limit: int = 20,
    offset: int = 0
):
    """List user's analysis tasks"""
    try:
        # Filter tasks by user (in production, use database query)
        user_id = str(user.get("id", "anonymous"))
        user_tasks = [
            task for task in ANALYSIS_TASKS.values()
            if task.get("user_id") == user_id
        ]
        
        # Sort by created_at descending
        user_tasks.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        paginated_tasks = user_tasks[offset:offset + limit]
        
        return {
            "success": True,
            "analyses": [
                {
                    "analysis_id": task["id"],
                    "query": task["query"],
                    "engines": task["engines"],
                    "status": task["status"],
                    "created_at": task["created_at"].isoformat(),
                    "updated_at": task["updated_at"].isoformat()
                }
                for task in paginated_tasks
            ],
            "total": len(user_tasks),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list analyses: {str(e)}"
        )
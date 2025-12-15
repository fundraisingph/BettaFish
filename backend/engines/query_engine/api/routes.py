"""
QueryEngine API Routes
"""
from typing import Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse

from api.auth import get_current_user
from api.websocket import manager
from core.database import get_db_connection
from models.auth import UserResponse
from ..services.query_service import QueryService
from ..models.schemas import (
    QuerySearchRequest,
    QuerySearchResponse,
    QueryOptimizeRequest,
    QueryOptimizeResponse,
    QueryResearchRequest,
    QueryResearchResponse,
    QueryStreamRequest,
    ProgressResponse
)

router = APIRouter(
    prefix="/query",
    tags=["query"],
)

# QueryService dependency
async def get_query_service():
    return QueryService()

@router.post("/search", response_model=QuerySearchResponse)
async def search_query(
    request: QuerySearchRequest,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    query_service: QueryService = Depends(get_query_service)
):
    """
    Search for precise information based on query
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create search task
        task_id = await query_service.create_search_task(
            session_id=session_id,
            user_id=current_user.id,
            query=request.query,
            search_type=request.search_type,
            max_results=request.max_results
        )
        
        # Execute search
        search_results = await query_service.execute_search(task_id)
        
        return QuerySearchResponse(
            success=True,
            message="Query search completed successfully",
            data=search_results,
            session_id=session_id,
            task_id=task_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize", response_model=QueryOptimizeResponse)
async def optimize_query(
    request: QueryOptimizeRequest,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    query_service: QueryService = Depends(get_query_service)
):
    """
    Optimize search query for better results
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create optimization task
        task_id = await query_service.create_optimize_task(
            session_id=session_id,
            user_id=current_user.id,
            query=request.query,
            optimization_type=request.optimization_type
        )
        
        # Execute optimization
        optimization_results = await query_service.execute_optimize(task_id)
        
        return QueryOptimizeResponse(
            success=True,
            message="Query optimization completed successfully",
            data=optimization_results,
            session_id=session_id,
            task_id=task_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/research", response_model=QueryResearchResponse)
async def research_query(
    request: QueryResearchRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    query_service: QueryService = Depends(get_query_service)
):
    """
    Perform comprehensive query research
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create research task
        task_id = await query_service.create_research_task(
            session_id=session_id,
            user_id=current_user.id,
            query=request.query,
            research_type=request.research_type,
            max_iterations=request.max_iterations
        )
        
        # Start background research
        background_tasks.add_task(
            query_service.execute_research,
            task_id,
            session_id
        )
        
        return QueryResearchResponse(
            success=True,
            message="Query research started successfully",
            data={"task_id": task_id, "status": "started"},
            session_id=session_id,
            task_id=task_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_query_research(
    request: QueryStreamRequest,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    query_service: QueryService = Depends(get_query_service)
):
    """
    Stream query research progress and results
    """
    try:
        # Verify session belongs to current user
        if not await query_service.verify_session_ownership(
            request.session_id, current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get task status
        task_status = await query_service.get_task_status(request.session_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Create streaming response
        async def generate():
            async for progress in query_service.stream_progress(request.session_id):
                yield f"data: {progress.json()}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/progress/{session_id}", response_model=ProgressResponse)
async def get_query_research_progress(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    query_service: QueryService = Depends(get_query_service)
):
    """
    Get query research progress for a session
    """
    try:
        # Verify session belongs to current user
        if not await query_service.verify_session_ownership(
            session_id, current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get progress
        progress = await query_service.get_progress(session_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Progress not found")
        
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_query_session(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    query_service: QueryService = Depends(get_query_service)
):
    """
    Delete a query research session
    """
    try:
        # Verify session belongs to current user
        if not await query_service.verify_session_ownership(
            session_id, current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete session
        success = await query_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"success": True, "message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def list_query_sessions(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    query_service: QueryService = Depends(get_query_service)
):
    """
    List all query research sessions for the current user
    """
    try:
        sessions = await query_service.list_user_sessions(current_user.id)
        return {"success": True, "data": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
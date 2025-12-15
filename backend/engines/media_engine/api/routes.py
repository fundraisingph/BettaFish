"""
MediaEngine API Routes
"""
from typing import Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse

from api.auth import get_current_user
from api.websocket import manager
from core.database import get_db_connection as get_db
from models.auth import UserResponse
from ..services.media_service import MediaService
from .models.schemas import (
    MediaSearchRequest,
    MediaSearchResponse,
    MediaAnalysisRequest,
    MediaAnalysisResponse,
    MediaResearchRequest,
    MediaResearchResponse,
    MediaStreamRequest,
    ProgressResponse
)

router = APIRouter(
    prefix="/media",
    tags=["media"],
)

# MediaService dependency
async def get_media_service():
    return MediaService()

@router.post("/search", response_model=MediaSearchResponse)
async def search_media(
    request: MediaSearchRequest,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db),
    media_service: MediaService = Depends(get_media_service)
):
    """
    Search for media content based on query
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create search task
        task_id = await media_service.create_search_task(
            session_id=session_id,
            user_id=current_user.id,
            query=request.query,
            search_type=request.search_type,
            time_range=request.time_range,
            max_results=request.max_results
        )
        
        # Execute search
        search_results = await media_service.execute_search(task_id)
        
        return MediaSearchResponse(
            success=True,
            message="Media search completed successfully",
            data=search_results,
            session_id=session_id,
            task_id=task_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=MediaAnalysisResponse)
async def analyze_media(
    request: MediaAnalysisRequest,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db),
    media_service: MediaService = Depends(get_media_service)
):
    """
    Analyze media content
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create analysis task
        task_id = await media_service.create_analysis_task(
            session_id=session_id,
            user_id=current_user.id,
            content=request.content,
            analysis_type=request.analysis_type
        )
        
        # Execute analysis
        analysis_results = await media_service.execute_analysis(task_id)
        
        return MediaAnalysisResponse(
            success=True,
            message="Media analysis completed successfully",
            data=analysis_results,
            session_id=session_id,
            task_id=task_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/research", response_model=MediaResearchResponse)
async def research_media(
    request: MediaResearchRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db),
    media_service: MediaService = Depends(get_media_service)
):
    """
    Perform comprehensive media research
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create research task
        task_id = await media_service.create_research_task(
            session_id=session_id,
            user_id=current_user.id,
            query=request.query,
            research_type=request.research_type,
            max_iterations=request.max_iterations
        )
        
        # Start background research
        background_tasks.add_task(
            media_service.execute_research,
            task_id,
            session_id
        )
        
        return MediaResearchResponse(
            success=True,
            message="Media research started successfully",
            data={"task_id": task_id, "status": "started"},
            session_id=session_id,
            task_id=task_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_media_research(
    request: MediaStreamRequest,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db),
    media_service: MediaService = Depends(get_media_service)
):
    """
    Stream media research progress and results
    """
    try:
        # Verify session belongs to current user
        if not await media_service.verify_session_ownership(
            request.session_id, current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get task status
        task_status = await media_service.get_task_status(request.session_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Create streaming response
        async def generate():
            async for progress in media_service.stream_progress(request.session_id):
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
async def get_research_progress(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db),
    media_service: MediaService = Depends(get_media_service)
):
    """
    Get research progress for a session
    """
    try:
        # Verify session belongs to current user
        if not await media_service.verify_session_ownership(
            session_id, current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get progress
        progress = await media_service.get_progress(session_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Progress not found")
        
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db),
    media_service: MediaService = Depends(get_media_service)
):
    """
    Delete a research session
    """
    try:
        # Verify session belongs to current user
        if not await media_service.verify_session_ownership(
            session_id, current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete session
        success = await media_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"success": True, "message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def list_sessions(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db),
    media_service: MediaService = Depends(get_media_service)
):
    """
    List all research sessions for the current user
    """
    try:
        sessions = await media_service.list_user_sessions(current_user.id)
        return {"success": True, "data": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""
InsightEngine API routes
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import logging
logger = logging.getLogger(__name__)

from api.auth import get_current_user
from models.auth import UserResponse as User
from core.exceptions import ValidationException as ValidationError, ResourceNotFoundException as NotFoundError
from services.websocket_manager import manager
from ..services.insight_service import InsightService
from ..models.schemas import (
    SearchRequest, SearchResponse, ResearchRequest, ResearchResponse,
    ProgressResponse, SentimentAnalysisRequest, SentimentAnalysisResponse,
    StreamRequest
)

# Initialize router
router = APIRouter(tags=["insight"])

# Initialize service
insight_service = InsightService()


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
) -> SearchResponse:
    """
    Execute search operation with specified tool
    
    Args:
        request: Search request with tool, query, and parameters
        current_user: Current authenticated user
        
    Returns:
        Search response with results
    """
    try:
        logger.info(f"User {current_user.email} executing search: {request.tool_name}")
        
        # Execute search
        response = await insight_service.search(request)
        
        return response
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Search operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/analyze-sentiment", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    current_user: User = Depends(get_current_user)
) -> SentimentAnalysisResponse:
    """
    Analyze sentiment of texts
    
    Args:
        request: Sentiment analysis request with texts
        current_user: Current authenticated user
        
    Returns:
        Sentiment analysis response
    """
    try:
        logger.info(f"User {current_user.email} analyzing sentiment")
        
        # Execute sentiment analysis
        response = await insight_service.analyze_sentiment_only(
            texts=request.texts,
            min_confidence=request.min_confidence
        )
        
        return response
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/research", response_model=ResearchResponse)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> ResearchResponse:
    """
    Start a new research task
    
    Args:
        request: Research request with query and options
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        
    Returns:
        Research response with task ID
    """
    try:
        logger.info(f"User {current_user.email} starting research: {request.query}")
        
        # Start research task
        response = await insight_service.start_research(request)
        
        if response.success:
            # Send WebSocket notification
            await manager.broadcast({
                "type": "research_started",
                "research_id": response.research_id,
                "query": request.query,
                "user_email": current_user.email
            })
        
        return response
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start research: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/research/{research_id}/progress", response_model=ProgressResponse)
async def get_research_progress(
    research_id: str,
    current_user: User = Depends(get_current_user)
) -> ProgressResponse:
    """
    Get progress of a research task
    
    Args:
        research_id: Research task ID
        current_user: Current authenticated user
        
    Returns:
        Progress response with current status
    """
    try:
        logger.info(f"User {current_user.email} getting research progress: {research_id}")
        
        # Get research progress
        response = await insight_service.get_research_progress(research_id)
        
        if response.error_message:
            raise NotFoundError(response.error_message)
        
        return response
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get research progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/research/{research_id}/state", response_model=ResearchResponse)
async def get_research_state(
    research_id: str,
    current_user: User = Depends(get_current_user)
) -> ResearchResponse:
    """
    Get complete state of a research task
    
    Args:
        research_id: Research task ID
        current_user: Current authenticated user
        
    Returns:
        Research response with current state
    """
    try:
        logger.info(f"User {current_user.email} getting research state: {research_id}")
        
        # Get research state
        response = await insight_service.get_research_state(research_id)
        
        if response.error_message:
            raise NotFoundError(response.error_message)
        
        return response
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get research state: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/research/active", response_model=Dict[str, Any])
async def get_active_research_tasks(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get all active research tasks
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dictionary of active research tasks
    """
    try:
        logger.info(f"User {current_user.email} getting active research tasks")
        
        # Get active research tasks
        tasks = await insight_service.get_active_research_tasks()
        
        # Convert to serializable format
        serializable_tasks = {}
        for task_id, state in tasks.items():
            serializable_tasks[task_id] = state.dict()
        
        return {
            "active_tasks": serializable_tasks,
            "total_count": len(tasks)
        }
        
    except Exception as e:
        logger.error(f"Failed to get active research tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stream/{research_id}")
async def stream_research_progress(
    research_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Stream research progress updates via Server-Sent Events
    
    Args:
        research_id: Research task ID
        current_user: Current authenticated user
        
    Returns:
        Streaming response with progress updates
    """
    try:
        logger.info(f"User {current_user.email} streaming research progress: {research_id}")
        
        # Check if research task exists
        progress = await insight_service.get_research_progress(research_id)
        if progress.error_message:
            raise NotFoundError(progress.error_message)
        
        # Define event generator
        async def event_generator():
            try:
                # Send initial state
                yield f"data: {progress.json()}\n\n"
                
                # Stream updates until completion
                last_progress = progress.progress_percentage
                while not progress.is_completed:
                    # Wait for update
                    await asyncio.sleep(2)  # Poll every 2 seconds
                    
                    # Get current progress
                    progress = await insight_service.get_research_progress(research_id)
                    
                    # Send update if progress changed
                    if progress.progress_percentage != last_progress:
                        yield f"data: {progress.json()}\n\n"
                        last_progress = progress.progress_percentage
                
                # Send final completion event
                yield f"data: {progress.json()}\n\n"
                
            except Exception as e:
                logger.error(f"Error in event generator: {str(e)}")
                yield f"event: error\ndata: {{\"error\": \"{str(e)}\"}}\n\n"
        
        # Return streaming response
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to stream research progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status", response_model=Dict[str, Any])
async def get_engine_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get InsightEngine status information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Status information dictionary
    """
    try:
        logger.info(f"User {current_user.email} getting engine status")
        
        # Get engine status
        status = await insight_service.get_engine_status()
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get engine status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/research/{research_id}", response_model=Dict[str, Any])
async def cancel_research(
    research_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Cancel a research task
    
    Args:
        research_id: Research task ID
        current_user: Current authenticated user
        
    Returns:
        Cancellation response
    """
    try:
        logger.info(f"User {current_user.email} cancelling research: {research_id}")
        
        # Get active research tasks
        tasks = await insight_service.get_active_research_tasks()
        
        if research_id not in tasks:
            raise NotFoundError("Research task not found")
        
        # Mark task as completed (cancellation)
        state = tasks[research_id]
        state.is_completed = True
        state.cancellation_reason = "Cancelled by user"
        
        # Update task
        tasks[research_id] = state
        
        # Send WebSocket notification
        await manager.broadcast({
            "type": "research_cancelled",
            "research_id": research_id,
            "user_email": current_user.email
        })
        
        return {
            "success": True,
            "message": "Research task cancelled successfully",
            "research_id": research_id
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to cancel research: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
"""
ReportEngine API Routes
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
from ..services.report_service import ReportService
from ..models.schemas import (
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportTemplateRequest,
    ReportTemplateResponse,
    ReportStreamRequest,
    ProgressResponse
)

router = APIRouter(
    prefix="/report",
    tags=["report"],
)

# ReportService dependency
async def get_report_service():
    return ReportService()

@router.post("/generate", response_model=ReportGenerationResponse)
async def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Generate a report from engine outputs
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create report generation task
        task_id = await report_service.create_report_task(
            session_id=session_id,
            user_id=current_user.id,
            title=request.title,
            template_type=request.template_type,
            engine_outputs=request.engine_outputs,
            include_charts=request.include_charts,
            output_format=request.output_format
        )
        
        # Start background report generation
        background_tasks.add_task(
            report_service.execute_report_generation,
            task_id,
            session_id
        )
        
        return ReportGenerationResponse(
            success=True,
            message="Report generation started successfully",
            data={"task_id": task_id, "session_id": session_id},
            session_id=session_id,
            task_id=task_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates", response_model=ReportTemplateResponse)
async def get_templates(
    request: ReportTemplateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Get available report templates
    """
    try:
        templates = await report_service.get_templates(
            engine_type=request.engine_type,
            category=request.category
        )
        
        return ReportTemplateResponse(
            success=True,
            message="Templates retrieved successfully",
            data=templates
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_report_generation(
    request: ReportStreamRequest,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Stream report generation progress and results
    """
    try:
        # Verify session belongs to current user
        if not await report_service.verify_session_ownership(
            request.session_id, current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get task status
        task_status = await report_service.get_task_status(request.session_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Create streaming response
        async def generate():
            async for progress in report_service.stream_progress(request.session_id):
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
async def get_report_progress(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Get report generation progress for a session
    """
    try:
        # Verify session belongs to current user
        if not await report_service.verify_session_ownership(
            session_id, current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get progress
        progress = await report_service.get_progress(session_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Progress not found")
        
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{session_id}")
async def download_report(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Download a generated report
    """
    try:
        # Verify session belongs to current user
        if not await report_service.verify_session_ownership(
            session_id, current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get report file
        report_file = await report_service.get_report_file(session_id)
        
        if not report_file:
            raise HTTPException(status_code=404, detail="Report not found")
        
        from fastapi.responses import FileResponse
        
        return FileResponse(
            path=report_file["path"],
            filename=report_file["filename"],
            media_type=report_file["media_type"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_report_session(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Delete a report generation session
    """
    try:
        # Verify session belongs to current user
        if not await report_service.verify_session_ownership(
            session_id, current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete session
        success = await report_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"success": True, "message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def list_report_sessions(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    report_service: ReportService = Depends(get_report_service)
):
    """
    List all report generation sessions for the current user
    """
    try:
        sessions = await report_service.list_user_sessions(current_user.id)
        return {"success": True, "data": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/preview/{template_id}")
async def preview_template(
    template_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_db_connection),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Preview a report template
    """
    try:
        preview = await report_service.preview_template(template_id)
        
        if not preview:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {"success": True, "data": preview}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
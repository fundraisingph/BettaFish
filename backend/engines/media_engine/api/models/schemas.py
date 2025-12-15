"""
MediaEngine API Schemas
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class MediaSearchRequest(BaseModel):
    """Media search request schema"""
    query: str = Field(..., description="Search query")
    search_type: str = Field(default="multimodal", description="Search type")
    time_range: Optional[str] = Field(None, description="Time range for search")
    max_results: int = Field(default=10, description="Maximum results to return")


class MediaSearchResponse(BaseModel):
    """Media search response schema"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Search results data")
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")


class MediaAnalysisRequest(BaseModel):
    """Media analysis request schema"""
    content: Dict[str, Any] = Field(..., description="Content to analyze")
    analysis_type: str = Field(default="multimodal", description="Analysis type")


class MediaAnalysisResponse(BaseModel):
    """Media analysis response schema"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Analysis results data")
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")


class MediaResearchRequest(BaseModel):
    """Media research request schema"""
    query: str = Field(..., description="Research query")
    research_type: str = Field(default="comprehensive", description="Research type")
    max_iterations: int = Field(default=3, description="Maximum iterations")


class MediaResearchResponse(BaseModel):
    """Media research response schema"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Research results data")
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")


class MediaStreamRequest(BaseModel):
    """Media stream request schema"""
    session_id: str = Field(..., description="Session ID")


class ProgressResponse(BaseModel):
    """Progress response schema"""
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Task status")
    progress: float = Field(..., description="Progress percentage")
    message: str = Field(..., description="Status message")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Update timestamp")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    class Config:
        json_encoders = {
            # Custom JSON encoding if needed
        }
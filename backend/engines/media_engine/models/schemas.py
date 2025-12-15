"""
MediaEngine Pydantic Schemas
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

# Request Schemas
class MediaSearchRequest(BaseModel):
    """Media search request"""
    query: str = Field(..., description="Search query")
    search_type: str = Field(default="multimodal", description="Type of search")
    time_range: Optional[str] = Field(None, description="Time range for search")
    max_results: int = Field(default=10, description="Maximum number of results")

class MediaAnalysisRequest(BaseModel):
    """Media analysis request"""
    content: Dict[str, Any] = Field(..., description="Content to analyze")
    analysis_type: str = Field(default="multimodal", description="Type of analysis")

class MediaResearchRequest(BaseModel):
    """Media research request"""
    query: str = Field(..., description="Research query")
    research_type: str = Field(default="comprehensive", description="Type of research")
    max_iterations: int = Field(default=3, description="Maximum research iterations")

class MediaStreamRequest(BaseModel):
    """Media stream request"""
    session_id: str = Field(..., description="Session ID for streaming")

# Response Schemas
class MediaSearchResponse(BaseModel):
    """Media search response"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Search results")
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")

class MediaAnalysisResponse(BaseModel):
    """Media analysis response"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Analysis results")
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")

class MediaResearchResponse(BaseModel):
    """Media research response"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Research results")
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")

class ProgressResponse(BaseModel):
    """Progress response"""
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Current status")
    progress: float = Field(..., description="Progress percentage")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")

# Internal Schemas
class SearchResult(BaseModel):
    """Search result item"""
    id: str = Field(..., description="Result ID")
    title: str = Field(..., description="Result title")
    content: str = Field(..., description="Result content")
    source: str = Field(..., description="Source of the result")
    timestamp: str = Field(..., description="Result timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class AnalysisResult(BaseModel):
    """Analysis result item"""
    content_id: str = Field(..., description="Content ID")
    sentiment: str = Field(..., description="Sentiment analysis")
    topics: List[str] = Field(..., description="Extracted topics")
    confidence: float = Field(..., description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ResearchIteration(BaseModel):
    """Research iteration result"""
    iteration: int = Field(..., description="Iteration number")
    query: str = Field(..., description="Query used")
    results: List[SearchResult] = Field(..., description="Search results")
    analysis: Optional[AnalysisResult] = Field(None, description="Analysis results")
    summary: str = Field(..., description="Iteration summary")
    timestamp: datetime = Field(..., description="Iteration timestamp")

class MediaResearchState(BaseModel):
    """Media research state"""
    session_id: str = Field(..., description="Session ID")
    query: str = Field(..., description="Original query")
    max_iterations: int = Field(..., description="Maximum iterations")
    current_iteration: int = Field(default=0, description="Current iteration")
    iterations: List[ResearchIteration] = Field(default=[], description="Completed iterations")
    final_summary: Optional[str] = Field(None, description="Final research summary")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")

# Error Schemas
class MediaError(BaseModel):
    """Media engine error"""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")

# Configuration Schemas
class MediaEngineConfig(BaseModel):
    """Media engine configuration"""
    search_providers: List[str] = Field(default=[], description="Available search providers")
    analysis_models: List[str] = Field(default=[], description="Available analysis models")
    max_search_results: int = Field(default=50, description="Maximum search results")
    default_iterations: int = Field(default=3, description="Default research iterations")
    timeout_seconds: int = Field(default=300, description="Operation timeout")

# Task Schemas
class MediaTask(BaseModel):
    """Media task"""
    task_id: str = Field(..., description="Task ID")
    session_id: str = Field(..., description="Session ID")
    user_id: int = Field(..., description="User ID")
    task_type: str = Field(..., description="Task type")
    status: str = Field(..., description="Task status")
    parameters: Dict[str, Any] = Field(..., description="Task parameters")
    results: Optional[Dict[str, Any]] = Field(None, description="Task results")
    error: Optional[str] = Field(None, description="Task error")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")

# Session Schemas
class MediaSession(BaseModel):
    """Media session"""
    session_id: str = Field(..., description="Session ID")
    user_id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")
    status: str = Field(..., description="Session status")
    tasks: List[MediaTask] = Field(default=[], description="Session tasks")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Session metadata")

# Provider Schemas
class SearchProvider(BaseModel):
    """Search provider configuration"""
    name: str = Field(..., description="Provider name")
    endpoint: str = Field(..., description="Provider endpoint")
    api_key: Optional[str] = Field(None, description="API key")
    rate_limit: int = Field(default=100, description="Rate limit per minute")
    timeout: int = Field(default=30, description="Request timeout")
    enabled: bool = Field(default=True, description="Provider enabled")

class AnalysisProvider(BaseModel):
    """Analysis provider configuration"""
    name: str = Field(..., description="Provider name")
    model: str = Field(..., description="Model name")
    endpoint: str = Field(..., description="Provider endpoint")
    api_key: Optional[str] = Field(None, description="API key")
    rate_limit: int = Field(default=100, description="Rate limit per minute")
    timeout: int = Field(default=60, description="Request timeout")
    enabled: bool = Field(default=True, description="Provider enabled")

# Content Schemas
class MediaContent(BaseModel):
    """Media content"""
    content_id: str = Field(..., description="Content ID")
    content_type: str = Field(..., description="Content type")
    title: str = Field(..., description="Content title")
    text: str = Field(..., description="Content text")
    media_url: Optional[str] = Field(None, description="Media URL")
    source: str = Field(..., description="Content source")
    author: Optional[str] = Field(None, description="Content author")
    published_at: Optional[datetime] = Field(None, description="Publication time")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

# Filter Schemas
class SearchFilter(BaseModel):
    """Search filter"""
    field: str = Field(..., description="Field to filter")
    operator: str = Field(..., description="Filter operator")
    value: Union[str, int, float, bool, List] = Field(..., description="Filter value")

class MediaSearchRequest(BaseModel):
    """Media search request with filters"""
    query: str = Field(..., description="Search query")
    search_type: str = Field(default="multimodal", description="Type of search")
    time_range: Optional[str] = Field(None, description="Time range for search")
    max_results: int = Field(default=10, description="Maximum number of results")
    filters: List[SearchFilter] = Field(default=[], description="Search filters")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order")

# Export Schemas
class MediaExportRequest(BaseModel):
    """Media export request"""
    session_id: str = Field(..., description="Session ID")
    export_format: str = Field(default="json", description="Export format")
    include_analysis: bool = Field(default=True, description="Include analysis results")
    include_metadata: bool = Field(default=True, description="Include metadata")

class MediaExportResponse(BaseModel):
    """Media export response"""
    success: bool = Field(..., description="Whether the export was successful")
    message: str = Field(..., description="Response message")
    export_url: Optional[str] = Field(None, description="Export file URL")
    data: Optional[Dict[str, Any]] = Field(None, description="Export data")
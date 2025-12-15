"""
QueryEngine Pydantic Schemas
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field

# Base schemas
class BaseRequest(BaseModel):
    """Base request schema"""
    pass

class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool = True
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)

# Search schemas
class QuerySearchRequest(BaseRequest):
    """Query search request"""
    query: str = Field(..., description="Search query")
    search_type: str = Field(default="comprehensive", description="Type of search")
    max_results: int = Field(default=10, description="Maximum number of results")

class QuerySearchResult(BaseModel):
    """Single search result"""
    title: str = Field(..., description="Result title")
    content: str = Field(..., description="Result content")
    url: Optional[str] = Field(None, description="Source URL")
    relevance_score: float = Field(..., description="Relevance score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class QuerySearchResponse(BaseResponse):
    """Query search response"""
    data: List[QuerySearchResult] = Field(default_factory=list, description="Search results")
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")

# Optimization schemas
class QueryOptimizeRequest(BaseRequest):
    """Query optimization request"""
    query: str = Field(..., description="Original query")
    optimization_type: str = Field(default="keyword", description="Type of optimization")

class QueryOptimizationResult(BaseModel):
    """Query optimization result"""
    original_query: str = Field(..., description="Original query")
    optimized_query: str = Field(..., description="Optimized query")
    optimization_type: str = Field(..., description="Type of optimization")
    improvements: List[str] = Field(default_factory=list, description="List of improvements")
    confidence_score: float = Field(..., description="Confidence in optimization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class QueryOptimizeResponse(BaseResponse):
    """Query optimization response"""
    data: QueryOptimizationResult = Field(..., description="Optimization results")
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")

# Research schemas
class QueryResearchRequest(BaseRequest):
    """Query research request"""
    query: str = Field(..., description="Research query")
    research_type: str = Field(default="comprehensive", description="Type of research")
    max_iterations: int = Field(default=3, description="Maximum number of iterations")

class QueryResearchResult(BaseModel):
    """Query research result"""
    query: str = Field(..., description="Original query")
    research_type: str = Field(..., description="Type of research")
    iterations: int = Field(..., description="Number of iterations performed")
    report_structure: Dict[str, Any] = Field(..., description="Report structure")
    formatted_report: str = Field(..., description="Formatted report")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class QueryResearchResponse(BaseResponse):
    """Query research response"""
    data: Dict[str, Any] = Field(..., description="Research results")
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")

# Progress schemas
class QueryStreamRequest(BaseRequest):
    """Query stream request"""
    session_id: str = Field(..., description="Session ID")

class ProgressResponse(BaseResponse):
    """Progress response"""
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Current status")
    current_iteration: int = Field(default=0, description="Current iteration")
    total_iterations: int = Field(default=0, description="Total iterations")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

# Task schemas
class QueryTask(BaseModel):
    """Query task model"""
    id: str = Field(..., description="Task ID")
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    query: str = Field(..., description="Query")
    search_type: str = Field(..., description="Search type")
    max_results: int = Field(..., description="Maximum results")
    status: str = Field(..., description="Task status")
    results: Optional[Dict[str, Any]] = Field(None, description="Task results")
    error: Optional[str] = Field(None, description="Error message")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

class QueryOptimizationTask(BaseModel):
    """Query optimization task model"""
    id: str = Field(..., description="Task ID")
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    query: str = Field(..., description="Query")
    optimization_type: str = Field(..., description="Optimization type")
    status: str = Field(..., description="Task status")
    results: Optional[Dict[str, Any]] = Field(None, description="Task results")
    error: Optional[str] = Field(None, description="Error message")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

class QueryResearchTask(BaseModel):
    """Query research task model"""
    id: str = Field(..., description="Task ID")
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    query: str = Field(..., description="Query")
    research_type: str = Field(..., description="Research type")
    max_iterations: int = Field(..., description="Maximum iterations")
    status: str = Field(..., description="Task status")
    results: Optional[Dict[str, Any]] = Field(None, description="Task results")
    error: Optional[str] = Field(None, description="Error message")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

# State schemas
class QueryResearchState(BaseModel):
    """Query research state model"""
    session_id: str = Field(..., description="Session ID")
    state_data: Dict[str, Any] = Field(..., description="State data")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

# Session schemas
class QuerySession(BaseModel):
    """Query session model"""
    session_id: str = Field(..., description="Session ID")
    query: str = Field(..., description="Query")
    status: str = Field(..., description="Session status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

# List schemas
class QuerySessionList(BaseModel):
    """List of query sessions"""
    sessions: List[QuerySession] = Field(default_factory=list, description="Session list")
    total: int = Field(default=0, description="Total count")

# Error schemas
class QueryError(BaseModel):
    """Query error model"""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

# WebSocket message schemas
class QueryWebSocketMessage(BaseModel):
    """WebSocket message for query operations"""
    type: str = Field(..., description="Message type")
    session_id: str = Field(..., description="Session ID")
    task_id: Optional[str] = Field(None, description="Task ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")

# Configuration schemas
class QueryEngineConfigSchema(BaseModel):
    """QueryEngine configuration schema"""
    max_search_results: int = Field(default=20, description="Maximum search results")
    max_optimization_attempts: int = Field(default=3, description="Maximum optimization attempts")
    max_research_iterations: int = Field(default=5, description="Maximum research iterations")
    default_search_type: str = Field(default="comprehensive", description="Default search type")
    default_optimization_type: str = Field(default="keyword", description="Default optimization type")
    default_research_type: str = Field(default="comprehensive", description="Default research type")
    enable_caching: bool = Field(default=True, description="Enable result caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    llm_timeout: int = Field(default=30, description="LLM timeout in seconds")
    search_timeout: int = Field(default=10, description="Search timeout in seconds")
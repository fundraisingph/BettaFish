"""
ReportEngine Pydantic Schemas
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

# Report generation schemas
class ReportGenerationRequest(BaseRequest):
    """Report generation request"""
    title: str = Field(..., description="Report title")
    template_type: str = Field(default="comprehensive", description="Template type")
    engine_outputs: Dict[str, Any] = Field(default_factory=dict, description="Outputs from engines")
    include_charts: bool = Field(default=False, description="Include charts in report")
    output_format: str = Field(default="markdown", description="Output format")

class ReportGenerationResponse(BaseResponse):
    """Report generation response"""
    data: Dict[str, Any] = Field(default_factory=dict, description="Generation data")
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")

# Template schemas
class ReportTemplateRequest(BaseRequest):
    """Report template request"""
    engine_type: str = Field(default="all", description="Filter by engine type")
    category: str = Field(default="all", description="Filter by category")

class ReportTemplateResponse(BaseResponse):
    """Report template response"""
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Template data")

# Stream schemas
class ReportStreamRequest(BaseRequest):
    """Report stream request"""
    session_id: str = Field(..., description="Session ID")

# Progress schemas
class ProgressResponse(BaseResponse):
    """Progress response"""
    session_id: str = Field(..., description="Session ID")
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Current status")
    current_step: str = Field(default="pending", description="Current step")
    progress_percentage: int = Field(default=0, description="Progress percentage")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

# Task schemas
class ReportTask(BaseModel):
    """Report task model"""
    id: str = Field(..., description="Task ID")
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Report title")
    template_type: str = Field(..., description="Template type")
    engine_outputs: Optional[Dict[str, Any]] = Field(None, description="Engine outputs")
    include_charts: bool = Field(..., description="Include charts")
    output_format: str = Field(..., description="Output format")
    status: str = Field(..., description="Task status")
    error: Optional[str] = Field(None, description="Error message")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

class ReportState(BaseModel):
    """Report state model"""
    session_id: str = Field(..., description="Session ID")
    state_data: Dict[str, Any] = Field(..., description="State data")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

# Session schemas
class ReportSession(BaseModel):
    """Report session model"""
    session_id: str = Field(..., description="Session ID")
    title: str = Field(..., description="Report title")
    status: str = Field(..., description="Session status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

# Error schemas
class ReportError(BaseModel):
    """Report error model"""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

# WebSocket message schemas
class ReportWebSocketMessage(BaseModel):
    """WebSocket message for report operations"""
    type: str = Field(..., description="Message type")
    session_id: str = Field(..., description="Session ID")
    task_id: Optional[str] = Field(None, description="Task ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")

# Configuration schemas
class ReportEngineConfigSchema(BaseModel):
    """ReportEngine configuration schema"""
    max_report_size: int = Field(default=10000, description="Maximum report size in KB")
    default_template: str = Field(default="comprehensive", description="Default template type")
    default_format: str = Field(default="markdown", description="Default output format")
    enable_charts: bool = Field(default=True, description="Enable chart generation")
    chart_types: List[str] = Field(default_factory=lambda: ["pie", "line", "bar"], description="Supported chart types")
    export_formats: List[str] = Field(default_factory=lambda: ["markdown", "html", "pdf"], description="Supported export formats")
    template_cache_ttl: int = Field(default=3600, description="Template cache TTL in seconds")
    max_concurrent_reports: int = Field(default=5, description="Maximum concurrent reports")
    enable_real_time_updates: bool = Field(default=True, description="Enable real-time progress updates")
    storage_path: str = Field(default="/tmp/reports", description="Report storage path")
    cleanup_interval: int = Field(default=86400, description="Cleanup interval in seconds")
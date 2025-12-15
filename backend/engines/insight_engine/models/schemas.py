"""
Pydantic schemas for InsightEngine API
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field


class QueryResult(BaseModel):
    """Unified database query result data class"""
    platform: str
    content_type: str
    title_or_content: str
    author_nickname: Optional[str] = None
    url: Optional[str] = None
    publish_time: Optional[datetime] = None
    engagement: Dict[str, int] = Field(default_factory=dict)
    source_keyword: Optional[str] = None
    hotness_score: float = 0.0
    source_table: str = ""

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class DBResponse(BaseModel):
    """Encapsulates the complete return result of a tool"""
    tool_name: str
    parameters: Dict[str, Any]
    results: List[QueryResult] = Field(default_factory=list)
    results_count: int = 0
    error_message: Optional[str] = None
    sentiment_analysis: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    """Request model for search operations"""
    tool_name: Literal[
        "search_hot_content",
        "search_topic_globally", 
        "search_topic_by_date",
        "get_comments_for_topic",
        "search_topic_on_platform",
        "analyze_sentiment"
    ]
    query: str
    start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    platform: Optional[Literal['bilibili', 'weibo', 'douyin', 'kuaishou', 'xhs', 'zhihu', 'tieba']] = None
    time_period: Optional[Literal['24h', 'week', 'year']] = Field('week', description="Time period for hot content search")
    limit: Optional[int] = Field(50, description="Maximum number of results")
    limit_per_table: Optional[int] = Field(50, description="Maximum results per table")
    enable_sentiment: Optional[bool] = Field(True, description="Enable automatic sentiment analysis")
    texts: Optional[List[str]] = Field(None, description="Texts for sentiment analysis")


class SearchResponse(BaseModel):
    """Response model for search operations"""
    success: bool
    tool_name: str
    parameters: Dict[str, Any]
    results_count: int
    results: List[QueryResult] = Field(default_factory=list)
    sentiment_analysis: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class SentimentAnalysisRequest(BaseModel):
    """Request model for sentiment analysis"""
    texts: Union[str, List[str]]
    min_confidence: Optional[float] = Field(0.5, description="Minimum confidence threshold")


class SentimentResult(BaseModel):
    """Individual sentiment analysis result"""
    text: str
    sentiment_label: str
    confidence: float
    probability_distribution: Dict[str, float]
    success: bool = True
    error_message: Optional[str] = None
    analysis_performed: bool = True


class BatchSentimentResult(BaseModel):
    """Batch sentiment analysis result"""
    results: List[SentimentResult]
    total_processed: int
    success_count: int
    failed_count: int
    average_confidence: float
    analysis_performed: bool = True


class SentimentAnalysisResponse(BaseModel):
    """Response model for sentiment analysis"""
    success: bool
    total_analyzed: int
    success_count: Optional[int] = None
    failed_count: Optional[int] = None
    average_confidence: Optional[float] = None
    results: Union[SentimentResult, List[SentimentResult], BatchSentimentResult]
    warning: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class ResearchRequest(BaseModel):
    """Request model for deep research"""
    query: str
    save_report: Optional[bool] = Field(True, description="Whether to save report to file")
    max_reflections: Optional[int] = Field(3, description="Maximum number of reflection cycles")
    max_paragraphs: Optional[int] = Field(6, description="Maximum number of paragraphs")


class ParagraphState(BaseModel):
    """Paragraph research state"""
    title: str
    content: str
    research: Dict[str, Any]
    order: int
    is_completed: bool = False


class ResearchState(BaseModel):
    """Complete research state"""
    query: str
    report_title: str
    paragraphs: List[ParagraphState]
    final_report: Optional[str] = None
    is_completed: bool = False
    created_at: datetime
    updated_at: datetime
    progress_summary: Dict[str, Any] = Field(default_factory=dict)


class ResearchResponse(BaseModel):
    """Response model for deep research"""
    success: bool
    research_id: Optional[str] = None
    state: Optional[ResearchState] = None
    final_report: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class StreamRequest(BaseModel):
    """Request model for streaming operations"""
    research_id: str = Field(..., description="Research task ID")


class ProgressResponse(BaseModel):
    """Response model for research progress"""
    research_id: str
    total_paragraphs: int
    completed_paragraphs: int
    progress_percentage: float
    is_completed: bool
    current_paragraph: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class StreamChunk(BaseModel):
    """WebSocket stream chunk model"""
    type: Literal["progress", "search_result", "sentiment_analysis", "paragraph_complete", "research_complete", "error"]
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InsightEngineStatus(BaseModel):
    """InsightEngine status response"""
    status: str
    model_info: Dict[str, Any]
    sentiment_analyzer_info: Dict[str, Any]
    database_connected: bool
    active_research_tasks: int
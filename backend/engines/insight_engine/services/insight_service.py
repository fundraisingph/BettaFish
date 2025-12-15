"""
InsightEngine service implementation
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import logging
logger = logging.getLogger(__name__)

from ..llms.base import LLMClient
from ..state.state import ResearchState
from ..models.schemas import (
    SearchRequest, SearchResponse, ResearchRequest, ResearchResponse,
    ProgressResponse, SentimentAnalysisRequest, SentimentAnalysisResponse,
    QueryResult, DBResponse, StreamChunk
)
from ..tools.search import MediaCrawlerDB
from ..tools.sentiment_analyzer import SentimentAnalyzer
from ..tools.keyword_optimizer import KeywordOptimizer
from ..utils.config import settings
from ..utils.text_processing import format_search_results_for_prompt
from ..nodes import (
    FirstSearchNode, FirstSummaryNode, ReflectionNode, 
    ReflectionSummaryNode, ReportStructureNode, ReportFormattingNode
)


class InsightService:
    """InsightEngine service for managing research operations"""
    
    def __init__(self):
        """Initialize InsightEngine service"""
        # Initialize LLM client
        self.llm_client = LLMClient(
            api_key=settings.INSIGHT_ENGINE_API_KEY or "",
            model_name=settings.INSIGHT_ENGINE_MODEL_NAME or "",
            base_url=settings.INSIGHT_ENGINE_BASE_URL
        )
        
        # Initialize tools
        self.search_db = MediaCrawlerDB()
        self.keyword_optimizer = KeywordOptimizer(self.llm_client)
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Initialize nodes
        self.first_search_node = FirstSearchNode(self.llm_client)
        self.reflection_node = ReflectionNode(self.llm_client)
        self.first_summary_node = FirstSummaryNode(self.llm_client)
        self.reflection_summary_node = ReflectionSummaryNode(self.llm_client)
        self.report_structure_node = ReportStructureNode(self.llm_client, "")
        self.report_formatting_node = ReportFormattingNode(self.llm_client)
        
        # Active research tasks
        self.active_research_tasks: Dict[str, ResearchState] = {}
        
        logger.info("InsightEngine service initialized")
    
    async def search(self, request: SearchRequest) -> SearchResponse:
        """
        Execute search operation
        
        Args:
            request: Search request with tool, query, and parameters
            
        Returns:
            Search response with results
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Executing search with tool: {request.tool_name}, query: {request.query}")
            
            # Execute appropriate search based on tool name
            if request.tool_name == "search_hot_content":
                results = await self.search_db.search_hot_content(
                    time_period=request.time_period or "week",
                    limit=request.limit or 50
                )
            elif request.tool_name == "search_topic_globally":
                results = await self.search_db.search_topic_globally(
                    topic=request.query,
                    limit_per_table=request.limit_per_table or 50
                )
            elif request.tool_name == "search_topic_by_date":
                if not request.start_date or not request.end_date:
                    return SearchResponse(
                        success=False,
                        tool_name=request.tool_name,
                        parameters=request.dict(),
                        results_count=0,
                        error_message="Missing start_date or end_date parameters",
                        execution_time=(datetime.now() - start_time).total_seconds()
                    )
                results = await self.search_db.search_topic_by_date(
                    topic=request.query,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    limit_per_table=request.limit_per_table or 100
                )
            elif request.tool_name == "get_comments_for_topic":
                results = await self.search_db.get_comments_for_topic(
                    topic=request.query,
                    limit=request.limit or 500
                )
            elif request.tool_name == "search_topic_on_platform":
                if not request.platform:
                    return SearchResponse(
                        success=False,
                        tool_name=request.tool_name,
                        parameters=request.dict(),
                        results_count=0,
                        error_message="Missing platform parameter",
                        execution_time=(datetime.now() - start_time).total_seconds()
                    )
                results = await self.search_db.search_topic_on_platform(
                    platform=request.platform,
                    topic=request.query,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    limit=request.limit or 20
                )
            elif request.tool_name == "analyze_sentiment":
                sentiment_result = await self.analyze_sentiment_only(
                    texts=request.texts or request.query,
                    min_confidence=request.min_confidence or 0.5
                )
                return SearchResponse(
                    success=True,
                    tool_name=request.tool_name,
                    parameters=request.dict(),
                    results_count=0,
                    sentiment_analysis=sentiment_result.get("sentiment_analysis"),
                    execution_time=(datetime.now() - start_time).total_seconds()
                )
            else:
                return SearchResponse(
                    success=False,
                    tool_name=request.tool_name,
                    parameters=request.dict(),
                    results_count=0,
                    error_message=f"Unknown tool: {request.tool_name}",
                    execution_time=(datetime.now() - start_time).total_seconds()
                )
            
            # Perform sentiment analysis if requested
            sentiment_analysis = None
            if request.enable_sentiment and hasattr(results, 'results') and results.results:
                sentiment_analysis = await self._perform_sentiment_analysis(results.results)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Handle DBResponse object
            if hasattr(results, 'results'):
                results_list = results.results
                results_count = results.results_count
            else:
                results_list = results if isinstance(results, list) else []
                results_count = len(results_list)
            
            return SearchResponse(
                success=True,
                tool_name=request.tool_name,
                parameters=request.dict(),
                results_count=results_count,
                results=[QueryResult(**result.dict()) for result in results_list],
                sentiment_analysis=sentiment_analysis,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Search operation failed: {str(e)}")
            return SearchResponse(
                success=False,
                tool_name=request.tool_name,
                parameters=request.dict(),
                results_count=0,
                error_message=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def analyze_sentiment_only(self, texts: str, min_confidence: float = 0.5) -> SentimentAnalysisResponse:
        """
        Analyze sentiment of texts
        
        Args:
            texts: Text or list of texts to analyze
            min_confidence: Minimum confidence threshold
            
        Returns:
            Sentiment analysis response
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Analyzing sentiment for {len(texts) if isinstance(texts, list) else 1} text(s)")
            
            # Initialize sentiment analyzer if needed
            if not self.sentiment_analyzer.is_initialized:
                await self.sentiment_analyzer.initialize()
            
            # Perform analysis
            if isinstance(texts, str):
                result = await self.sentiment_analyzer.analyze_single_text(texts)
                response_data = {
                    "success": result.success and result.analysis_performed,
                    "total_analyzed": 1 if result.analysis_performed else 0,
                    "results": [result.__dict__],
                }
                if not result.analysis_performed:
                    response_data["warning"] = result.error_message or "Sentiment analysis not performed"
            else:
                batch_result = await self.sentiment_analyzer.analyze_batch(texts)
                response_data = {
                    "success": batch_result.analysis_performed and batch_result.success_count > 0,
                    "total_analyzed": batch_result.total_processed,
                    "success_count": batch_result.success_count,
                    "failed_count": batch_result.failed_count,
                    "average_confidence": batch_result.average_confidence,
                    "results": [r.__dict__ for r in batch_result.results],
                }
                if not batch_result.analysis_performed:
                    response_data["warning"] = "Sentiment analysis not available"
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return SentimentAnalysisResponse(
                success=True,
                total_analyzed=response_data.get("total_analyzed", 0),
                success_count=response_data.get("success_count"),
                failed_count=response_data.get("failed_count"),
                average_confidence=response_data.get("average_confidence"),
                results=response_data.get("results"),
                warning=response_data.get("warning"),
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return SentimentAnalysisResponse(
                success=False,
                total_analyzed=0,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _perform_sentiment_analysis(self, results: list) -> Optional[Dict[str, Any]]:
        """
        Perform sentiment analysis on search results
        
        Args:
            results: List of search results
            
        Returns:
            Sentiment analysis data or None
        """
        if not results:
            return None
        
        try:
            # Initialize sentiment analyzer if needed
            if not self.sentiment_analyzer.is_initialized:
                await self.sentiment_analyzer.initialize()
            
            # Convert results to format expected by sentiment analyzer
            query_results = []
            for result in results:
                query_results.append({
                    "content": result.title_or_content,
                    "platform": result.platform,
                    "author": result.author_nickname,
                    "url": result.url,
                    "publish_time": result.publish_time.isoformat() if result.publish_time else None,
                })
            
            # Perform analysis
            sentiment_result = await self.sentiment_analyzer.analyze_query_results(
                query_results=query_results,
                text_field="content",
                min_confidence=settings.SENTIMENT_CONFIDENCE_THRESHOLD
            )
            
            return sentiment_result.get("sentiment_analysis")
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return None
    
    async def start_research(self, request: ResearchRequest) -> ResearchResponse:
        """
        Start a new research task
        
        Args:
            request: Research request with query and options
            
        Returns:
            Research response with task ID
        """
        start_time = datetime.now()
        
        try:
            # Generate unique research ID
            research_id = str(uuid.uuid4())
            
            # Create initial state
            state = ResearchState(
                id=research_id,
                query=request.query,
                report_title="",  # Will be set later
                is_completed=False
            )
            
            # Store active research task
            self.active_research_tasks[research_id] = state
            
            # Start research in background
            asyncio.create_task(self._execute_research(research_id, state, request))
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ResearchResponse(
                success=True,
                research_id=research_id,
                state=state.to_dict(),
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Failed to start research: {str(e)}")
            return ResearchResponse(
                success=False,
                error_message=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _execute_research(self, research_id: str, state: ResearchState, request: ResearchRequest):
        """
        Execute the complete research process
        
        Args:
            research_id: Research task ID
            state: Initial research state
            request: Research request with options
        """
        try:
            logger.info(f"Starting research task {research_id}: {request.query}")
            
            # Step 1: Generate report structure
            logger.info(f"[{research_id}] Generating report structure...")
            paragraphs_data = await self.report_structure_node.run()
            
            # Update state with paragraphs
            for paragraph_data in paragraphs_data:
                state.add_paragraph(
                    title=paragraph_data["title"],
                    content=paragraph_data["content"]
                )
            
            # Step 2: Process each paragraph
            total_paragraphs = state.get_total_paragraphs_count()
            
            for i in range(total_paragraphs):
                paragraph = state.get_paragraph(i)
                if not paragraph:
                    continue
                
                logger.info(f"[{research_id}] Processing paragraph {i+1}/{total_paragraphs}: {paragraph.title}")
                
                # Initial search and summary
                search_input = {
                    "title": paragraph.title,
                    "content": paragraph.content
                }
                
                # Generate search query and tool selection
                search_output = await self.first_search_node.run(search_input)
                search_query = search_output.get("search_query", "")
                search_tool = search_output.get("search_tool", "search_topic_globally")
                reasoning = search_output.get("reasoning", "")
                
                logger.info(f"[{research_id}] Search query: {search_query}, tool: {search_tool}")
                
                # Execute search with keyword optimization
                optimized_response = await self.keyword_optimizer.optimize_keywords(
                    original_query=search_query,
                    context=f"using {search_tool} tool"
                )
                
                # Execute search with optimized keywords
                search_kwargs = {}
                if search_tool == "search_topic_by_date":
                    start_date = search_output.get("start_date")
                    end_date = search_output.get("end_date")
                    if start_date and end_date:
                        search_kwargs["start_date"] = start_date
                        search_kwargs["end_date"] = end_date
                elif search_tool == "search_topic_on_platform":
                    platform = search_output.get("platform")
                    if platform:
                        search_kwargs["platform"] = platform
                    start_date = search_output.get("start_date")
                    end_date = search_output.get("end_date")
                    if start_date and end_date:
                        search_kwargs["start_date"] = start_date
                        search_kwargs["end_date"] = end_date
                
                search_response = await self.search(
                    SearchRequest(
                        tool_name=search_tool,
                        query=optimized_response.optimized_keywords[0],  # Use first optimized keyword
                        enable_sentiment=request.enable_sentiment,
                        **search_kwargs
                    )
                )
                
                if search_response.results:
                    # Format search results for LLM
                    formatted_results = format_search_results_for_prompt(
                        search_response.results, settings.MAX_CONTENT_LENGTH
                    )
                else:
                    formatted_results = "No search results found"
                
                # Update search history
                paragraph.research.add_search_results(search_query, search_response.results)
                
                # Generate initial summary
                summary_input = {
                    "title": paragraph.title,
                    "content": paragraph.content,
                    "search_query": search_query,
                    "search_results": formatted_results
                }
                
                # Update state with initial summary
                state = await self.first_summary_node.mutate_state(
                    summary_input, state, paragraph_index=i
                )
                
                # Reflection loops
                max_reflections = request.max_reflections or settings.MAX_REFLECTIONS
                for reflection_i in range(max_reflections):
                    logger.info(f"[{research_id}] Reflection {reflection_i+1}/{max_reflections} for paragraph: {paragraph.title}")
                    
                    # Generate reflection search query
                    reflection_input = {
                        "title": paragraph.title,
                        "content": paragraph.content,
                        "paragraph_latest_state": paragraph.research.latest_summary
                    }
                    
                    reflection_output = await self.reflection_node.run(reflection_input)
                    reflection_query = reflection_output.get("search_query", "")
                    reflection_tool = reflection_output.get("search_tool", "search_topic_globally")
                    reflection_reasoning = reflection_output.get("reasoning", "")
                    
                    logger.info(f"[{research_id}] Reflection query: {reflection_query}, tool: {reflection_tool}")
                    
                    # Execute reflection search with keyword optimization
                    reflection_optimized_response = await self.keyword_optimizer.optimize_keywords(
                        original_query=reflection_query,
                        context=f"using {reflection_tool} tool for reflection"
                    )
                    
                    # Execute reflection search
                    reflection_search_kwargs = {}
                    if reflection_tool == "search_topic_by_date":
                        start_date = reflection_output.get("start_date")
                        end_date = reflection_output.get("end_date")
                        if start_date and end_date:
                            reflection_search_kwargs["start_date"] = start_date
                            reflection_search_kwargs["end_date"] = end_date
                    elif reflection_tool == "search_topic_on_platform":
                        platform = reflection_output.get("platform")
                        if platform:
                            reflection_search_kwargs["platform"] = platform
                            start_date = reflection_output.get("start_date")
                            end_date = reflection_output.get("end_date")
                            if start_date and end_date:
                                reflection_search_kwargs["start_date"] = start_date
                                reflection_search_kwargs["end_date"] = end_date
                    
                    reflection_search_response = await self.search(
                        SearchRequest(
                            tool_name=reflection_tool,
                            query=reflection_optimized_response.optimized_keywords[0],  # Use first optimized keyword
                            enable_sentiment=request.enable_sentiment,
                            **reflection_search_kwargs
                        )
                    )
                    
                    if reflection_search_response.results:
                        # Format reflection search results for LLM
                        reflection_formatted_results = format_search_results_for_prompt(
                            reflection_search_response.results, settings.MAX_CONTENT_LENGTH
                        )
                    else:
                        reflection_formatted_results = "No reflection search results found"
                    
                    # Update search history
                    paragraph.research.add_search_results(reflection_query, reflection_search_response.results)
                    
                    # Generate reflection summary
                    reflection_summary_input = {
                        "title": paragraph.title,
                        "content": paragraph.content,
                        "search_query": reflection_query,
                        "search_results": reflection_formatted_results,
                        "paragraph_latest_state": paragraph.research.latest_summary
                    }
                    
                    # Update state with reflection summary
                    state = await self.reflection_summary_node.mutate_state(
                        reflection_summary_input, state, paragraph_index=i
                    )
                    
                    paragraph.research.increment_reflection()
            
                # Mark paragraph as completed
                paragraph.research.mark_completed()
                
                # Update progress
                progress = state.get_progress_summary()
                logger.info(f"[{research_id}] Paragraph {i+1}/{total_paragraphs} completed. Progress: {progress['progress_percentage']:.1f}%")
            
            # Step 3: Generate final report
            logger.info(f"[{research_id}] Generating final report...")
            
            # Prepare report data
            report_data = []
            for paragraph in state.paragraphs:
                report_data.append({
                    "title": paragraph.title,
                    "paragraph_latest_state": paragraph.research.latest_summary
                })
            
            # Generate final report
            final_report = await self.report_formatting_node.run(report_data)
            
            # Update state with final report
            state.final_report = final_report
            state.mark_completed()
            
            # Update active research task
            self.active_research_tasks[research_id] = state
            
            logger.info(f"[{research_id}] Research completed successfully")
            
        except Exception as e:
            logger.error(f"Research execution failed: {str(e)}")
            # Update state with error
            state.is_completed = True  # Mark as completed to avoid infinite loops
            self.active_research_tasks[research_id] = state
    
    async def get_research_progress(self, research_id: str) -> ProgressResponse:
        """
        Get progress of a research task
        
        Args:
            research_id: Research task ID
            
        Returns:
            Progress response with current status
        """
        if research_id not in self.active_research_tasks:
            return ProgressResponse(
                research_id=research_id,
                total_paragraphs=0,
                completed_paragraphs=0,
                progress_percentage=0.0,
                is_completed=False,
                error_message="Research task not found",
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            )
        
        state = self.active_research_tasks[research_id]
        progress = state.get_progress_summary()
        
        return ProgressResponse(
            research_id=research_id,
            total_paragraphs=progress["total_paragraphs"],
            completed_paragraphs=progress["completed_paragraphs"],
            progress_percentage=progress["progress_percentage"],
            is_completed=progress["is_completed"],
            current_paragraph=state.get_paragraph(state.get_completed_paragraphs_count() - 1).title if state.get_completed_paragraphs_count() > 0 else None,
            created_at=progress.get("created_at", datetime.utcnow().isoformat()),
            updated_at=progress.get("updated_at", datetime.utcnow().isoformat())
        )
    
    async def get_research_state(self, research_id: str) -> ResearchResponse:
        """
        Get complete state of a research task
        
        Args:
            research_id: Research task ID
            
        Returns:
            Research response with current state
        """
        if research_id not in self.active_research_tasks:
            return ResearchResponse(
                research_id=research_id,
                error_message="Research task not found"
            )
        
        state = self.active_research_tasks[research_id]
        
        return ResearchResponse(
            research_id=research_id,
            state=state.to_dict(),
            is_completed=state.is_completed
        )
    
    async def get_active_research_tasks(self) -> Dict[str, ResearchState]:
        """
        Get all active research tasks
        
        Returns:
            Dictionary of active research tasks
        """
        return self.active_research_tasks
    
    async def get_engine_status(self) -> Dict[str, Any]:
        """
        Get InsightEngine status information
        
        Returns:
            Status information dictionary
        """
        try:
            return {
                "status": "healthy",
                "model_info": self.llm_client.get_model_info(),
                "database_connected": True,  # Simplified check
                "active_research_tasks": len(self.active_research_tasks)
            }
            
        except Exception as e:
            logger.error(f"Failed to get engine status: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e)
            }
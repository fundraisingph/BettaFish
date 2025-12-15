"""
Database search tools for InsightEngine
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Literal
import logging
logger = logging.getLogger(__name__)

from ..utils.db import db_manager
from ..models.schemas import DBResponse, QueryResult


class MediaCrawlerDB:
    """Database search tool client for InsightEngine"""
    
    def __init__(self):
        """Initialize database search client"""
        self.db_manager = db_manager
        
    async def search_hot_content(
        self,
        time_period: Literal['24h', 'week', 'year'] = 'week',
        limit: int = 50
    ) -> DBResponse:
        """
        Search for hot content within specified time period
        
        Args:
            time_period: Time period ('24h', 'week', 'year')
            limit: Maximum number of results
            
        Returns:
            DBResponse with search results
        """
        params_for_log = {'time_period': time_period, 'limit': limit}
        logger.info(f"--- TOOL: Search Hot Content (params: {params_for_log}) ---")
        
        try:
            results = await db_manager.search_hot_content(time_period, limit)
            return DBResponse(
                tool_name="search_hot_content",
                parameters=params_for_log,
                results=results,
                results_count=len(results)
            )
        except Exception as e:
            logger.error(f"Hot content search error: {str(e)}")
            return DBResponse(
                tool_name="search_hot_content",
                parameters=params_for_log,
                results=[],
                results_count=0,
                error_message=str(e)
            )
    
    async def search_topic_globally(self, topic: str, limit_per_table: int = 100) -> DBResponse:
        """
        Global topic search across all platforms
        
        Args:
            topic: Topic to search
            limit_per_table: Maximum results per table
            
        Returns:
            DBResponse with search results
        """
        params_for_log = {'topic': topic, 'limit_per_table': limit_per_table}
        logger.info(f"--- TOOL: Global Topic Search (params: {params_for_log}) ---")
        
        try:
            results = await db_manager.search_topic_globally(topic, limit_per_table)
            return DBResponse(
                tool_name="search_topic_globally",
                parameters=params_for_log,
                results=results,
                results_count=len(results)
            )
        except Exception as e:
            logger.error(f"Global topic search error: {str(e)}")
            return DBResponse(
                tool_name="search_topic_globally",
                parameters=params_for_log,
                results=[],
                results_count=0,
                error_message=str(e)
            )
    
    async def search_topic_by_date(
        self,
        topic: str,
        start_date: str,
        end_date: str,
        limit_per_table: int = 100
    ) -> DBResponse:
        """
        Search topic by date range
        
        Args:
            topic: Topic to search
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit_per_table: Maximum results per table
            
        Returns:
            DBResponse with search results
        """
        params_for_log = {
            'topic': topic,
            'start_date': start_date,
            'end_date': end_date,
            'limit_per_table': limit_per_table
        }
        logger.info(f"--- TOOL: Date-based Topic Search (params: {params_for_log}) ---")
        
        try:
            results = await db_manager.search_topic_by_date(topic, start_date, end_date, limit_per_table)
            return DBResponse(
                tool_name="search_topic_by_date",
                parameters=params_for_log,
                results=results,
                results_count=len(results)
            )
        except Exception as e:
            logger.error(f"Date-based topic search error: {str(e)}")
            return DBResponse(
                tool_name="search_topic_by_date",
                parameters=params_for_log,
                results=[],
                results_count=0,
                error_message=str(e)
            )
    
    async def get_comments_for_topic(self, topic: str, limit: int = 500) -> DBResponse:
        """
        Get comments for a specific topic
        
        Args:
            topic: Topic to search
            limit: Maximum number of comments
            
        Returns:
            DBResponse with comment results
        """
        params_for_log = {'topic': topic, 'limit': limit}
        logger.info(f"--- TOOL: Get Topic Comments (params: {params_for_log}) ---")
        
        try:
            results = await db_manager.get_comments_for_topic(topic, limit)
            return DBResponse(
                tool_name="get_comments_for_topic",
                parameters=params_for_log,
                results=results,
                results_count=len(results)
            )
        except Exception as e:
            logger.error(f"Comments search error: {str(e)}")
            return DBResponse(
                tool_name="get_comments_for_topic",
                parameters=params_for_log,
                results=[],
                results_count=0,
                error_message=str(e)
            )
    
    async def search_topic_on_platform(
        self,
        platform: Literal['bilibili', 'weibo', 'douyin', 'kuaishou', 'xhs', 'zhihu', 'tieba'],
        topic: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 20
    ) -> DBResponse:
        """
        Search topic on specific platform
        
        Args:
            platform: Platform to search
            topic: Topic to search
            start_date: Optional start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            limit: Maximum number of results
            
        Returns:
            DBResponse with search results
        """
        params_for_log = {
            'platform': platform,
            'topic': topic,
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit
        }
        logger.info(f"--- TOOL: Platform-specific Search (params: {params_for_log}) ---")
        
        try:
            results = await db_manager.search_topic_on_platform(
                platform, topic, start_date, end_date, limit
            )
            return DBResponse(
                tool_name="search_topic_on_platform",
                parameters=params_for_log,
                results=results,
                results_count=len(results)
            )
        except Exception as e:
            logger.error(f"Platform search error: {str(e)}")
            return DBResponse(
                tool_name="search_topic_on_platform",
                parameters=params_for_log,
                results=[],
                results_count=0,
                error_message=str(e)
            )
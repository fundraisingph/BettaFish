"""
QueryEngine Search Tool
"""
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
import aiohttp
import async_timeout

from ..llms.base import LLMClient
from ..utils.config import query_config

logger = logging.getLogger(__name__)

class SearchTool:
    """Search tool for QueryEngine"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.config = query_config
        self.session = None
    
    async def _get_session(self):
        """Get HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def search(
        self,
        query: str,
        search_type: str = "comprehensive",
        max_results: int = 10,
        search_apis: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Perform search using available APIs"""
        try:
            # Determine which APIs to use
            if not search_apis:
                search_apis = self.config.get_available_search_apis()
            
            if not search_apis:
                logger.warning("No search APIs available")
                return []
            
            # Perform searches in parallel
            tasks = []
            for api_name in search_apis:
                if self.config.is_search_api_available(api_name):
                    task = self._search_with_api(api_name, query, max_results)
                    tasks.append(task)
            
            if not tasks:
                logger.warning("No valid search APIs available")
                return []
            
            # Wait for all searches to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine and rank results
            all_results = []
            for result in results:
                if isinstance(result, list):
                    all_results.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Search error: {str(result)}")
            
            # Rank and limit results
            ranked_results = self._rank_results(all_results, query)
            return ranked_results[:max_results]
            
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            raise
    
    async def _search_with_api(
        self,
        api_name: str,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Search with specific API"""
        try:
            api_config = self.config.get_search_api_config(api_name)
            if not api_config:
                raise ValueError(f"API {api_name} not configured")
            
            if api_name == "tavily":
                return await self._search_tavily(query, max_results, api_config)
            elif api_name == "bocha":
                return await self._search_bocha(query, max_results, api_config)
            elif api_name == "anspire":
                return await self._search_anspire(query, max_results, api_config)
            else:
                raise ValueError(f"Unknown API: {api_name}")
                
        except Exception as e:
            logger.error(f"Error searching with {api_name}: {str(e)}")
            raise
    
    async def _search_tavily(
        self,
        query: str,
        max_results: int,
        api_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search with Tavily API"""
        try:
            session = await self._get_session()
            
            url = f"{api_config['base_url']}/search"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_config['api_key']}"
            }
            
            payload = {
                "api_key": api_config['api_key'],
                "query": query,
                "search_depth": "basic",
                "include_answer": True,
                "include_raw_content": True,
                "max_results": min(max_results, api_config.get('max_results', 10))
            }
            
            async with async_timeout.timeout(api_config.get('timeout', 10)):
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Tavily API error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    
                    results = []
                    if data.get("results"):
                        for item in data["results"]:
                            results.append({
                                "title": item.get("title", ""),
                                "content": item.get("content", ""),
                                "url": item.get("url", ""),
                                "score": item.get("score", 0.5),
                                "source": "tavily",
                                "metadata": {
                                    "published_date": item.get("published_date"),
                                    "score": item.get("score"),
                                    "raw_content": item.get("raw_content", "")
                                }
                            })
                    
                    return results
                    
        except asyncio.TimeoutError:
            logger.error("Tavily API timeout")
            return []
        except Exception as e:
            logger.error(f"Error searching with Tavily: {str(e)}")
            return []
    
    async def _search_bocha(
        self,
        query: str,
        max_results: int,
        api_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search with Bocha API"""
        try:
            session = await self._get_session()
            
            url = f"{api_config['base_url']}/search"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_config['api_key']}"
            }
            
            payload = {
                "query": query,
                "max_results": min(max_results, api_config.get('max_results', 10)),
                "include_images": False,
                "include_videos": False
            }
            
            async with async_timeout.timeout(api_config.get('timeout', 10)):
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Bocha API error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    
                    results = []
                    if data.get("results"):
                        for item in data["results"]:
                            results.append({
                                "title": item.get("title", ""),
                                "content": item.get("content", ""),
                                "url": item.get("url", ""),
                                "score": item.get("relevance_score", 0.5),
                                "source": "bocha",
                                "metadata": {
                                    "relevance_score": item.get("relevance_score"),
                                    "snippet": item.get("snippet", ""),
                                    "domain": item.get("domain", "")
                                }
                            })
                    
                    return results
                    
        except asyncio.TimeoutError:
            logger.error("Bocha API timeout")
            return []
        except Exception as e:
            logger.error(f"Error searching with Bocha: {str(e)}")
            return []
    
    async def _search_anspire(
        self,
        query: str,
        max_results: int,
        api_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search with Anspire API"""
        try:
            session = await self._get_session()
            
            url = f"{api_config['base_url']}/search"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_config['api_key']}"
            }
            
            payload = {
                "q": query,
                "num": min(max_results, api_config.get('max_results', 10)),
                "hl": "en",
                "gl": "us"
            }
            
            async with async_timeout.timeout(api_config.get('timeout', 10)):
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Anspire API error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    
                    results = []
                    if data.get("items"):
                        for item in data["items"]:
                            results.append({
                                "title": item.get("title", ""),
                                "content": item.get("snippet", ""),
                                "url": item.get("link", ""),
                                "score": item.get("relevance_score", 0.5),
                                "source": "anspire",
                                "metadata": {
                                    "relevance_score": item.get("relevance_score"),
                                    "snippet": item.get("snippet", ""),
                                    "display_link": item.get("displayLink", ""),
                                    "formatted_url": item.get("formattedUrl", "")
                                }
                            })
                    
                    return results
                    
        except asyncio.TimeoutError:
            logger.error("Anspire API timeout")
            return []
        except Exception as e:
            logger.error(f"Error searching with Anspire: {str(e)}")
            return []
    
    def _rank_results(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """Rank search results by relevance"""
        try:
            # Simple ranking based on score and query relevance
            for result in results:
                # Normalize score to 0-1 range
                score = result.get("score", 0.5)
                if score > 1:
                    score = score / 100
                
                # Calculate query relevance (simple keyword matching)
                title = result.get("title", "").lower()
                content = result.get("content", "").lower()
                query_lower = query.lower()
                query_words = query_lower.split()
                
                # Count keyword matches
                title_matches = sum(1 for word in query_words if word in title)
                content_matches = sum(1 for word in query_words if word in content)
                
                # Calculate relevance score
                query_relevance = (title_matches * 2 + content_matches) / (len(query_words) * 3)
                
                # Combine scores
                combined_score = (score * 0.6) + (query_relevance * 0.4)
                result["combined_score"] = combined_score
            
            # Sort by combined score
            ranked_results = sorted(results, key=lambda x: x.get("combined_score", 0), reverse=True)
            
            return ranked_results
            
        except Exception as e:
            logger.error(f"Error ranking results: {str(e)}")
            return results
    
    async def generate_search_queries(
        self,
        query: str,
        num_queries: int = 5,
        search_type: str = "comprehensive"
    ) -> List[str]:
        """Generate multiple search queries"""
        try:
            return await self.llm_client.generate_search_queries(
                query=query,
                num_queries=num_queries,
                search_type=search_type
            )
        except Exception as e:
            logger.error(f"Error generating search queries: {str(e)}")
            return [query]  # Return original query as fallback
    
    async def summarize_search_results(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        summary_type: str = "comprehensive"
    ) -> str:
        """Summarize search results"""
        try:
            return await self.llm_client.summarize_search_results(
                query=query,
                search_results=search_results,
                summary_type=summary_type
            )
        except Exception as e:
            logger.error(f"Error summarizing search results: {str(e)}")
            return "Error summarizing search results"
    
    async def extract_key_insights(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        num_insights: int = 5
    ) -> List[str]:
        """Extract key insights from search results"""
        try:
            return await self.llm_client.extract_key_insights(
                query=query,
                search_results=search_results,
                num_insights=num_insights
            )
        except Exception as e:
            logger.error(f"Error extracting key insights: {str(e)}")
            return []
    
    async def search_and_analyze(
        self,
        query: str,
        search_type: str = "comprehensive",
        max_results: int = 10,
        include_summary: bool = True,
        include_insights: bool = True
    ) -> Dict[str, Any]:
        """Search and analyze results"""
        try:
            # Perform search
            search_results = await self.search(
                query=query,
                search_type=search_type,
                max_results=max_results
            )
            
            result = {
                "query": query,
                "search_type": search_type,
                "results": search_results,
                "total_results": len(search_results)
            }
            
            # Add summary if requested
            if include_summary and search_results:
                result["summary"] = await self.summarize_search_results(
                    query=query,
                    search_results=search_results,
                    summary_type=search_type
                )
            
            # Add insights if requested
            if include_insights and search_results:
                result["insights"] = await self.extract_key_insights(
                    query=query,
                    search_results=search_results
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in search and analyze: {str(e)}")
            raise
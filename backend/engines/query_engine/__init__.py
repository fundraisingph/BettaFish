"""
QueryEngine Module
"""
from .services.query_service import QueryService
from .state.state import ResearchState
from .models.schemas import (
    QuerySearchRequest,
    QuerySearchResponse,
    QueryOptimizeRequest,
    QueryOptimizeResponse,
    QueryResearchRequest,
    QueryResearchResponse,
    ProgressResponse
)

# Deep Search Agent (main class)
class DeepSearchAgent:
    """Main agent class for QueryEngine"""
    
    def __init__(self):
        self.query_service = QueryService()
    
    async def search(self, query: str, **kwargs):
        """Perform search"""
        return await self.query_service.execute_search(query, **kwargs)
    
    async def optimize(self, query: str, **kwargs):
        """Optimize query"""
        return await self.query_service.execute_optimize(query, **kwargs)
    
    async def research(self, query: str, **kwargs):
        """Perform research"""
        return await self.query_service.execute_research(query, **kwargs)

__all__ = [
    "DeepSearchAgent",
    "ResearchState",
    "QueryService",
    "QuerySearchRequest",
    "QuerySearchResponse",
    "QueryOptimizeRequest",
    "QueryOptimizeResponse",
    "QueryResearchRequest",
    "QueryResearchResponse",
    "ProgressResponse"
]

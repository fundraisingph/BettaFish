"""
QueryEngine Search Node
"""
import logging
from typing import Dict, List, Any, Optional

from .base_node import BaseNode
from ..tools.search import SearchTool
from ..utils.config import query_config

logger = logging.getLogger(__name__)

class SearchNode(BaseNode):
    """Search node for QueryEngine"""
    
    def __init__(self, llm_client=None):
        super().__init__(llm_client)
        self.search_tool = SearchTool(llm_client)
        self.config = query_config
    
    def validate_inputs(self, query: str, search_type: str = "comprehensive", max_results: int = 10) -> bool:
        """Validate search inputs"""
        if not query or not isinstance(query, str):
            return False
        
        if search_type not in ["comprehensive", "targeted", "broad", "specific"]:
            return False
        
        if not isinstance(max_results, int) or max_results <= 0:
            return False
        
        return True
    
    async def run(self, query: str, search_type: str = "comprehensive", max_results: int = 10) -> Dict[str, Any]:
        """Run search node"""
        try:
            self.log_execution(f"Starting search for query: {query}, type: {search_type}, max_results: {max_results}")
            
            # Generate multiple search queries for comprehensive search
            if search_type == "comprehensive":
                search_queries = await self.search_tool.generate_search_queries(
                    query=query,
                    num_queries=3,
                    search_type=search_type
                )
                
                # Perform searches for all queries
                all_results = []
                for search_query in search_queries:
                    results = await self.search_tool.search(
                        query=search_query,
                        search_type="targeted",
                        max_results=max_results // len(search_queries) + 1
                    )
                    all_results.extend(results)
                
                # Remove duplicates and rank
                unique_results = self._remove_duplicates(all_results)
                ranked_results = self._rank_results(unique_results, query)
                
                return {
                    "query": query,
                    "search_type": search_type,
                    "search_queries": search_queries,
                    "results": ranked_results[:max_results],
                    "total_results": len(ranked_results),
                    "unique_results": len(unique_results)
                }
            
            else:
                # Single query search for other types
                results = await self.search_tool.search(
                    query=query,
                    search_type=search_type,
                    max_results=max_results
                )
                
                return {
                    "query": query,
                    "search_type": search_type,
                    "search_queries": [query],
                    "results": results,
                    "total_results": len(results),
                    "unique_results": len(results)
                }
                
        except Exception as e:
            self.log_execution(f"Search failed: {str(e)}", "ERROR")
            raise
    
    async def run_with_analysis(
        self,
        query: str,
        search_type: str = "comprehensive",
        max_results: int = 10,
        include_summary: bool = True,
        include_insights: bool = True
    ) -> Dict[str, Any]:
        """Run search with analysis"""
        try:
            # Get basic search results
            search_result = await self.run(query, search_type, max_results)
            
            if not search_result["results"]:
                return search_result
            
            # Add analysis if requested
            if include_summary:
                search_result["summary"] = await self.search_tool.summarize_search_results(
                    query=query,
                    search_results=search_result["results"],
                    summary_type=search_type
                )
            
            if include_insights:
                search_result["insights"] = await self.search_tool.extract_key_insights(
                    query=query,
                    search_results=search_result["results"]
                )
            
            return search_result
            
        except Exception as e:
            self.log_execution(f"Search with analysis failed: {str(e)}", "ERROR")
            raise
    
    async def run_iterative_search(
        self,
        query: str,
        search_type: str = "comprehensive",
        max_results: int = 10,
        iterations: int = 3
    ) -> Dict[str, Any]:
        """Run iterative search with refinement"""
        try:
            all_results = []
            search_queries = [query]
            
            for iteration in range(iterations):
                self.log_execution(f"Iterative search iteration {iteration + 1}/{iterations}")
                
                # Use latest query for this iteration
                current_query = search_queries[-1]
                
                # Perform search
                results = await self.search_tool.search(
                    query=current_query,
                    search_type="targeted",
                    max_results=max_results // iterations + 1
                )
                
                all_results.extend(results)
                
                # Generate refined query for next iteration
                if iteration < iterations - 1 and results:
                    # Analyze results and generate refined query
                    refined_query = await self._generate_refined_query(
                        original_query=query,
                        current_query=current_query,
                        results=results,
                        iteration=iteration + 1
                    )
                    
                    search_queries.append(refined_query)
            
            # Remove duplicates and rank all results
            unique_results = self._remove_duplicates(all_results)
            ranked_results = self._rank_results(unique_results, query)
            
            return {
                "query": query,
                "search_type": search_type,
                "iterations": iterations,
                "search_queries": search_queries,
                "results": ranked_results[:max_results],
                "total_results": len(ranked_results),
                "unique_results": len(unique_results),
                "all_results_count": len(all_results)
            }
            
        except Exception as e:
            self.log_execution(f"Iterative search failed: {str(e)}", "ERROR")
            raise
    
    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on URL"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
            elif not url:  # Keep results without URLs
                unique_results.append(result)
        
        return unique_results
    
    def _rank_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rank results by relevance to query"""
        try:
            # Calculate relevance scores
            query_words = set(query.lower().split())
            
            for result in results:
                title = result.get("title", "").lower()
                content = result.get("content", "").lower()
                url = result.get("url", "").lower()
                
                # Count keyword matches
                title_matches = sum(1 for word in query_words if word in title)
                content_matches = sum(1 for word in query_words if word in content)
                url_matches = sum(1 for word in query_words if word in url)
                
                # Calculate relevance score
                relevance_score = (title_matches * 3 + content_matches * 2 + url_matches) / (len(query_words) * 6)
                
                # Combine with existing score
                existing_score = result.get("combined_score", result.get("score", 0.5))
                combined_score = (existing_score * 0.6) + (relevance_score * 0.4)
                
                result["relevance_score"] = relevance_score
                result["combined_score"] = combined_score
            
            # Sort by combined score
            ranked_results = sorted(results, key=lambda x: x.get("combined_score", 0), reverse=True)
            
            return ranked_results
            
        except Exception as e:
            self.log_execution(f"Error ranking results: {str(e)}", "WARNING")
            return results
    
    async def _generate_refined_query(
        self,
        original_query: str,
        current_query: str,
        results: List[Dict[str, Any]],
        iteration: int
    ) -> str:
        """Generate refined query based on search results"""
        try:
            # Get insights from current results
            insights = await self.search_tool.extract_key_insights(
                query=current_query,
                search_results=results,
                num_insights=3
            )
            
            # Generate refined query
            system_prompt = f"""
            You are a query refinement expert. Based on the search results and insights from iteration {iteration},
            generate a refined query that will yield better results for the original query.
            
            Return a JSON object with the following structure:
            {{
                "refined_query": "the refined query",
                "refinement_rationale": "explanation of how the query was refined",
                "focus_areas": ["area1", "area2", "area3"]
            }}
            """
            
            insights_text = "\n".join(f"- {insight}" for insight in insights)
            
            prompt = f"""
            Original Query: {original_query}
            Current Query: {current_query}
            Iteration: {iteration}
            
            Search Results Insights:
            {insights_text}
            
            Generate a refined query that addresses gaps or limitations in the current search results.
            The refined query should:
            1. Maintain the original intent
            2. Address missing information identified in insights
            3. Use different terminology or angles
            4. Be more specific or broader as needed
            """
            
            response = await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            return response.get("refined_query", current_query)
            
        except Exception as e:
            self.log_execution(f"Error generating refined query: {str(e)}", "WARNING")
            return current_query

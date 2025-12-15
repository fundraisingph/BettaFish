"""
Keyword optimizer for InsightEngine
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import logging
logger = logging.getLogger(__name__)

from ..llms.base import LLMClient
from ..utils.config import settings


@dataclass
class OptimizationResponse:
    """Response from keyword optimization"""
    optimized_keywords: List[str]
    reasoning: str


class KeywordOptimizer:
    """Keyword optimization middleware for better search results"""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize keyword optimizer
        
        Args:
            llm_client: LLM client for optimization
        """
        self.llm_client = llm_client
    
    async def optimize_keywords(self, original_query: str, context: str = "") -> OptimizationResponse:
        """
        Optimize search keywords for better results
        
        Args:
            original_query: Original search query
            context: Context of the search (e.g., "using search_topic_globally tool")
            
        Returns:
            OptimizationResponse with optimized keywords and reasoning
        """
        system_prompt = f"""
You are a search optimization expert specializing in social media and public opinion analysis.
Your task is to optimize search queries to get the most relevant and comprehensive results from social media databases.

Context: {context}

Optimization Principles:
1. **Use Netizen Language**: Convert formal terms to how real users talk
2. **Include Synonyms and Variations**: Add related terms, abbreviations, slang
3. **Platform-Specific Terms**: Consider how different platforms express the same concept
4. **Emotional and Opinion Words**: Include terms that capture sentiments and viewpoints
5. **Event-Specific Language**: Use names, dates, locations related to the topic

Input: "{original_query}"

Please provide 3-5 optimized search terms that will yield the best results from social media databases.

Output format:
{{
  "optimized_keywords": ["term1", "term2", "term3"],
  "reasoning": "Explanation of why these terms were chosen"
}}
"""
        
        try:
            response = self.llm_client.invoke(system_prompt, "")
            
            import json
            result = json.loads(response)
            
            optimized_keywords = result.get("optimized_keywords", [])
            reasoning = result.get("reasoning", "")
            
            logger.info(f"Keyword optimization: '{original_query}' -> {optimized_keywords}")
            logger.info(f"Optimization reasoning: {reasoning}")
            
            return OptimizationResponse(
                optimized_keywords=optimized_keywords,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Keyword optimization failed: {str(e)}")
            # Fallback to original query
            return OptimizationResponse(
                optimized_keywords=[original_query],
                reasoning=f"Optimization failed, using original query: {str(e)}"
            )
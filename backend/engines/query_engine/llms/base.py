"""
QueryEngine LLM Client
"""
import json
import logging
from typing import Dict, List, Optional, Any, Union
from openai import AsyncOpenAI

from core.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """LLM client for QueryEngine"""
    
    def __init__(self, model: Optional[str] = None):
        self.model = model or settings.QUERY_ENGINE_LLM_MODEL
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE
        )
        self.timeout = settings.LLM_TIMEOUT
    
    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a response from the LLM"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "timeout": self.timeout
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            if response_format:
                kwargs["response_format"] = response_format
            
            response = await self.client.chat.completions.create(**kwargs)
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    async def generate_json_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a JSON response from the LLM"""
        try:
            response = await self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error generating JSON response: {str(e)}")
            raise
    
    async def generate_structured_response(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a structured response from the LLM"""
        try:
            # Create a system prompt that includes the schema
            schema_prompt = f"""
            Please respond with a JSON object that follows this exact schema:
            {json.dumps(response_schema, indent=2)}
            
            Your response must be valid JSON that matches this schema structure.
            """
            
            if system_prompt:
                system_prompt = f"{system_prompt}\n\n{schema_prompt}"
            else:
                system_prompt = schema_prompt
            
            response = await self.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating structured response: {str(e)}")
            raise
    
    async def analyze_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze a query to extract key information"""
        try:
            system_prompt = """
            You are a query analysis expert. Analyze the given query and extract key information.
            Return a JSON object with the following structure:
            {
                "query_type": "informational|navigational|transactional|commercial",
                "intent": "brief description of user intent",
                "keywords": ["list", "of", "key", "keywords"],
                "entities": ["list", "of", "named", "entities"],
                "sentiment": "positive|negative|neutral",
                "complexity": "simple|moderate|complex",
                "search_strategy": "recommended search strategy"
            }
            """
            
            context_str = ""
            if context:
                context_str = f"\nContext: {json.dumps(context, indent=2)}"
            
            prompt = f"""
            Analyze this query: {query}
            {context_str}
            
            Provide a detailed analysis of the query.
            """
            
            return await self.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            logger.error(f"Error analyzing query: {str(e)}")
            raise
    
    async def optimize_query(
        self,
        query: str,
        optimization_type: str = "keyword",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize a query for better search results"""
        try:
            system_prompt = f"""
            You are a query optimization expert. Optimize the given query for better search results.
            The optimization type is: {optimization_type}
            
            Return a JSON object with the following structure:
            {{
                "optimized_query": "the optimized query",
                "original_query": "the original query",
                "optimization_type": "type of optimization applied",
                "improvements": ["list", "of", "improvements"],
                "confidence_score": 0.95,
                "additional_suggestions": ["alternative", "queries"],
                "metadata": {{
                    "keyword_density": 0.8,
                    "query_length": "short|medium|long",
                    "specificity": "low|medium|high"
                }}
            }}
            """
            
            context_str = ""
            if context:
                context_str = f"\nContext: {json.dumps(context, indent=2)}"
            
            prompt = f"""
            Optimize this query: {query}
            {context_str}
            
            Provide an optimized version of the query that will yield better search results.
            """
            
            return await self.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            logger.error(f"Error optimizing query: {str(e)}")
            raise
    
    async def generate_search_queries(
        self,
        query: str,
        num_queries: int = 5,
        search_type: str = "comprehensive"
    ) -> List[str]:
        """Generate multiple search queries for comprehensive research"""
        try:
            system_prompt = f"""
            You are a search query generation expert. Generate {num_queries} diverse search queries
            for comprehensive research on the given topic. The search type is: {search_type}
            
            Return a JSON object with the following structure:
            {{
                "queries": ["query1", "query2", "query3", "query4", "query5"],
                "rationale": "brief explanation of query diversity"
            }}
            """
            
            prompt = f"""
            Generate {num_queries} diverse search queries for comprehensive research on: {query}
            
            The queries should:
            1. Cover different aspects of the topic
            2. Use different keyword combinations
            3. Vary in specificity and scope
            4. Include both broad and focused queries
            5. Consider different perspectives and angles
            """
            
            response = await self.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            return response.get("queries", [])
            
        except Exception as e:
            logger.error(f"Error generating search queries: {str(e)}")
            raise
    
    async def summarize_search_results(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        summary_type: str = "comprehensive"
    ) -> str:
        """Summarize search results"""
        try:
            system_prompt = f"""
            You are a search result summarization expert. Summarize the given search results
            in response to the query. The summary type is: {summary_type}
            
            Create a comprehensive summary that:
            1. Directly addresses the original query
            2. Synthesizes information from multiple sources
            3. Identifies key themes and patterns
            4. Highlights important findings
            5. Notes any contradictions or gaps
            """
            
            # Format search results
            results_text = ""
            for i, result in enumerate(search_results, 1):
                results_text += f"\n{i}. Title: {result.get('title', 'N/A')}\n"
                results_text += f"   Content: {result.get('content', 'N/A')}\n"
                if result.get('url'):
                    results_text += f"   URL: {result['url']}\n"
                results_text += "\n"
            
            prompt = f"""
            Original Query: {query}
            
            Search Results:
            {results_text}
            
            Provide a comprehensive summary of these search results that directly addresses the query.
            """
            
            return await self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=1000
            )
            
        except Exception as e:
            logger.error(f"Error summarizing search results: {str(e)}")
            raise
    
    async def extract_key_insights(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        num_insights: int = 5
    ) -> List[str]:
        """Extract key insights from search results"""
        try:
            system_prompt = f"""
            You are an insight extraction expert. Extract the {num_insights} most important insights
            from the search results in response to the query.
            
            Return a JSON object with the following structure:
            {{
                "insights": [
                    "insight1: detailed explanation",
                    "insight2: detailed explanation",
                    "insight3: detailed explanation",
                    "insight4: detailed explanation",
                    "insight5: detailed explanation"
                ],
                "confidence_scores": [0.9, 0.8, 0.7, 0.6, 0.5]
            }}
            """
            
            # Format search results
            results_text = ""
            for i, result in enumerate(search_results, 1):
                results_text += f"\n{i}. Title: {result.get('title', 'N/A')}\n"
                results_text += f"   Content: {result.get('content', 'N/A')}\n"
                if result.get('url'):
                    results_text += f"   URL: {result['url']}\n"
                results_text += "\n"
            
            prompt = f"""
            Original Query: {query}
            
            Search Results:
            {results_text}
            
            Extract the {num_insights} most important insights from these search results.
            Each insight should be a complete sentence that provides valuable information.
            """
            
            response = await self.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            return response.get("insights", [])
            
        except Exception as e:
            logger.error(f"Error extracting key insights: {str(e)}")
            raise

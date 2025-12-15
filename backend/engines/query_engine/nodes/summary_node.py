"""
QueryEngine Summary Node
"""
import logging
from typing import Dict, List, Any, Optional

from .base_node import BaseNode

logger = logging.getLogger(__name__)

class SummaryNode(BaseNode):
    """Summary node for QueryEngine"""
    
    def validate_inputs(self, query: str, search_results: List[Dict[str, Any]], iteration: int = 1) -> bool:
        """Validate summary inputs"""
        if not query or not isinstance(query, str):
            return False
        
        if not search_results or not isinstance(search_results, list):
            return False
        
        if not isinstance(iteration, int) or iteration <= 0:
            return False
        
        return True
    
    async def run(self, query: str, search_results: List[Dict[str, Any]], iteration: int = 1) -> str:
        """Run summary node"""
        try:
            self.log_execution(f"Generating summary for iteration {iteration}, query: {query}")
            
            if not search_results:
                return f"No search results found for query: {query}"
            
            # Generate summary based on iteration type
            if iteration == 1:
                return await self._generate_initial_summary(query, search_results)
            else:
                return await self._generate_iteration_summary(query, search_results, iteration)
                
        except Exception as e:
            self.log_execution(f"Summary generation failed: {str(e)}", "ERROR")
            raise
    
    async def run_with_insights(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        iteration: int = 1,
        include_insights: bool = True,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """Run summary with additional insights"""
        try:
            # Generate basic summary
            summary = await self.run(query, search_results, iteration)
            
            result = {
                "query": query,
                "iteration": iteration,
                "summary": summary,
                "results_count": len(search_results)
            }
            
            # Add insights if requested
            if include_insights:
                result["insights"] = await self._extract_insights(query, search_results)
            
            # Add recommendations if requested
            if include_recommendations:
                result["recommendations"] = await self._generate_recommendations(query, search_results, iteration)
            
            return result
            
        except Exception as e:
            self.log_execution(f"Summary with insights failed: {str(e)}", "ERROR")
            raise
    
    async def _generate_initial_summary(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate initial summary"""
        try:
            system_prompt = """
            You are a search results summarization expert. Generate a comprehensive summary of search results
            that directly addresses the user's query.
            
            The summary should:
            1. Directly address the original query
            2. Synthesize information from multiple sources
            3. Identify key themes and patterns
            4. Highlight important findings
            5. Note any contradictions or gaps
            6. Be well-structured and easy to read
            7. Be comprehensive but concise
            """
            
            # Format search results
            results_text = self._format_search_results(search_results)
            
            prompt = f"""
            Original Query: {query}
            
            Search Results:
            {results_text}
            
            Generate a comprehensive summary that directly addresses the query based on these search results.
            """
            
            return await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=1000
            )
            
        except Exception as e:
            self.log_execution(f"Error generating initial summary: {str(e)}", "ERROR")
            raise
    
    async def _generate_iteration_summary(self, query: str, search_results: List[Dict[str, Any]], iteration: int) -> str:
        """Generate iteration summary"""
        try:
            system_prompt = f"""
            You are a search results summarization expert. Generate a summary for iteration {iteration}
            of a multi-iteration research process.
            
            The summary should:
            1. Focus on new information discovered in this iteration
            2. Compare with previous findings (if applicable)
            3. Identify gaps or areas needing further investigation
            4. Highlight unique insights from this iteration
            5. Suggest directions for next iteration
            6. Be concise but informative
            """
            
            # Format search results
            results_text = self._format_search_results(search_results)
            
            prompt = f"""
            Original Query: {query}
            Iteration: {iteration}
            
            Search Results:
            {results_text}
            
            Generate a summary for this iteration that focuses on new discoveries and insights.
            """
            
            return await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=800
            )
            
        except Exception as e:
            self.log_execution(f"Error generating iteration summary: {str(e)}", "ERROR")
            raise
    
    async def _extract_insights(self, query: str, search_results: List[Dict[str, Any]]) -> List[str]:
        """Extract key insights from search results"""
        try:
            system_prompt = """
            You are an insight extraction expert. Extract the most important insights from search results
            that directly relate to the user's query.
            
            Return a JSON object with the following structure:
            {
                "insights": [
                    "insight1: detailed explanation",
                    "insight2: detailed explanation",
                    "insight3: detailed explanation"
                ],
                "confidence_scores": [0.9, 0.8, 0.7]
            }
            
            Each insight should:
            1. Be a complete, meaningful statement
            2. Directly address the query
            3. Be supported by the search results
            4. Provide valuable information
            5. Be unique and non-redundant
            """
            
            # Format search results
            results_text = self._format_search_results(search_results)
            
            prompt = f"""
            Original Query: {query}
            
            Search Results:
            {results_text}
            
            Extract the most important insights from these search results.
            """
            
            response = await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            return response.get("insights", [])
            
        except Exception as e:
            self.log_execution(f"Error extracting insights: {str(e)}", "ERROR")
            return []
    
    async def _generate_recommendations(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        iteration: int
    ) -> List[str]:
        """Generate recommendations for further research"""
        try:
            system_prompt = f"""
            You are a research recommendation expert. Based on the search results from iteration {iteration},
            generate recommendations for further research or investigation.
            
            Return a JSON object with the following structure:
            {{
                "recommendations": [
                    "recommendation1: specific action or query",
                    "recommendation2: specific action or query",
                    "recommendation3: specific action or query"
                ],
                "reasoning": [
                    "reason1 for recommendation1",
                    "reason2 for recommendation2",
                    "reason3 for recommendation3"
                ]
            }}
            
            Each recommendation should:
            1. Be specific and actionable
            2. Address gaps in current understanding
            3. Suggest new angles or approaches
            4. Be relevant to the original query
            5. Help achieve comprehensive research
            """
            
            # Format search results
            results_text = self._format_search_results(search_results)
            
            prompt = f"""
            Original Query: {query}
            Iteration: {iteration}
            
            Search Results:
            {results_text}
            
            Generate recommendations for further research based on these results.
            """
            
            response = await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            return response.get("recommendations", [])
            
        except Exception as e:
            self.log_execution(f"Error generating recommendations: {str(e)}", "ERROR")
            return []
    
    def _format_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results for LLM processing"""
        formatted_results = []
        
        for i, result in enumerate(search_results, 1):
            title = result.get("title", "No title")
            content = result.get("content", "No content")
            url = result.get("url", "No URL")
            score = result.get("score", 0.5)
            
            formatted_result = f"""
{i}. Title: {title}
   Content: {content[:500]}{'...' if len(content) > 500 else ''}
   URL: {url}
   Score: {score}
"""
            formatted_results.append(formatted_result)
        
        return "\n".join(formatted_results)
    
    async def compare_summaries(
        self,
        summaries: List[Dict[str, Any]],
        query: str
    ) -> Dict[str, Any]:
        """Compare multiple summaries and identify patterns"""
        try:
            if not summaries:
                return {"comparison": "No summaries to compare", "patterns": [], "gaps": []}
            
            system_prompt = """
            You are a summary comparison expert. Compare multiple summaries from different research iterations
            and identify patterns, contradictions, and gaps.
            
            Return a JSON object with the following structure:
            {
                "comparison": "overall comparison of summaries",
                "patterns": ["pattern1", "pattern2", "pattern3"],
                "contradictions": ["contradiction1", "contradiction2"],
                "gaps": ["gap1", "gap2", "gap3"],
                "synthesis": "synthesized understanding from all summaries"
            }
            """
            
            # Format summaries
            summaries_text = ""
            for i, summary_data in enumerate(summaries, 1):
                summary = summary_data.get("summary", "")
                iteration = summary_data.get("iteration", i)
                summaries_text += f"\nIteration {iteration} Summary:\n{summary}\n"
            
            prompt = f"""
            Original Query: {query}
            
            Summaries from different iterations:
            {summaries_text}
            
            Compare these summaries and identify patterns, contradictions, and gaps.
            """
            
            return await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            self.log_execution(f"Error comparing summaries: {str(e)}", "ERROR")
            return {"comparison": f"Error: {str(e)}", "patterns": [], "gaps": []}

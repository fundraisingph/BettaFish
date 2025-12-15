"""
QueryEngine Report Structure Node
"""
import logging
from typing import Dict, List, Any, Optional

from .base_node import BaseNode

logger = logging.getLogger(__name__)

class ReportStructureNode(BaseNode):
    """Report structure node for QueryEngine"""
    
    def validate_inputs(self, query: str, research_results: List[Dict[str, Any]]) -> bool:
        """Validate report structure inputs"""
        if not query or not isinstance(query, str):
            return False
        
        if not research_results or not isinstance(research_results, list):
            return False
        
        return True
    
    async def run(self, query: str, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run report structure node"""
        try:
            self.log_execution(f"Generating report structure for query: {query}")
            
            if not research_results:
                return {
                    "query": query,
                    "structure": {
                        "title": f"Research Report: {query}",
                        "sections": [],
                        "summary": "No research results available"
                    }
                }
            
            # Generate report structure
            structure = await self._generate_report_structure(query, research_results)
            
            return {
                "query": query,
                "structure": structure,
                "research_iterations": len(research_results)
            }
            
        except Exception as e:
            self.log_execution(f"Report structure generation failed: {str(e)}", "ERROR")
            raise
    
    async def run_with_template(
        self,
        query: str,
        research_results: List[Dict[str, Any]],
        template_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Run report structure with specific template"""
        try:
            # Generate basic structure
            basic_result = await self.run(query, research_results)
            
            # Apply template
            if template_type == "comprehensive":
                structure = await self._apply_comprehensive_template(query, research_results)
            elif template_type == "executive":
                structure = await self._apply_executive_template(query, research_results)
            elif template_type == "technical":
                structure = await self._apply_technical_template(query, research_results)
            elif template_type == "academic":
                structure = await self._apply_academic_template(query, research_results)
            else:
                structure = basic_result["structure"]
            
            return {
                "query": query,
                "structure": structure,
                "template_type": template_type,
                "research_iterations": len(research_results)
            }
            
        except Exception as e:
            self.log_execution(f"Report structure with template failed: {str(e)}", "ERROR")
            raise
    
    async def _generate_report_structure(self, query: str, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate basic report structure"""
        try:
            system_prompt = """
            You are a report structure expert. Generate a comprehensive report structure based on research results.
            
            Return a JSON object with the following structure:
            {
                "title": "Report title",
                "executive_summary": "Brief overview of key findings",
                "sections": [
                    {
                        "title": "Section title",
                        "description": "Section description",
                        "subsections": [
                            {
                                "title": "Subsection title",
                                "description": "Subsection description",
                                "content_type": "summary|analysis|insights|recommendations"
                            }
                        ]
                    }
                ],
                "conclusions": "Main conclusions and implications",
                "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
                "appendices": ["appendix1", "appendix2"]
            }
            
            The structure should:
            1. Be logical and well-organized
            2. Cover all aspects of the research
            3. Include executive summary for quick understanding
            4. Have clear section hierarchies
            5. Include conclusions and recommendations
            6. Be comprehensive but focused
            """
            
            # Format research results
            research_text = self._format_research_results(research_results)
            
            prompt = f"""
            Original Query: {query}
            
            Research Results:
            {research_text}
            
            Generate a comprehensive report structure based on these research results.
            """
            
            return await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            self.log_execution(f"Error generating report structure: {str(e)}", "ERROR")
            raise
    
    async def _apply_comprehensive_template(self, query: str, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply comprehensive report template"""
        try:
            system_prompt = """
            You are a comprehensive report expert. Generate a detailed report structure that covers
            all aspects of the research in depth.
            
            Return a JSON object with the following structure:
            {
                "title": "Comprehensive Research Report: [Query]",
                "executive_summary": "Detailed overview of all key findings",
                "introduction": "Background and research context",
                "methodology": "Research approach and sources",
                "sections": [
                    {
                        "title": "Main topic area",
                        "description": "Description of this area",
                        "subsections": [
                            {
                                "title": "Specific aspect",
                                "description": "Description of this aspect",
                                "content_type": "analysis"
                            }
                        ]
                    }
                ],
                "cross_analysis": "Analysis of relationships between findings",
                "trends": "Identified trends and patterns",
                "contradictions": "Conflicting information and analysis",
                "gaps": "Research gaps and limitations",
                "conclusions": "Comprehensive conclusions",
                "recommendations": ["detailed", "actionable", "recommendations"],
                "future_research": "Directions for future investigation",
                "references": "Key sources and references"
            }
            """
            
            # Format research results
            research_text = self._format_research_results(research_results)
            
            prompt = f"""
            Original Query: {query}
            
            Research Results:
            {research_text}
            
            Generate a comprehensive report structure that covers all aspects in detail.
            """
            
            return await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            self.log_execution(f"Error applying comprehensive template: {str(e)}", "ERROR")
            raise
    
    async def _apply_executive_template(self, query: str, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply executive report template"""
        try:
            system_prompt = """
            You are an executive report expert. Generate a concise, high-level report structure
            focused on business implications and key takeaways.
            
            Return a JSON object with the following structure:
            {
                "title": "Executive Summary: [Query]",
                "key_findings": "Most important findings in bullet points",
                "business_implications": "Impact on business/organization",
                "opportunities": ["opportunity1", "opportunity2", "opportunity3"],
                "risks": ["risk1", "risk2", "risk3"],
                "recommendations": ["actionable", "high-level", "recommendations"],
                "next_steps": ["immediate", "next", "steps"],
                "financial_impact": "Financial implications if applicable",
                "timeline": "Suggested implementation timeline"
            }
            """
            
            # Format research results
            research_text = self._format_research_results(research_results)
            
            prompt = f"""
            Original Query: {query}
            
            Research Results:
            {research_text}
            
            Generate an executive report structure focused on business implications and key takeaways.
            """
            
            return await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            self.log_execution(f"Error applying executive template: {str(e)}", "ERROR")
            raise
    
    async def _apply_technical_template(self, query: str, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply technical report template"""
        try:
            system_prompt = """
            You are a technical report expert. Generate a detailed technical report structure
            focused on technical details, specifications, and analysis.
            
            Return a JSON object with the following structure:
            {
                "title": "Technical Analysis: [Query]",
                "abstract": "Technical abstract",
                "technical_overview": "Technical background and context",
                "specifications": "Key technical specifications",
                "analysis": [
                    {
                        "aspect": "Technical aspect name",
                        "details": "Detailed technical analysis",
                        "data": "Supporting data and metrics"
                    }
                ],
                "comparisons": "Comparison with alternatives",
                "performance": "Performance analysis and metrics",
                "limitations": "Technical limitations and constraints",
                "implementation": "Implementation considerations",
                "conclusions": "Technical conclusions",
                "recommendations": ["technical", "recommendations"],
                "appendices": ["technical", "appendices"]
            }
            """
            
            # Format research results
            research_text = self._format_research_results(research_results)
            
            prompt = f"""
            Original Query: {query}
            
            Research Results:
            {research_text}
            
            Generate a technical report structure focused on technical details and analysis.
            """
            
            return await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            self.log_execution(f"Error applying technical template: {str(e)}", "ERROR")
            raise
    
    async def _apply_academic_template(self, query: str, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply academic report template"""
        try:
            system_prompt = """
            You are an academic report expert. Generate a scholarly report structure
            following academic conventions and standards.
            
            Return a JSON object with the following structure:
            {
                "title": "Academic Research: [Query]",
                "abstract": "Scholarly abstract",
                "introduction": "Research introduction and context",
                "literature_review": "Review of existing literature",
                "methodology": "Research methodology",
                "findings": [
                    {
                        "theme": "Research theme",
                        "evidence": "Supporting evidence",
                        "analysis": "Scholarly analysis"
                    }
                ],
                "discussion": "Discussion of findings",
                "implications": "Theoretical and practical implications",
                "limitations": "Research limitations",
                "conclusions": "Scholarly conclusions",
                "future_research": "Directions for future research",
                "references": "Academic references and citations"
            }
            """
            
            # Format research results
            research_text = self._format_research_results(research_results)
            
            prompt = f"""
            Original Query: {query}
            
            Research Results:
            {research_text}
            
            Generate an academic report structure following scholarly conventions.
            """
            
            return await self.llm_client.generate_json_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            self.log_execution(f"Error applying academic template: {str(e)}", "ERROR")
            raise
    
    def _format_research_results(self, research_results: List[Dict[str, Any]]) -> str:
        """Format research results for LLM processing"""
        formatted_results = []
        
        for i, iteration in enumerate(research_results, 1):
            summary = iteration.get("summary", "")
            insights = iteration.get("insights", [])
            iteration_num = iteration.get("iteration", i)
            
            formatted_result = f"""
Iteration {iteration_num}:
Summary: {summary[:1000]}{'...' if len(summary) > 1000 else ''}

Key Insights:
"""
            
            for j, insight in enumerate(insights[:5], 1):
                formatted_result += f"{j}. {insight}\n"
            
            formatted_results.append(formatted_result)
        
        return "\n".join(formatted_results)

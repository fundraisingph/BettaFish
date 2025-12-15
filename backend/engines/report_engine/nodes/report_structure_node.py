"""
ReportEngine Report Structure Node
"""
import logging
from typing import Dict, List, Any, Optional

from .base_node import BaseNode

logger = logging.getLogger(__name__)

class ReportStructureNode(BaseNode):
    """Report structure node for ReportEngine"""
    
    def validate_inputs(self, query: str, research_results: List[Dict[str, Any]], template_type: str = "comprehensive") -> bool:
        """Validate report structure inputs"""
        if not query or not isinstance(query, str):
            return False
        
        if not research_results or not isinstance(research_results, list):
            return False
        
        if template_type not in ["comprehensive", "executive", "technical", "academic"]:
            return False
        
        return True
    
    async def run(self, query: str, research_results: List[Dict[str, Any]], template_type: str = "comprehensive") -> Dict[str, Any]:
        """Run report structure node"""
        try:
            self.log_execution(f"Generating report structure for template: {template_type}")
            
            if not research_results:
                return {
                    "title": f"Report: {query}",
                    "template_type": template_type,
                    "sections": [],
                    "executive_summary": "No research results available",
                    "conclusions": "",
                    "recommendations": [],
                    "appendices": []
                }
            
            # Generate structure based on template type
            if template_type == "comprehensive":
                return await self._generate_comprehensive_structure(query, research_results)
            elif template_type == "executive":
                return await self._generate_executive_structure(query, research_results)
            elif template_type == "technical":
                return await self._generate_technical_structure(query, research_results)
            elif template_type == "academic":
                return await self._generate_academic_structure(query, research_results)
            else:
                return await self._generate_comprehensive_structure(query, research_results)
                
        except Exception as e:
            self.log_execution(f"Report structure generation failed: {str(e)}", "ERROR")
            raise
    
    async def run_with_template(
        self,
        query: str,
        research_results: List[Dict[str, Any]],
        template_type: str = "comprehensive",
        custom_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run report structure with custom template options"""
        try:
            # Get base structure
            structure = await self.run(query, research_results, template_type)
            
            # Apply custom options if provided
            if custom_options:
                structure = self._apply_custom_options(structure, custom_options)
            
            return structure
            
        except Exception as e:
            self.log_execution(f"Report structure with template failed: {str(e)}", "ERROR")
            raise
    
    async def _generate_comprehensive_structure(self, query: str, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive report structure"""
        try:
            system_prompt = """
            You are a comprehensive report structure expert. Generate a detailed report structure
            that covers all aspects of the research.
            
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
            Generate a comprehensive report structure for: {query}
            
            Research Results:
            {research_text}
            
            Create a detailed report structure that covers all aspects of the research.
            """
            
            return await self.llm_client.generate_structured_response(
                prompt=prompt,
                response_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "executive_summary": {"type": "string"},
                        "introduction": {"type": "string"},
                        "methodology": {"type": "string"},
                        "sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "subsections": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "title": {"type": "string"},
                                                "description": {"type": "string"},
                                                "content_type": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "cross_analysis": {"type": "string"},
                        "trends": {"type": "string"},
                        "contradictions": {"type": "string"},
                        "gaps": {"type": "string"},
                        "conclusions": {"type": "string"},
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "future_research": {"type": "string"},
                        "references": {"type": "string"}
                    }
                },
                system_prompt=system_prompt
            )
            
        except Exception as e:
            self.log_execution(f"Error generating comprehensive structure: {str(e)}", "ERROR")
            raise
    
    async def _generate_executive_structure(self, query: str, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate executive report structure"""
        try:
            system_prompt = """
            You are an executive report expert. Generate a high-level report structure
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
            
            The structure should:
            1. Focus on business implications
            2. Be concise and high-level
            3. Include actionable recommendations
            4. Highlight opportunities and risks
            5. Be suitable for executive audience
            """
            
            # Format research results
            research_text = self._format_research_results(research_results)
            
            prompt = f"""
            Generate an executive report structure for: {query}
            
            Research Results:
            {research_text}
            
            Create a high-level report structure focused on business implications and key takeaways.
            """
            
            return await self.llm_client.generate_structured_response(
                prompt=prompt,
                response_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "key_findings": {"type": "string"},
                        "business_implications": {"type": "string"},
                        "opportunities": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "risks": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "next_steps": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "financial_impact": {"type": "string"},
                        "timeline": {"type": "string"}
                    }
                },
                system_prompt=system_prompt
            )
            
        except Exception as e:
            self.log_execution(f"Error generating executive structure: {str(e)}", "ERROR")
            raise
    
    async def _generate_technical_structure(self, query: str, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate technical report structure"""
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
            
            The structure should:
            1. Focus on technical details and specifications
            2. Include performance metrics and analysis
            3. Compare with alternatives
            4. Address limitations and constraints
            5. Provide implementation guidance
            6. Be suitable for technical audience
            """
            
            # Format research results
            research_text = self._format_research_results(research_results)
            
            prompt = f"""
            Generate a technical report structure for: {query}
            
            Research Results:
            {research_text}
            
            Create a detailed technical report structure focused on technical details and analysis.
            """
            
            return await self.llm_client.generate_structured_response(
                prompt=prompt,
                response_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "abstract": {"type": "string"},
                        "technical_overview": {"type": "string"},
                        "specifications": {"type": "string"},
                        "analysis": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "aspect": {"type": "string"},
                                    "details": {"type": "string"},
                                    "data": {"type": "string"}
                                }
                            }
                        },
                        "comparisons": {"type": "string"},
                        "performance": {"type": "string"},
                        "limitations": {"type": "string"},
                        "implementation": {"type": "string"},
                        "conclusions": {"type": "string"},
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "appendices": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                system_prompt=system_prompt
            )
            
        except Exception as e:
            self.log_execution(f"Error generating technical structure: {str(e)}", "ERROR")
            raise
    
    async def _generate_academic_structure(self, query: str, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate academic report structure"""
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
            
            The structure should:
            1. Follow academic conventions
            2. Include literature review
            3. Provide proper methodology
            4. Include citations and references
            5. Be suitable for academic audience
            """
            
            # Format research results
            research_text = self._format_research_results(research_results)
            
            prompt = f"""
            Generate an academic report structure for: {query}
            
            Research Results:
            {research_text}
            
            Create a scholarly report structure following academic conventions.
            """
            
            return await self.llm_client.generate_structured_response(
                prompt=prompt,
                response_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "abstract": {"type": "string"},
                        "introduction": {"type": "string"},
                        "literature_review": {"type": "string"},
                        "methodology": {"type": "string"},
                        "findings": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "theme": {"type": "string"},
                                    "evidence": {"type": "string"},
                                    "analysis": {"type": "string"}
                                }
                            }
                        },
                        "discussion": {"type": "string"},
                        "implications": {"type": "string"},
                        "limitations": {"type": "string"},
                        "conclusions": {"type": "string"},
                        "future_research": {"type": "string"},
                        "references": {"type": "string"}
                    }
                },
                system_prompt=system_prompt
            )
            
        except Exception as e:
            self.log_execution(f"Error generating academic structure: {str(e)}", "ERROR")
            raise
    
    def _format_research_results(self, research_results: List[Dict[str, Any]]) -> str:
        """Format research results for LLM processing"""
        formatted_results = []
        
        for i, result in enumerate(research_results, 1):
            summary = result.get("summary", "")
            insights = result.get("insights", [])
            iteration = result.get("iteration", i)
            
            formatted_result = f"""
{i}. Iteration {iteration}:
Summary: {summary[:1000]}{'...' if len(summary) > 1000 else ''}

Key Insights:
"""
            
            for j, insight in enumerate(insights[:5], 1):
                formatted_result += f"{j}. {insight}\n"
            
            formatted_results.append(formatted_result)
        
        return "\n".join(formatted_results)
    
    def _apply_custom_options(self, structure: Dict[str, Any], custom_options: Dict[str, Any]) -> Dict[str, Any]:
        """Apply custom options to structure"""
        # Apply custom options to structure
        if custom_options.get("title"):
            structure["title"] = custom_options["title"]
        
        if custom_options.get("sections"):
            structure["sections"] = custom_options["sections"]
        
        if custom_options.get("executive_summary"):
            structure["executive_summary"] = custom_options["executive_summary"]
        
        return structure
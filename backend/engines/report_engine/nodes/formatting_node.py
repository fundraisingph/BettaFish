"""
ReportEngine Formatting Node
"""
import logging
from typing import Dict, List, Any, Optional

from .base_node import BaseNode

logger = logging.getLogger(__name__)

class FormattingNode(BaseNode):
    """Formatting node for ReportEngine"""
    
    def validate_inputs(self, report_structure: Dict[str, Any], research_results: List[Dict[str, Any]]) -> bool:
        """Validate formatting inputs"""
        if not report_structure or not isinstance(report_structure, dict):
            return False
        
        if not research_results or not isinstance(research_results, list):
            return False
        
        return True
    
    async def run(self, report_structure: Dict[str, Any], research_results: List[Dict[str, Any]]) -> str:
        """Run formatting node"""
        try:
            self.log_execution("Formatting report based on structure and research results")
            
            # Generate formatted report
            formatted_report = await self._generate_formatted_report(report_structure, research_results)
            
            return formatted_report
            
        except Exception as e:
            self.log_execution(f"Report formatting failed: {str(e)}", "ERROR")
            raise
    
    async def run_with_format(
        self,
        report_structure: Dict[str, Any],
        research_results: List[Dict[str, Any]],
        output_format: str = "markdown"
    ) -> Dict[str, Any]:
        """Run formatting with specific output format"""
        try:
            # Generate basic formatted report
            formatted_content = await self.run(report_structure, research_results)
            
            result = {
                "content": formatted_content,
                "format": output_format,
                "structure": report_structure,
                "research_iterations": len(research_results)
            }
            
            # Apply format-specific processing
            if output_format == "html":
                result["content"] = await self._convert_to_html(formatted_content)
                result["content_type"] = "text/html"
            elif output_format == "pdf":
                result["content"] = await self._convert_to_pdf(formatted_content)
                result["content_type"] = "application/pdf"
            elif output_format == "json":
                result["content"] = await self._convert_to_json(report_structure, research_results)
                result["content_type"] = "application/json"
            else:
                result["content_type"] = "text/markdown"
            
            return result
            
        except Exception as e:
            self.log_execution(f"Report formatting with format failed: {str(e)}", "ERROR")
            raise
    
    async def _generate_formatted_report(self, report_structure: Dict[str, Any], research_results: List[Dict[str, Any]]) -> str:
        """Generate formatted report in markdown"""
        try:
            system_prompt = """
            You are a report formatting expert. Convert the report structure and research results
            into a well-formatted markdown report.
            
            The formatted report should:
            1. Follow the provided structure exactly
            2. Include all relevant research findings
            3. Be well-organized with proper headings
            4. Use markdown formatting effectively
            5. Include tables, lists, and emphasis where appropriate
            6. Be comprehensive and readable
            7. Include proper citations and references
            """
            
            # Format inputs
            structure_text = self._format_structure(report_structure)
            research_text = self._format_research_results(research_results)
            
            prompt = f"""
            Report Structure:
            {structure_text}
            
            Research Results:
            {research_text}
            
            Generate a well-formatted markdown report based on this structure and research.
            """
            
            return await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4000
            )
            
        except Exception as e:
            self.log_execution(f"Error generating formatted report: {str(e)}", "ERROR")
            raise
    
    async def _convert_to_html(self, markdown_content: str) -> str:
        """Convert markdown to HTML"""
        try:
            system_prompt = """
            You are an HTML formatting expert. Convert the markdown content to clean, semantic HTML.
            
            The HTML should:
            1. Use semantic HTML5 tags (header, nav, main, section, article, etc.)
            2. Include proper CSS classes for styling
            3. Be responsive and accessible
            4. Include proper heading hierarchy
            5. Use tables, lists, and other HTML elements appropriately
            6. Include meta tags for SEO
            7. Be well-structured and valid
            """
            
            prompt = f"""
            Convert this markdown content to clean, semantic HTML:
            
            {markdown_content}
            
            Generate complete HTML document with proper structure and styling.
            """
            
            return await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=5000
            )
            
        except Exception as e:
            self.log_execution(f"Error converting to HTML: {str(e)}", "ERROR")
            raise
    
    async def _convert_to_pdf(self, markdown_content: str) -> str:
        """Convert markdown to PDF"""
        try:
            system_prompt = """
            You are a PDF formatting expert. Convert the markdown content to PDF format.
            
            The PDF should:
            1. Preserve all formatting and structure
            2. Include proper page breaks and pagination
            3. Be suitable for professional printing
            4. Include headers and footers
            5. Maintain table formatting
            6. Be properly formatted for A4 paper
            """
            
            prompt = f"""
            Convert this markdown content to PDF format:
            
            {markdown_content}
            
            Generate properly formatted PDF content.
            """
            
            # In a real implementation, this would use a PDF library
            # For now, return a placeholder
            return "PDF generation not implemented in this version"
            
        except Exception as e:
            self.log_execution(f"Error converting to PDF: {str(e)}", "ERROR")
            raise
    
    async def _convert_to_json(self, report_structure: Dict[str, Any], research_results: List[Dict[str, Any]]) -> str:
        """Convert to structured JSON format"""
        try:
            import json
            
            # Create structured JSON output
            json_report = {
                "report_structure": report_structure,
                "research_results": research_results,
                "metadata": {
                    "generated_at": "2024-01-01T00:00:00Z",  # Placeholder
                    "format_version": "1.0",
                    "source": "ReportEngine"
                }
            }
            
            return json.dumps(json_report, indent=2)
            
        except Exception as e:
            self.log_execution(f"Error converting to JSON: {str(e)}", "ERROR")
            raise
    
    async def enhance_report(
        self,
        formatted_report: str,
        enhancements: List[str] = None
    ) -> str:
        """Enhance formatted report with additional features"""
        try:
            if not enhancements:
                return formatted_report
            
            system_prompt = """
            You are a report enhancement expert. Enhance the report content with the requested features.
            
            The enhanced report should:
            1. Maintain the original content structure
            2. Add the requested enhancements seamlessly
            3. Improve readability and presentation
            4. Be well-formatted and professional
            5. Include proper navigation and cross-references
            """
            
            enhancements_text = "\n".join(f"- {enhancement}" for enhancement in enhancements)
            
            prompt = f"""
            Enhance this report with the following features:
            
            {enhancements_text}
            
            Report Content:
            {formatted_report}
            
            Create an enhanced version of the report with the requested features.
            """
            
            return await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=5000
            )
            
        except Exception as e:
            self.log_execution(f"Error enhancing report: {str(e)}", "ERROR")
            raise
    
    async def generate_table_of_contents(self, report_content: str) -> str:
        """Generate table of contents from report content"""
        try:
            system_prompt = """
            You are a table of contents expert. Generate a table of contents from the report content.
            
            Return a markdown table of contents with:
            1. Proper indentation for heading levels
            2. Links to sections (using markdown anchors)
            3. Page numbers (estimated)
            4. Clear hierarchy and organization
            """
            
            prompt = f"""
            Generate a table of contents for this report:
            
            {report_content[:2000]}...
            
            Create a well-structured table of contents with proper markdown formatting.
            """
            
            return await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=500
            )
            
        except Exception as e:
            self.log_execution(f"Error generating table of contents: {str(e)}", "ERROR")
            raise
    
    async def generate_citations(self, report_content: str) -> str:
        """Generate citations from report content"""
        try:
            system_prompt = """
            You are a citation expert. Generate proper citations for the report content.
            
            Return markdown citations with:
            1. Proper citation style
            2. Complete reference information
            3. Links to sources when available
            4. Consistent formatting
            """
            
            prompt = f"""
            Generate citations for this report:
            
            {report_content[:2000]}...
            
            Create properly formatted citations for all referenced sources.
            """
            
            return await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=1000
            )
            
        except Exception as e:
            self.log_execution(f"Error generating citations: {str(e)}", "ERROR")
            raise
    
    async def generate_glossary(self, report_content: str) -> str:
        """Generate glossary from report content"""
        try:
            system_prompt = """
            You are a glossary expert. Generate a glossary of key terms from the report content.
            
            Return a markdown glossary with:
            1. Key terms in alphabetical order
            2. Clear, concise definitions
            3. Context-specific explanations
            4. Cross-references when relevant
            """
            
            prompt = f"""
            Generate a glossary for this report:
            
            {report_content[:2000]}...
            
            Create a comprehensive glossary of key terms and concepts.
            """
            
            return await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=1000
            )
            
        except Exception as e:
            self.log_execution(f"Error generating glossary: {str(e)}", "ERROR")
            raise
    
    def _format_structure(self, structure: Dict[str, Any]) -> str:
        """Format report structure for LLM processing"""
        try:
            import json
            return json.dumps(structure, indent=2)
        except Exception as e:
            self.log_execution(f"Error formatting structure: {str(e)}", "WARNING")
            return str(structure)
    
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
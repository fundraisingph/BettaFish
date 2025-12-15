"""
ReportEngine LLM Client
"""
import json
import logging
from typing import Dict, List, Optional, Any, Union

from core.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """LLM client for ReportEngine"""
    
    def __init__(self, model: Optional[str] = None):
        self.model = model or settings.REPORT_ENGINE_LLM_MODEL
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
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_API_BASE
            )
            
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
            
            response = await client.chat.completions.create(**kwargs)
            
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
            return await self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
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
            
            response = await self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error generating structured response: {str(e)}")
            raise
    
    async def generate_report_structure(
        self,
        title: str,
        research_results: List[Dict[str, Any]],
        template_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate report structure"""
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
            research_text = ""
            for i, result in enumerate(research_results, 1):
                research_text += f"\n{i}. {result}\n"
            
            prompt = f"""
            Generate a report structure for: {title}
            
            Template Type: {template_type}
            
            Research Results:
            {research_text}
            
            Create a comprehensive report structure based on these research results.
            """
            
            return await self.generate_structured_response(
                prompt=prompt,
                response_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "executive_summary": {"type": "string"},
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
            logger.error(f"Error generating report structure: {str(e)}")
            raise
    
    async def generate_report_content(
        self,
        report_structure: Dict[str, Any],
        research_results: List[Dict[str, Any]]
    ) -> str:
        """Generate report content"""
        try:
            system_prompt = """
            You are a report content generation expert. Convert the report structure and research results
            into well-formatted markdown content.
            
            The content should:
            1. Follow the provided structure exactly
            2. Include all relevant research findings
            3. Be well-organized with proper headings
            4. Use markdown formatting effectively
            5. Include tables, lists, and emphasis where appropriate
            6. Be comprehensive and readable
            7. Include proper citations and references
            """
            
            # Format inputs
            structure_text = json.dumps(report_structure, indent=2)
            research_text = ""
            for i, result in enumerate(research_results, 1):
                research_text += f"\n{i}. {result}\n"
            
            prompt = f"""
            Report Structure:
            {structure_text}
            
            Research Results:
            {research_text}
            
            Generate well-formatted markdown content based on this structure and research.
            """
            
            return await self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4000
            )
            
        except Exception as e:
            logger.error(f"Error generating report content: {str(e)}")
            raise
    
    async def generate_html_content(
        self,
        markdown_content: str
    ) -> str:
        """Generate HTML content from markdown"""
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
            
            return await self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=5000
            )
            
        except Exception as e:
            logger.error(f"Error generating HTML content: {str(e)}")
            raise
    
    async def generate_charts(
        self,
        data: Dict[str, Any],
        chart_types: List[str] = None
    ) -> Dict[str, Any]:
        """Generate charts from data"""
        try:
            system_prompt = """
            You are a chart generation expert. Generate chart configurations from the provided data.
            
            Return a JSON object with the following structure:
            {
                "charts": [
                    {
                        "id": "chart_id",
                        "type": "pie|line|bar|scatter|area",
                        "title": "Chart title",
                        "description": "Chart description",
                        "data": {
                            "labels": ["label1", "label2", "label3"],
                            "datasets": [
                                {
                                    "label": "Dataset label",
                                    "data": [10, 20, 30],
                                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                                    "borderColor": "rgba(255, 99, 132, 1)"
                                }
                            ]
                        },
                        "options": {
                            "responsive": true,
                            "maintainAspectRatio": false,
                            "plugins": {
                                "legend": {
                                    "position": "top"
                                },
                                "tooltip": {
                                    "mode": "index",
                                    "intersect": false
                                }
                            }
                        }
                    }
                ]
            }
            
            The charts should:
            1. Be appropriate for the data type
            2. Have clear titles and descriptions
            3. Use appropriate colors and styling
            4. Include proper labels and legends
            5. Be responsive and accessible
            """
            
            # Format data
            data_text = json.dumps(data, indent=2)
            
            prompt = f"""
            Generate charts from this data:
            
            {data_text}
            
            Chart Types: {chart_types or 'all'}
            
            Create appropriate chart configurations for the data.
            """
            
            return await self.generate_structured_response(
                prompt=prompt,
                response_schema={
                    "type": "object",
                    "properties": {
                        "charts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "type": {"type": "string"},
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "data": {"type": "object"},
                                    "options": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                system_prompt=system_prompt
            )
            
        except Exception as e:
            logger.error(f"Error generating charts: {str(e)}")
            raise
    
    async def enhance_report(
        self,
        content: str,
        enhancements: List[str] = None
    ) -> str:
        """Enhance report with additional features"""
        try:
            if not enhancements:
                return content
            
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
            {content}
            
            Create an enhanced version of the report with the requested features.
            """
            
            return await self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=5000
            )
            
        except Exception as e:
            logger.error(f"Error enhancing report: {str(e)}")
            raise
    
    async def generate_summary(
        self,
        content: str
    ) -> str:
        """Generate a summary of the report"""
        try:
            system_prompt = """
            You are a report summarization expert. Generate a concise summary of the report content.
            
            The summary should:
            1. Be concise and focused
            2. Highlight key findings and insights
            3. Be suitable for executive overview
            4. Be well-structured and readable
            5. Include the most important points
            6. Be comprehensive but brief
            """
            
            prompt = f"""
            Generate a concise summary of this report:
            
            {content}
            
            Create a summary suitable for executive overview.
            """
            
            return await self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=500
            )
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
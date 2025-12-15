"""
Report formatting node implementation
Responsible for generating final formatted reports
"""

import json
from typing import Dict, Any
import logging
logger = logging.getLogger(__name__)

from .base_node import BaseNode
from ..prompts import SYSTEM_PROMPT_REPORT_FORMATTING, output_schema_report_formatting


class ReportFormattingNode(BaseNode):
    """Node for formatting final reports"""
    
    def __init__(self, llm_client):
        """
        Initialize report formatting node
        
        Args:
            llm_client: LLM client
        """
        super().__init__(llm_client, "ReportFormattingNode")
    
    async def run(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Call LLM to format final report
        
        Args:
            input_data: List of paragraph data with titles and latest_state
            **kwargs: Extra parameters
            
        Returns:
            Formatted report
        """
        try:
            # Prepare input data
            if not isinstance(input_data, list):
                raise ValueError("Input data must be a list of paragraph data")
            
            message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("Formatting final report")
            
            # Call LLM (streaming, safely concatenate UTF-8)
            response = await self.llm_client.stream_invoke_to_string(SYSTEM_PROMPT_REPORT_FORMATTING, message)
            
            # Process response
            processed_response = self.process_output(response)
            
            self.log_info("Final report formatting completed")
            return processed_response
            
        except Exception as e:
            self.log_error(f"Failed to format final report: {str(e)}")
            raise e
    
    def process_output(self, output: str) -> Dict[str, Any]:
        """
        Process LLM output, extract formatted report
        
        Args:
            output: LLM raw output
            
        Returns:
            Dictionary containing formatted_report
        """
        try:
            # Parse JSON
            import json
            result = json.loads(output)
            
            # Validate structure
            if not isinstance(result, dict):
                self.log_warning("Expected dict in response, got different type")
                return self._get_default_formatting()
            
            formatted_report = result.get("formatted_report", "")
            
            if not formatted_report:
                self.log_warning("No formatted_report found in response")
                return self._get_default_formatting()
            
            return {
                "formatted_report": formatted_report
            }
            
        except json.JSONDecodeError as e:
            self.log_error(f"JSON parsing failed: {str(e)}")
            return self._get_default_formatting()
        except Exception as e:
            self.log_error(f"Output processing failed: {str(e)}")
            return self._get_default_formatting()
    
    def _get_default_formatting(self) -> Dict[str, Any]:
        """
        Get default formatting when LLM fails
        
        Returns:
            Default formatting dictionary
        """
        return {
            "formatted_report": "# Report Formatting Failed\n\nUnable to generate formatted report due to processing errors. Please check the logs and try again."
        }
    
    def format_report_manually(self, paragraph_data: list, report_title: str) -> str:
        """
        Manually format report when LLM fails
        
        Args:
            paragraph_data: List of paragraph data
            report_title: Report title
            
        Returns:
            Manually formatted report
        """
        try:
            report_sections = []
            
            for i, paragraph in enumerate(paragraph_data, 1):
                if isinstance(paragraph, dict):
                    title = paragraph.get("title", f"Section {i}")
                    content = paragraph.get("paragraph_latest_state", "No content available")
                else:
                    title = f"Section {i}"
                    content = str(paragraph)
                
                section = f"""
## {title}

{content}

---
"""
                report_sections.append(section)
            
            # Add header
            header = f"""
# 【Public Opinion Insight】{report_title} Deep Public Opinion Analysis Report

## Executive Summary
### Core Public Opinion Findings
- Main emotional tendencies and distributions
- Key controversy focus points
- Important public opinion data indicators

### Public Opinion Hotspot Overview
- Most concerned discussion points
- Different platforms' focus points
- Emotional evolution trends

"""
            
            # Add footer
            footer = """

## Deep Insights and Suggestions
### Social Psychological Analysis
[Deep social psychology behind public opinion]

### Public Opinion Management Suggestions
[Targeted public opinion response suggestions]

## Data Appendix
### Key Public Opinion Indicators Summary
### Important User Comments Collection
### Detailed Sentiment Analysis Data

---
*Report generated by BettaFish Insight Engine*
*Generated on: {self._get_current_time()}*
"""
            
            return header + "\n".join(report_sections) + footer
            
        except Exception as e:
            logger.error(f"Manual formatting failed: {str(e)}")
            return f"# Report Formatting Error\n\nFailed to format report: {str(e)}"
    
    def _get_current_time(self) -> str:
        """Get current time string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
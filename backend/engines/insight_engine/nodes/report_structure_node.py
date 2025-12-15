"""
Report structure node implementation
Responsible for generating report structure from query
"""

import json
from typing import Dict, Any
import logging
logger = logging.getLogger(__name__)

from .base_node import BaseNode
from ..prompts import SYSTEM_PROMPT_REPORT_STRUCTURE, output_schema_report_structure


class ReportStructureNode(BaseNode):
    """Node for generating report structure"""
    
    def __init__(self, llm_client, query: str):
        """
        Initialize report structure node
        
        Args:
            llm_client: LLM client
            query: Research query
        """
        super().__init__(llm_client, "ReportStructureNode")
        self.query = query
    
    async def run(self, input_data: Any = None, **kwargs) -> Dict[str, Any]:
        """
        Call LLM to generate report structure
        
        Args:
            input_data: Input data (ignored, uses self.query)
            **kwargs: Extra parameters
            
        Returns:
            Report structure as list of paragraphs
        """
        try:
            self.log_info(f"Generating report structure for query: {self.query}")
            
            # Prepare input for LLM
            message = self.query
            
            # Call LLM (streaming, safely concatenate UTF-8)
            response = await self.llm_client.stream_invoke_to_string(SYSTEM_PROMPT_REPORT_STRUCTURE, message)
            
            # Process response
            processed_response = self.process_output(response)
            
            self.log_info(f"Report structure generated with {len(processed_response)} paragraphs")
            return processed_response
            
        except Exception as e:
            self.log_error(f"Failed to generate report structure: {str(e)}")
            raise e
    
    def process_output(self, output: str) -> Dict[str, Any]:
        """
        Process LLM output, extract report structure
        
        Args:
            output: LLM raw output
            
        Returns:
            Report structure as list of paragraphs
        """
        try:
            # Parse JSON
            import json
            result = json.loads(output)
            
            # Validate structure
            if not isinstance(result, list):
                self.log_warning("Expected list in response, got different type")
                return []
            
            # Validate each paragraph has required fields
            valid_paragraphs = []
            for item in result:
                if isinstance(item, dict) and "title" in item and "content" in item:
                    valid_paragraphs.append({
                        "title": item["title"],
                        "content": item["content"]
                    })
                else:
                    self.log_warning(f"Invalid paragraph structure: {item}")
            
            return valid_paragraphs
            
        except json.JSONDecodeError as e:
            self.log_error(f"JSON parsing failed: {str(e)}")
            # Return empty structure as fallback
            return []
        except Exception as e:
            self.log_error(f"Output processing failed: {str(e)}")
            return []
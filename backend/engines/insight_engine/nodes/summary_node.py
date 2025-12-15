"""
Summary node implementation
Responsible for generating summaries from search results
"""

import json
from typing import Dict, Any
from json.decoder import JSONDecodeError
import logging
logger = logging.getLogger(__name__)

from .base_node import BaseNode, StateMutationNode
from ..prompts import SYSTEM_PROMPT_FIRST_SUMMARY, SYSTEM_PROMPT_REFLECTION_SUMMARY
from ..utils.text_processing import (
    remove_reasoning_from_output,
    clean_json_tags,
    extract_clean_response,
    fix_incomplete_json
)


class FirstSummaryNode(StateMutationNode):
    """Node for generating first summary from search results"""
    
    def __init__(self, llm_client):
        """
        Initialize first summary node
        
        Args:
            llm_client: LLM client
        """
        super().__init__(llm_client, "FirstSummaryNode")
    
    async def run(self, input_data: Any, **kwargs) -> Any:
        """
        Execute first summary generation
        
        Args:
            input_data: Input data containing title, content, search_query, search_results
            **kwargs: Extra parameters
            
        Returns:
            Processing result
        """
        try:
            # Prepare input data
            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("Generating first summary")
            
            # Call LLM (streaming, safely concatenate UTF-8）
            response = await self.llm_client.stream_invoke_to_string(SYSTEM_PROMPT_FIRST_SUMMARY, message)
            
            # Process response
            processed_response = self.process_output(response)
            
            self.log_info("First summary generated successfully")
            return processed_response
            
        except Exception as e:
            self.log_error(f"Failed to generate first summary: {str(e)}")
            raise e
    
    async def mutate_state(self, input_data: Any, state: Any, paragraph_index: int = None, **kwargs) -> Any:
        """
        Modify state with first summary
        
        Args:
            input_data: Input data containing title, content, search_query, search_results
            state: Current research state
            paragraph_index: Index of paragraph to modify
            **kwargs: Extra parameters
            
        Returns:
            Updated state
        """
        try:
            # Prepare input data
            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("Generating first summary")
            
            # Call LLM (streaming, safely concatenate UTF-8）
            response = await self.llm_client.stream_invoke_to_string(SYSTEM_PROMPT_FIRST_SUMMARY, message)
            
            # Process response
            processed_response = self.process_output(response)
            
            # Update state
            paragraph = state.get_paragraph(paragraph_index)
            if paragraph:
                paragraph.research.latest_summary = processed_response.get("paragraph_latest_state", "")
                state.update_timestamp()
            
            self.log_info("First summary generated successfully")
            return state
            
        except Exception as e:
            self.log_error(f"Failed to generate first summary: {str(e)}")
            raise e
    
    def process_output(self, output: str) -> Dict[str, str]:
        """
        Process LLM output, extract paragraph_latest_state
        
        Args:
            output: LLM raw output
            
        Returns:
            Dictionary containing paragraph_latest_state
        """
        try:
            # Clean response text
            cleaned_output = remove_reasoning_from_output(output)
            cleaned_output = clean_json_tags(cleaned_output)
            
            # Log cleaned output for debugging
            self.log_info(f"Cleaned output: {cleaned_output}")
            
            # Parse JSON
            try:
                result = json.loads(cleaned_output)
                self.log_info("JSON parsing successful")
            except JSONDecodeError as e:
                self.log_error(f"JSON parsing failed: {str(e)}")
                # Use more powerful extraction method
                result = extract_clean_response(cleaned_output)
                if "error" in result:
                    self.log_error("JSON parsing failed, attempting to fix...")
                    # Try to fix JSON
                    fixed_json = fix_incomplete_json(cleaned_output)
                    if fixed_json:
                        try:
                            result = json.loads(fixed_json)
                            self.log_info("JSON fixing successful")
                        except JSONDecodeError:
                            self.log_error("JSON fixing failed")
                            # Return default summary
                            return self._get_default_summary()
                    else:
                        self.log_error("Unable to fix JSON, using default summary")
                        return self._get_default_summary()
            
            # Validate and clean results
            paragraph_latest_state = result.get("paragraph_latest_state", "")
            
            return {
                "paragraph_latest_state": paragraph_latest_state
            }
            
        except Exception as e:
            self.log_error(f"Output processing failed: {str(e)}")
            # Return default summary
            return self._get_default_summary()
    
    def _get_default_summary(self) -> Dict[str, str]:
        """
        Get default summary
        
        Returns:
            Default summary dictionary
        """
        return {
            "paragraph_latest_state": "Initial analysis based on available data"
        }


class ReflectionSummaryNode(StateMutationNode):
    """Node for generating reflection summary"""
    
    def __init__(self, llm_client):
        """
        Initialize reflection summary node
        
        Args:
            llm_client: LLM client
        """
        super().__init__(llm_client, "ReflectionSummaryNode")
    
    async def run(self, input_data: Any, **kwargs) -> Any:
        """
        Execute reflection summary generation
        
        Args:
            input_data: Input data containing title, content, search_query, search_results, paragraph_latest_state
            **kwargs: Extra parameters
            
        Returns:
            Processing result
        """
        try:
            # Prepare input data
            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("Generating reflection summary")
            
            # Call LLM (streaming, safely concatenate UTF-8）
            response = await self.llm_client.stream_invoke_to_string(SYSTEM_PROMPT_REFLECTION_SUMMARY, message)
            
            # Process response
            processed_response = self.process_output(response)
            
            self.log_info("Reflection summary generated successfully")
            return processed_response
            
        except Exception as e:
            self.log_error(f"Failed to generate reflection summary: {str(e)}")
            raise e
    
    async def mutate_state(self, input_data: Any, state: Any, paragraph_index: int = None, **kwargs) -> Any:
        """
        Modify state with reflection summary
        
        Args:
            input_data: Input data containing title, content, search_query, search_results, paragraph_latest_state
            state: Current research state
            paragraph_index: Index of paragraph to modify
            **kwargs: Extra parameters
            
        Returns:
            Updated state
        """
        try:
            # Prepare input data
            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("Generating reflection summary")
            
            # Call LLM (streaming, safely concatenate UTF-8）
            response = await self.llm_client.stream_invoke_to_string(SYSTEM_PROMPT_REFLECTION_SUMMARY, message)
            
            # Process response
            processed_response = self.process_output(response)
            
            # Update state
            paragraph = state.get_paragraph(paragraph_index)
            if paragraph:
                paragraph.research.latest_summary = processed_response.get("updated_paragraph_latest_state", "")
                state.update_timestamp()
            
            self.log_info("Reflection summary generated successfully")
            return state
            
        except Exception as e:
            self.log_error(f"Failed to generate reflection summary: {str(e)}")
            raise e
    
    def process_output(self, output: str) -> Dict[str, str]:
        """
        Process LLM output, extract updated_paragraph_latest_state
        
        Args:
            output: LLM raw output
            
        Returns:
            Dictionary containing updated_paragraph_latest_state
        """
        try:
            # Clean response text
            cleaned_output = remove_reasoning_from_output(output)
            cleaned_output = clean_json_tags(cleaned_output)
            
            # Log cleaned output for debugging
            self.log_info(f"Cleaned output: {cleaned_output}")
            
            # Parse JSON
            try:
                result = json.loads(cleaned_output)
                self.log_info("JSON parsing successful")
            except JSONDecodeError as e:
                self.log_error(f"JSON parsing failed: {str(e)}")
                # Use more powerful extraction method
                result = extract_clean_response(cleaned_output)
                if "error" in result:
                    self.log_error("JSON parsing failed, attempting to fix...")
                    # Try to fix JSON
                    fixed_json = fix_incomplete_json(cleaned_output)
                    if fixed_json:
                        try:
                            result = json.loads(fixed_json)
                            self.log_info("JSON fixing successful")
                        except JSONDecodeError:
                            self.log_error("JSON fixing failed")
                            # Return default summary
                            return self._get_default_reflection_summary()
                    else:
                        self.log_error("Unable to fix JSON, using default summary")
                        return self._get_default_reflection_summary()
            
            # Validate and clean results
            updated_paragraph_latest_state = result.get("updated_paragraph_latest_state", "")
            
            return {
                "updated_paragraph_latest_state": updated_paragraph_latest_state
            }
            
        except Exception as e:
            self.log_error(f"Output processing failed: {str(e)}")
            # Return default summary
            return self._get_default_reflection_summary()
    
    def _get_default_reflection_summary(self) -> Dict[str, str]:
        """
        Get default reflection summary
        
        Returns:
            Default reflection summary dictionary
        """
        return {
            "updated_paragraph_latest_state": "Enhanced analysis with additional insights"
        }
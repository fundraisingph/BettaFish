"""
Search node implementation
Responsible for generating search queries and reflection queries
"""

import json
from typing import Dict, Any
from json.decoder import JSONDecodeError
import logging
logger = logging.getLogger(__name__)

from .base_node import BaseNode
from ..prompts import SYSTEM_PROMPT_FIRST_SEARCH, SYSTEM_PROMPT_REFLECTION
from ..utils.text_processing import (
    remove_reasoning_from_output,
    clean_json_tags,
    extract_clean_response,
    fix_incomplete_json
)


class FirstSearchNode(BaseNode):
    """Node for generating first search queries for paragraphs"""
    
    def __init__(self, llm_client):
        """
        Initialize first search node
        
        Args:
            llm_client: LLM client
        """
        super().__init__(llm_client, "FirstSearchNode")
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data"""
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
                return "title" in data and "content" in data
            except JSONDecodeError:
                return False
        elif isinstance(input_data, dict):
            return "title" in input_data and "content" in input_data
        return False
    
    async def run(self, input_data: Any, **kwargs) -> Dict[str, str]:
        """
        Call LLM to generate search queries
        
        Args:
            input_data: Input data containing title and content
            **kwargs: Extra parameters
            
        Returns:
            Dictionary containing search_query and reasoning
        """
        try:
            if not self.validate_input(input_data):
                raise ValueError("Input data format error, need to contain title and content fields")
            
            # Prepare input data
            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("Generating first search query")
            
            # Call LLM (streaming, safely concatenate UTF-8）
            response = await self.llm_client.stream_invoke_to_string(SYSTEM_PROMPT_FIRST_SEARCH, message)
            
            # Process response
            processed_response = self.process_output(response)
            
            self.log_info(f"Generated search query: {processed_response.get('search_query', 'N/A')}")
            return processed_response
            
        except Exception as e:
            self.log_error(f"Failed to generate first search query: {str(e)}")
            raise e
    
    def process_output(self, output: str) -> Dict[str, str]:
        """
        Process LLM output, extract search query and reasoning
        
        Args:
            output: LLM raw output
            
        Returns:
            Dictionary containing search_query and reasoning
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
                            # Return default query
                            return self._get_default_search_query()
                    else:
                        self.log_error("Unable to fix JSON, using default query")
                        return self._get_default_search_query()
            
            # Validate and clean results
            search_query = result.get("search_query", "")
            reasoning = result.get("reasoning", "")
            
            if not search_query:
                self.log_warning("No search query found, using default query")
                return self._get_default_search_query()
            
            return {
                "search_query": search_query,
                "reasoning": reasoning
            }
            
        except Exception as e:
            self.log_error(f"Output processing failed: {str(e)}")
            # Return default query
            return self._get_default_search_query()
    
    def _get_default_search_query(self) -> Dict[str, str]:
        """
        Get default search query
        
        Returns:
            Default search query dictionary
        """
        return {
            "search_query": "Related topic research",
            "reasoning": "Using default search query due to parsing failure"
        }


class ReflectionNode(BaseNode):
    """Node for reflecting on paragraphs and generating new search queries"""
    
    def __init__(self, llm_client):
        """
        Initialize reflection node
        
        Args:
            llm_client: LLM client
        """
        super().__init__(llm_client, "ReflectionNode")
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data"""
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
                required_fields = ["title", "content", "paragraph_latest_state"]
                return all(field in data for field in required_fields)
            except JSONDecodeError:
                return False
        elif isinstance(input_data, dict):
            required_fields = ["title", "content", "paragraph_latest_state"]
            return all(field in input_data for field in required_fields)
        return False
    
    async def run(self, input_data: Any, **kwargs) -> Dict[str, str]:
        """
        Call LLM to reflect and generate search queries
        
        Args:
            input_data: Input data containing title, content and paragraph_latest_state
            **kwargs: Extra parameters
            
        Returns:
            Dictionary containing search_query and reasoning
        """
        try:
            if not self.validate_input(input_data):
                raise ValueError("Input data format error, need to contain title, content and paragraph_latest_state fields")
            
            # Prepare input data
            if isinstance(input_data, str):
                message = input_data
            else:
                message = json.dumps(input_data, ensure_ascii=False)
            
            self.log_info("Reflecting and generating new search query")
            
            # Call LLM (streaming, safely concatenate UTF-8）
            response = await self.llm_client.stream_invoke_to_string(SYSTEM_PROMPT_REFLECTION, message)
            
            # Process response
            processed_response = self.process_output(response)
            
            self.log_info(f"Reflection generated search query: {processed_response.get('search_query', 'N/A')}")
            return processed_response
            
        except Exception as e:
            self.log_error(f"Failed to generate reflection search query: {str(e)}")
            raise e
    
    def process_output(self, output: str) -> Dict[str, str]:
        """
        Process LLM output, extract search query and reasoning
        
        Args:
            output: LLM raw output
            
        Returns:
            Dictionary containing search_query and reasoning
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
                            # Return default query
                            return self._get_default_reflection_query()
                    else:
                        self.log_error("Unable to fix JSON, using default query")
                        return self._get_default_reflection_query()
            
            # Validate and clean results
            search_query = result.get("search_query", "")
            reasoning = result.get("reasoning", "")
            
            if not search_query:
                self.log_warning("No search query found, using default query")
                return self._get_default_reflection_query()
            
            return {
                "search_query": search_query,
                "reasoning": reasoning
            }
            
        except Exception as e:
            self.log_error(f"Output processing failed: {str(e)}")
            # Return default query
            return self._get_default_reflection_query()
    
    def _get_default_reflection_query(self) -> Dict[str, str]:
        """
        Get default reflection search query
        
        Returns:
            Default reflection search query dictionary
        """
        return {
            "search_query": "Deep research supplementary information",
            "reasoning": "Using default reflection search query due to parsing failure"
        }
"""
QueryEngine Base Node
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ..llms.base import LLMClient

logger = logging.getLogger(__name__)

class BaseNode(ABC):
    """Base node for QueryEngine"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.node_type = self.__class__.__name__
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        """Run node logic"""
        # Validate inputs
        if not self.validate_inputs(*args, **kwargs):
            return self._create_error_result("Input validation failed")
        
        try:
            # Execute node logic
            result = await self._execute_node_logic(*args, **kwargs)
            
            # Validate outputs
            if not self.validate_outputs(result):
                return self._create_error_result("Output validation failed")
            
            return self._create_success_result(result)
            
        except Exception as e:
            logger.error(f"Node execution failed: {str(e)}")
            return self._create_error_result(str(e))
    
    def validate_inputs(self, *args, **kwargs) -> bool:
        """Validate node inputs"""
        return True
    
    def validate_outputs(self, result: Dict[str, Any]) -> bool:
        """Validate node outputs"""
        return True
    
    def _execute_node_logic(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the actual node logic - to be implemented by subclasses"""
        return {}
    
    def _create_success_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create success result"""
        return {
            "success": True,
            "result": result,
            "error": None
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result"""
        return {
            "success": False,
            "result": None,
            "error": error_message
        }
    
    def log_execution(self, message: str, level: str = "INFO"):
        """Log node execution"""
        log_message = f"[{self.node_type}] {message}"
        
        if level.upper() == "DEBUG":
            logger.debug(log_message)
        elif level.upper() == "INFO":
            logger.info(log_message)
        elif level.upper() == "WARNING":
            logger.warning(log_message)
        elif level.upper() == "ERROR":
            logger.error(log_message)
        elif level.upper() == "CRITICAL":
            logger.critical(log_message)
    
    async def safe_run(self, *args, **kwargs) -> Dict[str, Any]:
        """Safely run the node with error handling"""
        try:
            self.log_execution(f"Starting execution with args: {args}, kwargs: {kwargs}")
            
            # Validate inputs
            if not self.validate_inputs(*args, **kwargs):
                raise ValueError("Invalid inputs for node execution")
            
            # Run the node
            result = await self.run(*args, **kwargs)
            
            self.log_execution("Execution completed successfully")
            return result
            
        except Exception as e:
            self.log_execution(f"Execution failed: {str(e)}", "ERROR")
            raise
    
    def get_node_info(self) -> Dict[str, Any]:
        """Get node information"""
        return {
            "node_type": self.node_type,
            "description": self.__doc__ or "No description available",
            "has_llm_client": self.llm_client is not None
        }
    
    def set_llm_client(self, llm_client: LLMClient):
        """Set LLM client"""
        self.llm_client = llm_client
    
    def get_llm_client(self) -> LLMClient:
        """Get LLM client"""
        return self.llm_client

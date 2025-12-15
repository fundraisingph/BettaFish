"""
Base node class
Defines all processing node base interfaces
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
logger = logging.getLogger(__name__)

from ..llms.base import LLMClient
from ..state.state import ResearchState


class BaseNode(ABC):
    """Node base class"""
    
    def __init__(self, llm_client: LLMClient, node_name: str = ""):
        """
        Initialize node
        
        Args:
            llm_client: LLM client
            node_name: Node name
        """
        self.llm_client = llm_client
        self.node_name = node_name or self.__class__.__name__
    
    @abstractmethod
    async def run(self, input_data: Any, **kwargs) -> Any:
        """
        Execute node processing logic
        
        Args:
            input_data: Input data
            **kwargs: Extra parameters
            
        Returns:
            Processing result
        """
        # Validate inputs
        if not self._validate_inputs(inputs):
            return self._create_error_result("Input validation failed")
        
        try:
            # Execute node logic
            result = await self._execute_node_logic(inputs)
            
            # Validate outputs
            if not self._validate_outputs(result):
                return self._create_error_result("Output validation failed")
            
            return self._create_success_result(result)
            
        except Exception as e:
            logger.error(f"Node execution failed: {str(e)}")
            return self._create_error_result(str(e))
    
    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data
        
        Args:
            input_data: Input data
            
        Returns:
            Validation whether passed
        """
        return True
    
    def process_output(self, output: Any) -> Any:
        """
        Process output data
        
        Args:
            output: Raw output
            
        Returns:
            Processed output
        """
        return output
    
    def log_info(self, message: str):
        """Log info message"""
        logger.info(f"[{self.node_name}] {message}")
    
    def log_warning(self, message: str):
        """Log warning message"""
        logger.warning(f"[{self.node_name}] Warning: {message}")
    
    def log_error(self, message: str):
        """Log error message"""
        logger.error(f"[{self.node_name}] Error: {message}")


class StateMutationNode(BaseNode):
    """Node base class with state mutation functionality"""
    
    @abstractmethod
    async def mutate_state(self, input_data: Any, state: ResearchState, **kwargs) -> ResearchState:
        """
        Modify state
        
        Args:
            input_data: Input data
            state: Current state
            **kwargs: Extra parameters
            
        Returns:
            Modified state
        """
        pass
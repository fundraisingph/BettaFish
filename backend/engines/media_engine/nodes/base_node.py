"""
Base node class
Defines the base interface for all processing nodes
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..llms.base import LLMClient
from ..state.state import State
from loguru import logger


class BaseNode(ABC):
    """Base node class"""

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
    def run(self, input_data: Any, **kwargs) -> Any:
        """
        Execute node processing logic

        Args:
            input_data: Input data
            **kwargs: Additional parameters

        Returns:
            Processing result
        """
        # Validate inputs
        if not self.validate_input(input_data):
            return {"error": "Input validation failed"}
        
        try:
            # Execute node logic (implementation in subclasses)
            result = self._execute_node_logic(input_data, **kwargs)
            
            # Process outputs
            return self.process_output(result)
            
        except Exception as e:
            logger.error(f"Node execution failed: {str(e)}")
            return {"error": str(e)}
    
    def _execute_node_logic(self, input_data: Any, **kwargs) -> Any:
        """
        Execute the specific node logic (to be implemented by subclasses)
        
        Args:
            input_data: Input data
            **kwargs: Additional parameters
            
        Returns:
            Processing result
        """
        # Default implementation - subclasses should override this
        return input_data

    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data

        Args:
            input_data: Input data

        Returns:
            Whether validation passes
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
        """Record info log"""
        logger.info(f"[{self.node_name}] {message}")
    
    def log_warning(self, message: str):
        """Record warning log"""
        logger.warning(f"[{self.node_name}] Warning: {message}")

    def log_error(self, message: str):
        """Record error log"""
        logger.error(f"[{self.node_name}] Error: {message}")


class StateMutationNode(BaseNode):
    """Base node class with state modification functionality"""
    
    @abstractmethod
    def mutate_state(self, input_data: Any, state: State, **kwargs) -> State:
        """
        Modify state
        
        Args:
            input_data: Input data
            state: Current state
            **kwargs: Additional parameters
            
        Returns:
            Modified state
        """
        pass

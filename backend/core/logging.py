"""
Structured logging for BettaFish backend.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

from .config import settings


class StructuredLogger:
    """Structured logger for consistent error logging"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Configure handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log structured event"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data,
            "service": "bettafish-api"
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log structured error information"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "ERROR",
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "context": context or {},
            "service": "bettafish-api"
        }
        
        if settings.DEBUG:
            log_data["stack_trace"] = traceback.format_exc()
        
        self.logger.error(json.dumps(log_data))
    
    def log_warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log structured warning information"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "WARNING",
            "message": message,
            "context": context or {},
            "service": "bettafish-api"
        }
        
        self.logger.warning(json.dumps(log_data))
    
    def log_info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log structured information"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "message": message,
            "context": context or {},
            "service": "bettafish-api"
        }
        
        self.logger.info(json.dumps(log_data))


# Global logger instances
error_logger = StructuredLogger("bettafish.errors")
auth_logger = StructuredLogger("bettafish.auth")
api_logger = StructuredLogger("bettafish.api")
websocket_logger = StructuredLogger("bettafish.websocket")
agent_logger = StructuredLogger("bettafish.agents")
database_logger = StructuredLogger("bettafish.database")


# Configure standard logging
import traceback

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(settings.LOG_FILE)
        ]
    )


# Export logger instances
__all__ = [
    "StructuredLogger",
    "error_logger",
    "auth_logger", 
    "api_logger",
    "websocket_logger",
    "agent_logger",
    "database_logger",
    "setup_logging"
]
"""
Custom exceptions for BettaFish backend.
"""

from typing import Any, Dict, List, Optional
from fastapi import status


class BettaFishException(Exception):
    """Base exception for BettaFish application"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[List[Dict]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class ValidationException(BettaFishException):
    """Validation error exception"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[List[Dict]] = None,
        error_code: Optional[str] = "VALIDATION_ERROR"
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class AuthenticationException(BettaFishException):
    """Authentication error exception"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: Optional[str] = "AUTHENTICATION_ERROR"
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(BettaFishException):
    """Authorization error exception"""
    
    def __init__(
        self,
        message: str = "Access denied",
        error_code: Optional[str] = "AUTHORIZATION_ERROR"
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_403_FORBIDDEN
        )


class ResourceNotFoundException(BettaFishException):
    """Resource not found exception"""
    
    def __init__(
        self,
        resource: str = "Resource",
        error_code: Optional[str] = "RESOURCE_NOT_FOUND"
    ):
        super().__init__(
            message=f"{resource} not found",
            error_code=error_code,
            status_code=status.HTTP_404_NOT_FOUND
        )


class BusinessLogicException(BettaFishException):
    """Business logic error exception"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = "BUSINESS_LOGIC_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code
        )


class ExternalServiceException(BettaFishException):
    """External service error exception"""
    
    def __init__(
        self,
        service: str,
        message: str = "External service error",
        error_code: Optional[str] = "EXTERNAL_SERVICE_ERROR"
    ):
        super().__init__(
            message=f"{service}: {message}",
            error_code=error_code,
            status_code=status.HTTP_502_BAD_GATEWAY
        )


class RateLimitException(BettaFishException):
    """Rate limit exception"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        error_code: Optional[str] = "RATE_LIMIT_EXCEEDED"
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class WebSocketException(BettaFishException):
    """WebSocket error exception"""
    
    def __init__(
        self,
        message: str = "WebSocket error",
        error_code: Optional[str] = "WEBSOCKET_ERROR"
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class AgentException(BettaFishException):
    """Agent error exception"""
    
    def __init__(
        self,
        agent_type: str,
        message: str,
        error_code: Optional[str] = "AGENT_ERROR"
    ):
        super().__init__(
            message=f"Agent {agent_type}: {message}",
            error_code=error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class DatabaseException(BettaFishException):
    """Database error exception"""
    
    def __init__(
        self,
        message: str = "Database error",
        error_code: Optional[str] = "DATABASE_ERROR"
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ConfigurationException(BettaFishException):
    """Configuration error exception"""
    
    def __init__(
        self,
        message: str = "Configuration error",
        error_code: Optional[str] = "CONFIGURATION_ERROR"
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
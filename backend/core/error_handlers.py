"""
Error handling middleware and handlers for FastAPI.
"""

import traceback
from datetime import datetime
from typing import Dict, Any

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .exceptions import BettaFishException
from .logging import error_logger


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next):
        """Handle exceptions and return structured error responses"""
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await self._handle_exception(request, exc)
    
    async def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle exception and return appropriate error response"""
        request_id = getattr(request.state, "request_id", None)
        
        # Handle BettaFish exceptions
        if isinstance(exc, BettaFishException):
            error_response = {
                "success": False,
                "error": exc.__class__.__name__,
                "message": exc.message,
                "code": exc.error_code,
                "details": exc.details,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
                "stack_trace": traceback.format_exc() if settings.DEBUG else None
            }
            
            error_logger.log_error(exc, {
                "request_id": request_id,
                "error_code": exc.error_code
            })
            
            return JSONResponse(
                status_code=exc.status_code,
                content=error_response
            )
        
        # Handle HTTP exceptions
        if isinstance(exc, HTTPException):
            error_response = {
                "success": False,
                "error": "HTTPException",
                "message": exc.detail,
                "code": str(exc.status_code),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
                "stack_trace": traceback.format_exc() if settings.DEBUG else None
            }
            
            error_logger.log_error(exc, {
                "request_id": request_id,
                "status_code": exc.status_code
            })
            
            return JSONResponse(
                status_code=exc.status_code,
                content=error_response
            )
        
        # Handle unexpected exceptions
        error_response = {
            "success": False,
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "code": "INTERNAL_SERVER_ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "stack_trace": traceback.format_exc() if settings.DEBUG else None
        }
        
        error_logger.log_error(exc, {
            "request_id": request_id
        })
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )


async def betta_fish_exception_handler(request: Request, exc: BettaFishException) -> JSONResponse:
    """Handler for BettaFish exceptions"""
    request_id = getattr(request.state, "request_id", None)
    
    error_response = {
        "success": False,
        "error": exc.__class__.__name__,
        "message": exc.message,
        "code": exc.error_code,
        "details": exc.details,
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "stack_trace": traceback.format_exc() if settings.DEBUG else None
    }
    
    error_logger.log_error(exc, {
        "request_id": request_id,
        "error_code": exc.error_code
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for validation exceptions"""
    request_id = getattr(request.state, "request_id", None)
    
    # Extract validation details if available
    details = []
    if hasattr(exc, 'errors'):
        for error in exc.errors:
            field = '.'.join(str(loc) for loc in error.get('loc', []))
            details.append({
                "field": field,
                "message": error.get('msg', ''),
                "code": error.get('type', '')
            })
    
    error_response = {
        "success": False,
        "error": "ValidationError",
        "message": "Validation failed",
        "code": "VALIDATION_ERROR",
        "details": details,
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "stack_trace": traceback.format_exc() if settings.DEBUG else None
    }
    
    error_logger.log_error(exc, {
        "request_id": request_id,
        "validation_errors": details
    })
    
    return JSONResponse(
        status_code=422,
        content=error_response
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for HTTP exceptions"""
    request_id = getattr(request.state, "request_id", None)
    
    error_response = {
        "success": False,
        "error": "HTTPException",
        "message": exc.detail,
        "code": str(exc.status_code),
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "stack_trace": traceback.format_exc() if settings.DEBUG else None
    }
    
    error_logger.log_error(exc, {
        "request_id": request_id,
        "status_code": exc.status_code
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for general exceptions"""
    request_id = getattr(request.state, "request_id", None)
    
    error_response = {
        "success": False,
        "error": "InternalServerError",
        "message": "An unexpected error occurred",
        "code": "INTERNAL_SERVER_ERROR",
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "stack_trace": traceback.format_exc() if settings.DEBUG else None
    }
    
    error_logger.log_error(exc, {
        "request_id": request_id
    })
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )
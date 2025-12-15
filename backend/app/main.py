import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from core.config import settings, CORS_CONFIG
from core.database import initialize_database, cleanup_database, check_database_health
from core.error_handlers import (
    ErrorHandlingMiddleware,
    betta_fish_exception_handler,
    validation_exception_handler
)
from core.exceptions import BettaFishException
from api import auth, engines, websocket, health
from engines.insight_engine.api.routes import router as insight_router
from engines.media_engine.api.routes import router as media_router
from engines.query_engine.api.routes import router as query_router
from engines.report_engine.api.routes import router as report_router


# Configure logging
# logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting BettaFish FastAPI application")
    
    # Initialize database
    # try:
    #     await initialize_database()
    #     logger.info("Database initialized successfully")
    # except Exception as e:
    #     logger.error(f"Database initialization failed: {e}")
    #     raise
    
    # Start background tasks
    cleanup_task = asyncio.create_task(periodic_cleanup())
    logger.info("Background tasks started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down BettaFish FastAPI application")
    
    # Cancel background tasks
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    
    # Cleanup database connections
    from core.database import db_manager
    await db_manager.disconnect()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    **CORS_CONFIG
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*"] if settings.DEBUG else ["bettafish.example.com"]
)

# Add error handling middleware
app.add_middleware(ErrorHandlingMiddleware)

# Add exception handlers
app.add_exception_handler(BettaFishException, betta_fish_exception_handler)
app.add_exception_handler(Exception, validation_exception_handler)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request"""
    import uuid
    
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Check database health
    db_health = await check_database_health()
    
    if db_health["status"] != "healthy":
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": db_health
            }
        )
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_health
    }


# Include API routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"]
)

app.include_router(
    engines.router,
    prefix=f"{settings.API_V1_STR}/engines",
    tags=["engines"]
)

app.include_router(
    websocket.router,
    prefix="/ws",
    tags=["websocket"]
)

app.include_router(
    insight_router,
    prefix=f"{settings.API_V1_STR}/insight",
    tags=["insight-engine"]
)

app.include_router(
    media_router,
    prefix=f"{settings.API_V1_STR}/media",
    tags=["media-engine"]
)

app.include_router(
    query_router,
    prefix=f"{settings.API_V1_STR}/query",
    tags=["query-engine"]
)

app.include_router(
    report_router,
    prefix=f"{settings.API_V1_STR}/report",
    tags=["report-engine"]
)

app.include_router(
    query_router,
    prefix=f"{settings.API_V1_STR}/query",
    tags=["query-engine"]
)

app.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "docs_url": "/docs" if settings.DEBUG else None,
        "health_url": "/health",
        "api_url": settings.API_V1_STR
    }


# Background task for periodic cleanup
async def periodic_cleanup():
    """Periodic cleanup task"""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            await cleanup_database()
            logger.info("Periodic cleanup completed")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Periodic cleanup failed: {e}")


# Exception handlers for specific error types
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "NotFound",
            "message": f"Endpoint {request.url.path} not found",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    """Handle 405 errors"""
    return JSONResponse(
        status_code=405,
        content={
            "success": False,
            "error": "MethodNotAllowed",
            "message": f"Method {request.method} not allowed for {request.url.path}",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    """Handle 429 errors"""
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": "RateLimitExceeded",
            "message": "Rate limit exceeded, please try again later",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, "request_id", None)
        }
    )


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG
    )
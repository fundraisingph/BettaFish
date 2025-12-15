# FastAPI Backend Architecture for BettaFish

## Overview

This document outlines the FastAPI backend architecture that will replace the Flask-based system, providing better performance, type safety, and developer experience while maintaining all existing functionality.

## Core Architecture Components

### 1. Application Structure
```
backend/
├── app.py                    # FastAPI application entry point
├── main.py                   # Application factory and configuration
├── api/                       # API route modules
│   ├── deps.py              # Dependencies (database, auth, etc.)
│   ├── system.py             # System management endpoints
│   ├── agents.py             # Agent management endpoints
│   ├── reports.py            # Report generation endpoints
│   ├── auth.py               # Authentication endpoints
│   └── websocket.py           # WebSocket endpoints
├── core/                      # Core business logic
│   ├── config.py             # Application configuration
│   ├── security.py           # Security utilities
│   ├── database.py           # Database connection management
│   └── exceptions.py         # Custom exception classes
├── models/                    # Pydantic models
│   ├── user.py               # User-related models
│   ├── agent.py              # Agent-related models
│   ├── report.py             # Report-related models
│   └── common.py             # Common base models
├── services/                  # Business logic services
│   ├── auth.py               # Authentication service
│   ├── agent_manager.py       # Agent process management
│   ├── report_generator.py    # Report generation service
│   └── websocket_manager.py  # WebSocket connection management
├── utils/                     # Utility functions
│   ├── logger.py             # Logging configuration
│   └── helpers.py            # Common helper functions
└── tests/                      # Test suite
    ├── conftest.py            # Pytest configuration
    ├── test_api/             # API tests
    └── test_services/         # Service tests
```

### 2. FastAPI Application Factory
```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from .api import api_router
from .core.config import settings
from .core.database import engine
from .services.websocket_manager import manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_database()
    await initialize_services()
    yield
    # Shutdown
    await cleanup_resources()

def create_app() -> FastAPI:
    app = FastAPI(
        title="BettaFish API",
        description="Multi-agent public opinion analysis system",
        version="2.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Add WebSocket routes
    app.include_router(websocket_router, prefix="/ws")
    
    return app

app = create_app()
```

### 3. Database Connection Management
```python
# backend/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from prisma import Prisma
import asyncio

from .config import settings

# SQLAlchemy for legacy compatibility
async_engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession
)

# Prisma client for new operations
prisma = Prisma()

@asynccontextmanager
async def get_db():
    """Get database session (SQLAlchemy for legacy)"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@asynccontextmanager
async def get_prisma():
    """Get Prisma client"""
    yield prisma

async def initialize_database():
    """Initialize database connections"""
    # Test Prisma connection
    await prisma.connect()
    
    # Test SQLAlchemy connection
    async with get_db() as db:
        await db.execute("SELECT 1")
```

### 4. API Route Structure
```python
# backend/api/system.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any

from ..core.database import get_prisma
from ..services.agent_manager import AgentManager
from ..models.common import SuccessResponse

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/status")
async def get_system_status(prisma=Depends(get_prisma)) -> Dict[str, Any]:
    """Get system status including all agents"""
    agent_manager = AgentManager(prisma)
    return await agent_manager.get_system_status()

@router.post("/start")
async def start_system(
    background_tasks: BackgroundTasks,
    prisma=Depends(get_prisma)
) -> SuccessResponse:
    """Start all system components"""
    agent_manager = AgentManager(prisma)
    await agent_manager.start_all_agents(background_tasks)
    return SuccessResponse(message="System startup initiated")

@router.post("/shutdown")
async def shutdown_system(
    background_tasks: BackgroundTasks,
    prisma=Depends(get_prisma)
) -> SuccessResponse:
    """Gracefully shutdown all components"""
    agent_manager = AgentManager(prisma)
    await agent_manager.shutdown_all_agents(background_tasks)
    return SuccessResponse(message="System shutdown initiated")
```

### 5. WebSocket Implementation
```python
# backend/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict, Any
import json
import asyncio

from ..core.database import get_prisma
from ..services.websocket_manager import manager
from ..models.common import WebSocketMessage

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/agents/{agent_type}")
async def agent_websocket_endpoint(
    websocket: WebSocket,
    agent_type: str,
    prisma=Depends(get_prisma)
):
    """WebSocket endpoint for agent real-time logs"""
    await manager.connect_agent(websocket, agent_type)
    
    try:
        while True:
            # Receive message from agent
            data = await websocket.receive_text()
            message = WebSocketMessage.parse_raw(data)
            
            # Broadcast to frontend
            await manager.broadcast_to_frontend({
                "type": "agent_log",
                "agent_type": agent_type,
                "message": message.content,
                "timestamp": message.timestamp
            })
            
    except WebSocketDisconnect:
        await manager.disconnect_agent(websocket, agent_type)

@router.websocket("/frontend")
async def frontend_websocket_endpoint(
    websocket: WebSocket,
    prisma=Depends(get_prisma)
):
    """WebSocket endpoint for frontend clients"""
    await manager.connect_frontend(websocket)
    
    try:
        while True:
            # Receive commands from frontend
            data = await websocket.receive_text()
            command = WebSocketMessage.parse_raw(data)
            
            # Handle frontend commands
            await handle_frontend_command(command, prisma)
            
    except WebSocketDisconnect:
        await manager.disconnect_frontend(websocket)
```

### 6. Agent Management Service
```python
# backend/services/agent_manager.py
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from ..core.database import get_prisma
from ..models.agent import Agent, AgentStatus, AgentType
from ..utils.logger import get_logger

logger = get_logger(__name__)

class AgentManager:
    def __init__(self, prisma):
        self.prisma = prisma
        self.running_agents: Dict[str, asyncio.Task] = {}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        agents = await self.prisma.agent.find_many()
        
        return {
            "started": any(agent.status == AgentStatus.RUNNING for agent in agents),
            "agents": [
                {
                    "type": agent.type,
                    "status": agent.status,
                    "port": agent.port,
                    "last_seen": agent.updatedAt
                }
                for agent in agents
            ]
        }
    
    async def start_all_agents(self, background_tasks: BackgroundTasks):
        """Start all agents asynchronously"""
        agent_types = [AgentType.INSIGHT, AgentType.MEDIA, AgentType.QUERY, AgentType.FORUM]
        
        for agent_type in agent_types:
            task = background_tasks.add_task(
                self._start_agent_process,
                agent_type
            )
            self.running_agents[agent_type] = task
            
            # Update agent status in database
            await self.prisma.agent.update(
                where={"type": agent_type},
                data={
                    "status": AgentStatus.STARTING,
                    "updatedAt": datetime.utcnow()
                }
            )
    
    async def _start_agent_process(self, agent_type: str):
        """Start individual agent process"""
        logger.info(f"Starting agent: {agent_type}")
        
        try:
            # Import and start agent-specific process
            if agent_type == AgentType.INSIGHT:
                from ..agents.insight import start_insight_agent
                await start_insight_agent()
            elif agent_type == AgentType.MEDIA:
                from ..agents.media import start_media_agent
                await start_media_agent()
            elif agent_type == AgentType.QUERY:
                from ..agents.query import start_query_agent
                await start_query_agent()
            elif agent_type == AgentType.FORUM:
                from ..agents.forum import start_forum_agent
                await start_forum_agent()
            
            # Update status to running
            await self.prisma.agent.update(
                where={"type": agent_type},
                data={
                    "status": AgentStatus.RUNNING,
                    "updatedAt": datetime.utcnow()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to start agent {agent_type}: {e}")
            
            # Update status to error
            await self.prisma.agent.update(
                where={"type": agent_type},
                data={
                    "status": AgentStatus.ERROR,
                    "updatedAt": datetime.utcnow()
                }
            )
    
    async def stop_all_agents(self):
        """Stop all running agents"""
        for agent_type, task in self.running_agents.items():
            if task and not task.done():
                task.cancel()
                
                # Update agent status
                await self.prisma.agent.update(
                    where={"type": agent_type},
                    data={
                        "status": AgentStatus.STOPPED,
                        "updatedAt": datetime.utcnow()
                    }
                )
        
        self.running_agents.clear()
```

### 7. Authentication System
```python
# backend/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Get password hash"""
    return pwd_context.hash(password)
```

### 8. Error Handling and Validation
```python
# backend/core/exceptions.py
from fastapi import HTTPException
from typing import Dict, Any, Optional

class BettaFishException(Exception):
    """Base exception for BettaFish application"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
    
    def __str__(self):
        return self.message

class AuthenticationError(BettaFishException):
    """Authentication related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 401, details)

class AuthorizationError(BettaFishException):
    """Authorization related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 403, details)

class ValidationError(BettaFishException):
    """Validation related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 422, details)

class AgentError(BettaFishException):
    """Agent related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)

# FastAPI exception handler
async def bettafish_exception_handler(request, exc: BettaFishException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details
        }
    )
```

### 9. Configuration Management
```python
# backend/core/config.py
from pydantic import BaseSettings, Field
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "BettaFish API"
    VERSION: str = "2.0.0"
    DEBUG: bool = Field(False, env="DEBUG")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        ["http://localhost:3000", "https://yourdomain.com"],
        env="ALLOWED_ORIGINS"
    )
    
    # Agent Configuration
    AGENT_TIMEOUT: int = Field(300, env="AGENT_TIMEOUT")
    MAX_CONCURRENT_AGENTS: int = Field(10, env="MAX_CONCURRENT_AGENTS")
    
    # LLM Configuration (inherited from existing)
    INSIGHT_ENGINE_API_KEY: Optional[str] = Field(None, env="INSIGHT_ENGINE_API_KEY")
    INSIGHT_ENGINE_BASE_URL: Optional[str] = Field(None, env="INSIGHT_ENGINE_BASE_URL")
    INSIGHT_ENGINE_MODEL_NAME: str = Field("kimi-k2-0711-preview", env="INSIGHT_ENGINE_MODEL_NAME")
    
    # ... other LLM configurations
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## Migration Strategy

### 1. Parallel Deployment
- Run Flask and FastAPI simultaneously during transition
- Use feature flags to control which backend handles requests
- Gradually migrate users to FastAPI endpoints
- Maintain database compatibility between both systems

### 2. Agent Process Migration
- Convert subprocess-based agent management to async tasks
- Implement proper process lifecycle management
- Add health checks and monitoring
- Ensure graceful shutdown and restart capabilities

### 3. WebSocket Migration
- Replace Socket.IO with native WebSockets
- Implement connection pooling and management
- Add message queuing and broadcasting
- Maintain backward compatibility with existing client code

### 4. Database Migration
- Use Prisma alongside SQLAlchemy during transition
- Implement data synchronization between ORMs
- Gradually migrate queries to Prisma
- Ensure data integrity throughout migration

## Performance Optimizations

### 1. Async Processing
- Convert all I/O operations to async/await
- Implement connection pooling for database
- Use async HTTP clients for external APIs
- Optimize concurrent request handling

### 2. Caching Strategy
- Implement Redis for session storage
- Add response caching for frequently accessed data
- Cache agent status and system state
- Use CDN for static assets

### 3. Database Optimization
- Add proper database indexes
- Implement query optimization
- Use connection pooling
- Add database monitoring and metrics

## Security Enhancements

### 1. Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control
- Session management with Redis
- API key authentication for external integrations

### 2. Input Validation
- Pydantic models for request/response validation
- SQL injection prevention with Prisma
- XSS protection with proper sanitization
- Rate limiting and request throttling

### 3. CORS and Security Headers
- Proper CORS configuration
- Security headers (HSTS, CSP, etc.)
- API versioning support
- Request logging and monitoring

## Testing Strategy

### 1. Unit Testing
- Pytest with async support
- Mock external dependencies
- Test coverage for all endpoints
- Database transaction testing

### 2. Integration Testing
- End-to-end workflow testing
- Agent coordination testing
- WebSocket communication testing
- Database integration testing

### 3. Performance Testing
- Load testing with concurrent users
- Database query performance testing
- Memory usage profiling
- Response time benchmarking

This FastAPI architecture provides a solid foundation for BettaFish's next phase of development, offering improved performance, type safety, and developer experience while maintaining all existing functionality.
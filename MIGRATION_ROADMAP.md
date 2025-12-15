# BettaFish Migration Roadmap: Flask to FastAPI with Prisma ORM

## Executive Summary

This document outlines the comprehensive migration strategy for transitioning BettaFish from a Flask-based architecture to FastAPI with Prisma ORM and PostgreSQL database. The migration will maintain backward compatibility while improving performance, type safety, and developer experience.

## Current Architecture Analysis

### Existing Flask Architecture
- **Main Orchestrator**: Flask app.py with SocketIO for real-time communication
- **Process Management**: Subprocess-based management of Streamlit applications
- **Database**: SQLAlchemy with PostgreSQL/MySQL support
- **Real-time Communication**: Flask-SocketIO for agent coordination
- **Configuration**: Pydantic Settings with .env file support
- **Frontend**: Next.js 15 with TypeScript and Tailwind CSS

### Key Migration Points
1. **API Layer**: Flask routes → FastAPI endpoints
2. **Database Layer**: SQLAlchemy → Prisma ORM
3. **Real-time Communication**: Flask-SocketIO → FastAPI WebSockets
4. **Process Management**: Subprocess → Async task management
5. **Authentication**: Basic → JWT-based auth system
6. **Error Handling**: Flask error handlers → FastAPI exception handlers
7. **Configuration**: Pydantic Settings (maintain with enhancements)
8. **Frontend Integration**: SocketIO client → WebSocket client

## Migration Phases

### Phase 1: Foundation Setup (Week 1-2)

#### 1.1 Database Schema Design with Prisma
- Create comprehensive Prisma schema for all data models
- Design relationships between agents, reports, and user data
- Implement migrations from existing SQLAlchemy models
- Set up PostgreSQL with proper indexing

#### 1.2 FastAPI Backend Structure
- Create new FastAPI application structure
- Implement dependency injection system
- Set up CORS and middleware configuration
- Create base API response models

#### 1.3 Development Environment Setup
- Create new Docker configuration for FastAPI
- Set up development database with Prisma
- Configure environment variables
- Create migration scripts

### Phase 2: Core API Migration (Week 3-4)

#### 2.1 System Management APIs
- Convert Flask system routes to FastAPI endpoints
- Implement async task management for agent processes
- Create health check endpoints
- Migrate configuration management APIs

#### 2.2 Agent Communication APIs
- Convert agent start/stop/status endpoints
- Implement real-time log streaming
- Create agent coordination APIs
- Migrate search interfaces

#### 2.3 Report Generation APIs
- Convert ReportEngine Flask blueprint to FastAPI router
- Implement async report generation
- Create file management endpoints
- Migrate PDF export functionality

### Phase 3: Real-time Communication (Week 5-6)

#### 3.1 WebSocket Implementation
- Replace SocketIO with FastAPI WebSockets
- Implement connection management
- Create message broadcasting system
- Handle agent coordination via WebSockets

#### 3.2 Frontend WebSocket Client
- Update Next.js to use WebSocket client
- Migrate Socket.IO event handlers
- Implement reconnection logic
- Update real-time UI components

### Phase 4: Agent Engine Migration (Week 7-8)

#### 4.1 Insight Engine Migration
- Convert Streamlit subprocess management to async tasks
- Migrate database operations to Prisma
- Update LLM integration for async patterns
- Maintain backward compatibility

#### 4.2 Media Engine Migration
- Migrate multimodal processing to async
- Update search tool integration
- Convert content analysis pipelines
- Optimize for concurrent processing

#### 4.3 Query Engine Migration
- Convert search optimization to async
- Migrate result processing pipelines
- Update query formulation logic
- Implement caching mechanisms

#### 4.4 Report Engine Migration
- Convert report generation to async
- Migrate template system
- Update IR (Intermediate Representation) handling
- Optimize PDF generation pipeline

### Phase 5: Authentication & Security (Week 9-10)

#### 5.1 Authentication System
- Implement JWT-based authentication
- Create user management APIs
- Add role-based access control
- Implement session management

#### 5.2 Security Enhancements
- Add API rate limiting
- Implement input validation
- Add CORS configuration
- Create security middleware

### Phase 6: Testing & Deployment (Week 11-12)

#### 6.1 Testing Strategy
- Create comprehensive test suite
- Implement integration tests
- Add performance benchmarks
- Create load testing scenarios

#### 6.2 Deployment Preparation
- Update Docker configurations
- Create migration scripts
- Prepare production environment
- Document deployment procedures

## Technical Implementation Details

### Database Schema Design

#### Core Models
```prisma
// User management
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  username  String   @unique
  role      UserRole  @default(USER)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

// Agent management
model Agent {
  id          String   @id @default(cuid())
  name        String
  type        AgentType
  status      AgentStatus
  port        Int?
  config      Json?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}

// Analysis tasks
model AnalysisTask {
  id          String   @id @default(cuid())
  query       String
  status      TaskStatus
  userId      String
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  // Relations
  user        User       @relation(fields: [userId])
  reports     Report[]
  agentLogs   AgentLog[]
}

// Reports
model Report {
  id          String   @id @default(cuid())
  title       String
  content     String
  format      ReportFormat
  taskId      String
  filePath    String?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  // Relations
  task        AnalysisTask @relation(fields: [taskId])
  metadata    ReportMetadata[]
}

// Agent logs
model AgentLog {
  id        String   @id @default(cuid())
  agentId   String
  level     LogLevel
  message   String
  metadata  Json?
  timestamp DateTime @default(now())
  
  // Relations
  agent     Agent @relation(fields: [agentId])
  task      AnalysisTask @relation(fields: [taskId])
}

// Report metadata
model ReportMetadata {
  id         String   @id @default(cuid())
  reportId   String
  key        String
  value      String
  createdAt DateTime @default(now())
  
  // Relations
  report     Report @relation(fields: [reportId])
}

// Enums
enum UserRole {
  USER
  ADMIN
}

enum AgentType {
  INSIGHT
  MEDIA
  QUERY
  REPORT
  FORUM
}

enum AgentStatus {
  STOPPED
  STARTING
  RUNNING
  ERROR
}

enum TaskStatus {
  PENDING
  RUNNING
  COMPLETED
  FAILED
}

enum ReportFormat {
  HTML
  PDF
  MARKDOWN
}

enum LogLevel {
  DEBUG
  INFO
  WARNING
  ERROR
}
```

### FastAPI Application Structure

```python
# backend/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import asyncio

app = FastAPI(
    title="BettaFish API",
    description="Multi-agent public opinion analysis system",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication
security = HTTPBearer()

# Database connection
@asynccontextmanager
async def get_db():
    async with Prisma() as db:
        yield db

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.agent_tasks: Dict[str, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()
```

### API Endpoint Migration

#### System Management
```python
# backend/api/system.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/status")
async def get_system_status():
    """Get system status including all agents"""
    return {
        "started": system_state.started,
        "starting": system_state.starting,
        "agents": await get_all_agent_status()
    }

@router.post("/start")
async def start_system(background_tasks: BackgroundTasks):
    """Start all system components"""
    if system_state.starting:
        raise HTTPException(status_code=400, detail="System already starting")
    
    # Start all agents asynchronously
    for agent_type in AgentType:
        background_tasks.add_task(start_agent, agent_type)
    
    return {"message": "System startup initiated"}

@router.post("/shutdown")
async def shutdown_system():
    """Gracefully shutdown all components"""
    # Stop all agents
    await stop_all_agents()
    
    # Stop WebSocket connections
    await manager.disconnect_all()
    
    return {"message": "System shutdown initiated"}
```

#### Agent Management
```python
# backend/api/agents.py
from fastapi import APIRouter, Depends, WebSocket
from typing import Dict, Any

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.get("/{agent_type}")
async def get_agent_status(agent_type: AgentType):
    """Get status of specific agent"""
    agent = await get_agent_by_type(agent_type)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "type": agent.type,
        "status": agent.status,
        "port": agent.port,
        "last_update": agent.updatedAt
    }

@router.post("/{agent_type}/start")
async def start_agent(
    agent_type: AgentType,
    background_tasks: BackgroundTasks
):
    """Start specific agent"""
    agent = await get_agent_by_type(agent_type)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent.status != AgentStatus.STOPPED:
        raise HTTPException(status_code=409, detail="Agent already running")
    
    # Start agent asynchronously
    background_tasks.add_task(start_agent_process, agent_type)
    
    return {"message": f"{agent_type} agent starting"}

@router.websocket("/{agent_type}/ws")
async def agent_websocket_endpoint(
    websocket: WebSocket,
    agent_type: AgentType
):
    """WebSocket endpoint for agent real-time logs"""
    await manager.connect(websocket)
    
    try:
        # Start agent process
        process = await start_agent_process(agent_type)
        
        # Stream logs
        async for log_line in stream_agent_logs(process):
            await websocket.send_json({
                "type": "log",
                "agent": agent_type,
                "message": log_line
            })
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        await stop_agent_process(agent_type)
```

### Frontend Integration

#### WebSocket Client Hook
```typescript
// frontend/src/hooks/use-websocket.ts
import { useEffect, useRef, useState } from 'react'
import { WebSocket } from 'utils/websocket'

export function useWebSocket(url: string) {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)
  const [messages, setMessages] = useState<any[]>([])
  
  useEffect(() => {
    const ws = new WebSocket(url)
    
    ws.onopen = () => {
      setConnected(true)
      setSocket(ws)
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setMessages(prev => [...prev, data])
    }
    
    ws.onclose = () => {
      setConnected(false)
      setSocket(null)
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    return () => {
      ws.close()
    }
  }, [url])
  
  const sendMessage = (message: any) => {
    if (socket && connected) {
      socket.send(JSON.stringify(message))
    }
  }
  
  return { connected, messages, sendMessage }
}
```

#### API Client Integration
```typescript
// frontend/src/lib/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
})

export const systemAPI = {
  getStatus: () => api.get('/api/system/status'),
  start: () => api.post('/api/system/start'),
  shutdown: () => api.post('/api/system/shutdown'),
}

export const agentsAPI = {
  getStatus: (type: string) => api.get(`/api/agents/${type}`),
  start: (type: string) => api.post(`/api/agents/${type}/start`),
  stop: (type: string) => api.post(`/api/agents/${type}/stop`),
}

export const reportsAPI = {
  generate: (data: any) => api.post('/api/reports/generate', data),
  download: (id: string) => api.get(`/api/reports/${id}/download`),
}
```

## Migration Strategy

### Backward Compatibility

1. **Parallel Deployment**: Run Flask and FastAPI side-by-side during migration
2. **Feature Flags**: Use environment variables to control which backend serves requests
3. **API Versioning**: Implement /api/v1/ (Flask) and /api/v2/ (FastAPI) endpoints
4. **Database Compatibility**: Ensure both ORMs can work with the same database
5. **Gradual Rollout**: Migrate users incrementally by feature

### Data Migration Plan

1. **Schema Analysis**: Compare SQLAlchemy models with Prisma schema
2. **Migration Scripts**: Create Prisma migrations for all existing data
3. **Data Validation**: Verify data integrity after migration
4. **Rollback Strategy**: Keep Flask available during transition period
5. **Testing**: Validate all operations with migrated data

### Testing Strategy

1. **Unit Tests**: Test all FastAPI endpoints
2. **Integration Tests**: Test agent coordination and WebSocket communication
3. **Load Tests**: Test system under concurrent user load
4. **Performance Tests**: Compare FastAPI vs Flask performance
5. **E2E Tests**: Test complete user workflows

## Deployment Strategy

### Development Environment
```bash
# Clone new branch
git checkout -b feature/fastapi-migration

# Set up FastAPI environment
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up database
prisma migrate dev
prisma generate

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Generate Prisma client
RUN prisma generate

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: "3.9"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://bettafish:password@db:5432/bettafish
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: bettafish
      POSTGRES_PASSWORD: password
      POSTGRES_DB: bettafish
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Troubleshooting Guide

### Common Issues

1. **WebSocket Connection Failures**
   - Check CORS configuration
   - Verify WebSocket endpoint URLs
   - Ensure proper authentication headers

2. **Database Connection Errors**
   - Verify Prisma schema alignment
   - Check database connection strings
   - Run Prisma migrations

3. **Agent Process Management**
   - Check async task configuration
   - Verify process permissions
   - Monitor resource usage

4. **Performance Issues**
   - Monitor database query performance
   - Check WebSocket connection limits
   - Optimize async operations

### Debugging Tools

1. **Logging Enhancement**
   ```python
   import structlog
   logger = structlog.get_logger()
   ```

2. **Performance Monitoring**
   ```python
   from prometheus_client import Counter, Histogram
   
   request_count = Counter('requests_total')
   request_duration = Histogram('request_duration_seconds')
   ```

3. **Health Checks**
   ```python
   @app.get("/health")
   async def health_check():
       return {
           "status": "healthy",
           "timestamp": datetime.utcnow(),
           "version": "2.0.0"
       }
   ```

## Timeline

| Phase | Duration | Start Date | End Date | Dependencies |
|--------|----------|------------|----------|-------------|
| Foundation Setup | 2 weeks | Week 1 | Week 2 | - |
| Core API Migration | 2 weeks | Week 3 | Week 4 | Phase 1 |
| Real-time Communication | 2 weeks | Week 5 | Week 6 | Phase 2 |
| Agent Engine Migration | 2 weeks | Week 7 | Week 8 | Phase 3 |
| Authentication & Security | 2 weeks | Week 9 | Week 10 | Phase 4 |
| Testing & Deployment | 2 weeks | Week 11 | Week 12 | Phase 5 |

## Success Criteria

1. **Functional Parity**: All Flask features work in FastAPI
2. **Performance Improvement**: 20% faster response times
3. **Type Safety**: 100% type coverage for API endpoints
4. **Test Coverage**: 90%+ test coverage
5. **Documentation**: Complete API documentation
6. **Deployment Success**: Production deployment without issues

## Rollback Plan

1. **Immediate Rollback**: Switch back to Flask if critical issues
2. **Data Integrity**: Ensure no data loss during rollback
3. **User Communication**: Notify users of any service interruptions
4. **Post-mortem**: Analyze migration issues for future improvements

## Conclusion

This migration roadmap provides a comprehensive approach to transitioning BettaFish from Flask to FastAPI with Prisma ORM. The phased approach minimizes risk while ensuring backward compatibility and maintaining system functionality throughout the migration process.

The new architecture will provide:
- Better performance with async processing
- Improved type safety with Prisma
- Enhanced developer experience
- More scalable real-time communication
- Better testing and debugging capabilities

Successful execution of this roadmap will position BettaFish for future growth and improved maintainability.
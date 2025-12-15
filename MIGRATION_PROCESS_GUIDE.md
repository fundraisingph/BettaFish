# BettaFish Migration Process and Troubleshooting Guide

## Overview

This document provides a comprehensive guide for migrating BettaFish from Flask to FastAPI, including step-by-step processes, troubleshooting procedures, and best practices for a smooth transition.

## Migration Timeline

### Overall Schedule (12 Weeks)

```mermaid
gantt
    title BettaFish Migration Timeline
    dateFormat  YYYY-MM-DD
    section Preparation
    Environment Setup     :prep1, 2024-01-01, 1w
    Database Migration    :prep2, after prep1, 1w
    section Backend Migration
    InsightEngine        :backend1, after prep2, 2w
    MediaEngine         :backend2, after backend1, 2w
    QueryEngine         :backend3, after backend2, 2w
    ReportEngine        :backend4, after backend3, 2w
    section Frontend Integration
    API Client Migration :frontend1, after backend1, 2w
    WebSocket Integration :frontend2, after backend2, 1w
    UI Updates          :frontend3, after backend4, 1w
    section Testing & Deployment
    Integration Testing :test1, after frontend3, 1w
    Production Deployment :deploy1, after test1, 1w
```

## Detailed Migration Process

### Phase 0: Preparation (Weeks 0-1)

#### 0.1 Environment Setup
```bash
# 1. Create new backend structure
mkdir -p backend/{app,core,engines,services,models,api,tests}

# 2. Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install FastAPI and dependencies
pip install fastapi uvicorn prisma pydantic python-jose[cryptography]
pip install pytest pytest-asyncio pytest-cov black flake8

# 4. Initialize Prisma
cd backend
prisma init
```

#### 0.2 Database Migration
```bash
# 1. Export existing data from Flask database
python scripts/export_flask_data.py

# 2. Create Prisma schema
# (Use the schema from PRISMA_SCHEMA.md)

# 3. Run Prisma migrations
prisma migrate dev --name init

# 4. Import data to new schema
python scripts/import_to_prisma.py
```

#### 0.3 Configuration Setup
```python
# backend/core/config.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/bettafish"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "BettaFish"
    
    # Debug
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Phase 1: InsightEngine Migration (Weeks 2-3)

#### 1.1 Database Layer Migration
```python
# backend/engines/insight/database.py
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.core.database import get_prisma
from backend.models.insight import InsightSearch, InsightResult

class InsightDatabase:
    def __init__(self):
        self.prisma = get_prisma()
    
    async def migrate_from_flask(self, flask_data: List[Dict]) -> bool:
        """Migrate data from Flask database"""
        try:
            for item in flask_data:
                # Convert Flask data to Prisma format
                prisma_data = self._convert_flask_to_prisma(item)
                
                # Save to Prisma database
                await self.prisma.insightsearch.create(data=prisma_data)
            
            return True
        except Exception as e:
            print(f"Migration error: {e}")
            return False
    
    def _convert_flask_to_prisma(self, flask_item: Dict) -> Dict:
        """Convert Flask data format to Prisma format"""
        return {
            "id": flask_item.get("id"),
            "query": flask_item.get("query"),
            "platform": flask_item.get("platform"),
            "results": flask_item.get("results", []),
            "createdAt": flask_item.get("created_at"),
            "updatedAt": flask_item.get("updated_at"),
            "isActive": True
        }
```

#### 1.2 Agent Migration
```python
# backend/engines/insight/agent.py
# (Implementation from ENGINE_MIGRATION_STRATEGY.md)
```

#### 1.3 API Endpoint Migration
```python
# backend/api/engines/insight.py
# (Implementation from ENGINE_MIGRATION_STRATEGY.md)
```

#### 1.4 Testing Migration
```bash
# 1. Run unit tests
pytest tests/unit/engines/test_insight.py -v

# 2. Run integration tests
pytest tests/integration/test_insight_api.py -v

# 3. Run performance tests
locust -f tests/performance/insight_locustfile.py --host=http://localhost:8000
```

### Phase 2: MediaEngine Migration (Weeks 4-5)

#### 2.1 Web Search Integration
```python
# backend/engines/media/web_search.py
# (Implementation from ENGINE_MIGRATION_STRATEGY.md)
```

#### 2.2 Multimodal Analysis
```python
# backend/engines/media/multimodal_analyzer.py
# (Implementation from ENGINE_MIGRATION_STRATEGY.md)
```

#### 2.3 API Integration
```python
# backend/api/engines/media.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from backend.core.database import get_prisma
from backend.models.validation import MediaAnalysisRequest
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/engines/media", tags=["media"])

@router.post("/analyze")
async def analyze_media(
    request: MediaAnalysisRequest,
    user: dict = Depends(get_current_user),
    prisma = Depends(get_prisma)
):
    """Start media analysis"""
    # Implementation from ENGINE_MIGRATION_STRATEGY.md
    pass
```

### Phase 3: QueryEngine Migration (Weeks 6-7)

#### 3.1 Query Optimization
```python
# backend/engines/query/query_optimizer.py
# (Implementation from ENGINE_MIGRATION_STRATEGY.md)
```

#### 3.2 Result Ranking
```python
# backend/engines/query/result_ranker.py
from typing import List, Dict, Any
import numpy as np

class ResultRanker:
    def __init__(self):
        self.weights = {
            "relevance": 0.4,
            "freshness": 0.2,
            "authority": 0.2,
            "popularity": 0.2
        }
    
    def rank_results(self, query: str, results: List[Dict]) -> List[Dict]:
        """Rank search results by relevance"""
        scored_results = []
        
        for result in results:
            score = self._calculate_score(query, result)
            scored_results.append({**result, "relevance_score": score})
        
        # Sort by score (descending)
        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return scored_results
    
    def _calculate_score(self, query: str, result: Dict) -> float:
        """Calculate relevance score for a result"""
        # Implement scoring algorithm
        relevance = self._calculate_relevance(query, result)
        freshness = self._calculate_freshness(result)
        authority = self._calculate_authority(result)
        popularity = self._calculate_popularity(result)
        
        score = (
            relevance * self.weights["relevance"] +
            freshness * self.weights["freshness"] +
            authority * self.weights["authority"] +
            popularity * self.weights["popularity"]
        )
        
        return score
```

### Phase 4: ReportEngine Migration (Weeks 8-9)

#### 4.1 Report Generation
```python
# backend/engines/report/report_generator.py
# (Implementation from ENGINE_MIGRATION_STRATEGY.md)
```

#### 4.2 Template System
```python
# backend/services/template_service.py
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader

class TemplateService:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader("templates"))
    
    async def render_html(self, ir: Dict, template_name: str) -> str:
        """Render HTML report from intermediate representation"""
        template = self.env.get_template(f"{template_name}.html")
        return template.render(**ir)
    
    async def get_template_structure(self, template_name: str) -> Dict:
        """Get template structure"""
        # Load template configuration
        pass
```

### Phase 5: Frontend Integration (Weeks 10-11)

#### 5.1 API Client Migration
```typescript
// frontend/src/lib/api-client.ts
// (Implementation from FRONTEND_INTEGRATION_PLAN.md)
```

#### 5.2 WebSocket Integration
```typescript
// frontend/src/lib/websocket-client.ts
// (Implementation from FRONTEND_INTEGRATION_PLAN.md)
```

#### 5.3 Component Updates
```typescript
// frontend/src/components/analysis-dashboard.tsx
// (Implementation from FRONTEND_INTEGRATION_PLAN.md)
```

### Phase 6: Testing and Deployment (Weeks 12)

#### 6.1 Integration Testing
```bash
# 1. Run full integration test suite
pytest tests/integration/ -v

# 2. Run end-to-end tests
npx playwright test

# 3. Run performance tests
locust -f tests/performance/full_system_locustfile.py --host=http://localhost:8000
```

#### 6.2 Production Deployment
```bash
# 1. Build Docker images
docker build -t bettafish/backend:latest ./backend
docker build -t bettafish/frontend:latest ./frontend

# 2. Deploy to staging
kubectl apply -f k8s/staging/

# 3. Run smoke tests
python scripts/smoke_tests.py --environment=staging

# 4. Deploy to production (blue-green)
kubectl apply -f k8s/production/
```

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Database Migration Issues

**Problem**: Prisma migration fails with constraint errors
```
Error: Migration failed with constraint violation
```

**Solution**:
```bash
# 1. Check existing constraints
prisma db pull

# 2. Review schema differences
prisma diff

# 3. Reset database if needed (WARNING: This deletes data)
prisma migrate reset

# 4. Re-run migration with force flag
prisma migrate dev --name fix_constraints --force
```

**Problem**: Data import fails with type mismatch
```
Error: Type mismatch in field 'createdAt'
```

**Solution**:
```python
# In migration script, handle type conversion
def convert_date(flask_date):
    if isinstance(flask_date, str):
        return datetime.fromisoformat(flask_date.replace('Z', '+00:00'))
    return flask_date

# Apply conversion before import
for item in flask_data:
    item['createdAt'] = convert_date(item.get('created_at'))
    item['updatedAt'] = convert_date(item.get('updated_at'))
```

#### 2. Authentication Issues

**Problem**: JWT token validation fails
```
Error: Invalid token signature
```

**Solution**:
```python
# Check JWT configuration
import jwt
from backend.core.config import settings

try:
    # Test token generation
    token = jwt.encode(
        {"sub": "test", "exp": datetime.utcnow() + timedelta(minutes=30)},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    print(f"Generated token: {token}")
    
    # Test token validation
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    print(f"Decoded payload: {payload}")
except Exception as e:
    print(f"JWT error: {e}")
```

**Problem**: User permissions not working correctly
```
Error: Access denied for user role
```

**Solution**:
```python
# Check user role assignment
async def debug_user_permissions(user_id: str):
    prisma = get_prisma()
    user = await prisma.user.find_unique(
        where={"id": user_id},
        include={"role": True}
    )
    
    print(f"User: {user}")
    print(f"Role: {user.get('role')}")
    print(f"Permissions: {user.get('role', {}).get('permissions', [])}")
```

#### 3. WebSocket Connection Issues

**Problem**: WebSocket connection fails
```
Error: WebSocket connection closed: 1006
```

**Solution**:
```typescript
// Check WebSocket URL and authentication
const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}?token=${token}`;
console.log(`Connecting to: ${wsUrl}`);

// Add connection timeout
const ws = new WebSocket(wsUrl);
ws.timeout = 5000; // 5 second timeout

ws.onopen = () => {
  console.log('WebSocket connected successfully');
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
  console.log('Check URL, token, and server status');
};
```

**Problem**: Real-time updates not working
```
Error: No messages received from WebSocket
```

**Solution**:
```python
# Check WebSocket message routing
async def debug_websocket_routing():
    manager = WebSocketManager()
    
    # Check connection count
    print(f"Frontend connections: {len(manager.frontend_connections)}")
    print(f"Agent connections: {manager.agent_connections}")
    
    # Test message broadcast
    await manager.broadcast_to_frontend({
        "type": "test",
        "message": "Debug message"
    })
```

#### 4. Performance Issues

**Problem**: Slow API response times
```
Warning: Response time > 2 seconds
```

**Solution**:
```python
# Add performance monitoring
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

# Apply to slow endpoints
@monitor_performance
async def slow_endpoint():
    # Endpoint implementation
    pass
```

**Problem**: Memory usage increasing over time
```
Error: Memory usage > 80%
```

**Solution**:
```python
# Add memory monitoring
import psutil
import gc

def check_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_percent = process.memory_percent()
    
    print(f"Memory usage: {memory_percent:.1f}%")
    print(f"RSS: {memory_info.rss / 1024 / 1024:.1f} MB")
    
    if memory_percent > 80:
        print("High memory usage detected, forcing garbage collection")
        gc.collect()
```

#### 5. Agent Communication Issues

**Problem**: Agent processes not starting
```
Error: Agent failed to start
```

**Solution**:
```python
# Debug agent startup
async def debug_agent_startup(agent_type: str):
    try:
        # Check agent configuration
        prisma = get_prisma()
        agent = await prisma.agent.find_unique(where={"type": agent_type})
        print(f"Agent config: {agent}")
        
        # Check required dependencies
        import importlib
        module = importlib.import_module(f"backend.engines.{agent_type}")
        print(f"Module loaded: {module}")
        
        # Test agent instantiation
        from backend.engines.insight.agent import InsightAgent
        test_agent = InsightAgent(agent)
        print(f"Agent created: {test_agent}")
        
    except Exception as e:
        print(f"Agent startup error: {e}")
        import traceback
        traceback.print_exc()
```

**Problem**: Forum collaboration not working
```
Error: Forum messages not being processed
```

**Solution**:
```python
# Debug forum communication
async def debug_forum_communication():
    forum_service = ForumService(get_prisma())
    
    # Check active discussions
    discussions = await forum_service.get_active_discussions()
    print(f"Active discussions: {len(discussions)}")
    
    # Test message processing
    test_message = {
        "type": "forum_message",
        "data": {
            "discussion_id": "test_discussion",
            "sender": "HOST",
            "content": "Test message"
        }
    }
    
    await forum_service.process_message(test_message)
    print("Message processed successfully")
```

### Monitoring and Debugging Tools

#### 1. Health Check Endpoints
```python
# backend/api/health.py
from fastapi import APIRouter, Depends
from datetime import datetime
import psutil
import asyncio

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "database": await check_database_health(),
        "redis": await check_redis_health()
    }

async def check_database_health():
    """Check database connection"""
    try:
        prisma = get_prisma()
        await prisma.execute_raw("SELECT 1")
        return {"status": "healthy", "response_time": "< 100ms"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_redis_health():
    """Check Redis connection"""
    try:
        redis = redis.from_url(settings.REDIS_URL)
        await redis.ping()
        return {"status": "healthy", "response_time": "< 50ms"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

#### 2. Logging Configuration
```python
# backend/core/logging.py
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Configure structured logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_event(self, event_type: str, data: dict):
        """Log structured event"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.logger.info(json.dumps(log_data))

# Usage
logger = StructuredLogger("bettafish")
logger.log_event("agent_started", {"agent_type": "insight", "task_id": "123"})
```

#### 3. Debug Scripts
```python
# scripts/debug_system.py
import asyncio
import sys
from backend.core.database import get_prisma
from backend.services.websocket_manager import manager

async def debug_system():
    """Debug system components"""
    print("=== BettaFish System Debug ===")
    
    # Check database connection
    try:
        prisma = get_prisma()
        result = await prisma.execute_raw("SELECT 1")
        print("✓ Database connection: OK")
    except Exception as e:
        print(f"✗ Database connection: {e}")
    
    # Check WebSocket connections
    try:
        frontend_count = len(manager.frontend_connections)
        agent_count = sum(len(conns) for conns in manager.agent_connections.values())
        print(f"✓ WebSocket connections: {frontend_count} frontend, {agent_count} agents")
    except Exception as e:
        print(f"✗ WebSocket connections: {e}")
    
    # Check agent status
    try:
        prisma = get_prisma()
        agents = await prisma.agent.find_many()
        for agent in agents:
            status = "✓" if agent["status"] == "idle" else "⚠"
            print(f"{status} Agent {agent['type']}: {agent['status']}")
    except Exception as e:
        print(f"✗ Agent status: {e}")
    
    print("=== Debug Complete ===")

if __name__ == "__main__":
    asyncio.run(debug_system())
```

### Emergency Procedures

#### 1. System Rollback
```bash
# 1. Immediate rollback to Flask
kubectl set image deployment/bettafish-backend backend=bettafish/flask:legacy

# 2. Verify rollback
kubectl rollout status deployment/bettafish-backend
kubectl get pods -l app=bettafish

# 3. Check system health
curl http://bettafish.example.com/health
```

#### 2. Data Recovery
```bash
# 1. Create database backup
pg_dump bettafish > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Restore from backup if needed
psql bettafish < backup_20240101_120000.sql

# 3. Verify data integrity
python scripts/verify_data_integrity.py
```

#### 3. Emergency Communication
```markdown
# Incident Response Template

## System Status Update

**Time**: [Timestamp]
**Issue**: [Brief description]
**Impact**: [Affected users/features]
**Status**: [Investigating/Mitigated/Resolved]

## Actions Taken
1. [Action 1]
2. [Action 2]
3. [Action 3]

## Next Steps
1. [Next step 1]
2. [Next step 2]

## ETA
[Estimated resolution time]

## Updates
[Latest updates will be added here]
```

This comprehensive migration process and troubleshooting guide ensures a smooth transition from Flask to FastAPI with proper error handling, monitoring, and emergency procedures.
# Deployment and Testing Strategy for BettaFish

## Overview

This document outlines the comprehensive deployment and testing strategy for migrating BettaFish from Flask to FastAPI. The strategy ensures a smooth transition with minimal downtime and robust testing at each stage.

## Deployment Architecture

### Environment Strategy

```mermaid
graph TD
    A[Development] --> B[Staging]
    B --> C[Production]
    
    A --> A1[Local Development]
    A --> A2[Development Server]
    
    B --> B1[Staging Environment]
    B --> B2[Performance Testing]
    
    C --> C1[Production Environment]
    C --> C2[Blue-Green Deployment]
    C --> C3[Canary Releases]
```

### Infrastructure Components

#### 1. Container Strategy
```yaml
# docker-compose.yml (Development)
version: '3.8'

services:
  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/bettafish_dev
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=dev-secret-key
      - DEBUG=true
    volumes:
      - ./backend:/app
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Next.js Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

  # PostgreSQL Database
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=bettafish_dev
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/prisma/init.sql:/docker-entrypoint-initdb.d/init.sql

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.dev.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
```

#### 2. Production Docker Configuration
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as base

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3. Kubernetes Deployment
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bettafish-backend
  labels:
    app: bettafish
    component: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bettafish
      component: backend
  template:
    metadata:
      labels:
        app: bettafish
        component: backend
    spec:
      containers:
      - name: backend
        image: bettafish/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: bettafish-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: bettafish-secrets
              key: redis-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: bettafish-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: bettafish-backend-service
spec:
  selector:
    app: bettafish
    component: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: bettafish

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run linting
      run: |
        cd backend
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        black --check .
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=./ --cov-report=xml
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
        JWT_SECRET_KEY: test-secret
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to staging
      run: |
        # Deploy to staging environment
        echo "Deploying to staging..."
        # Add deployment commands here

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        # Deploy to production environment
        echo "Deploying to production..."
        # Add deployment commands here
```

## Testing Strategy

### 1. Unit Testing

#### Backend Unit Tests
```python
# tests/unit/test_auth_service.py
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from backend.services.auth_service import AuthService
from backend.core.exceptions import AuthenticationException

@pytest.fixture
def mock_prisma():
    return Mock()

@pytest.fixture
def auth_service(mock_prisma):
    return AuthService(mock_prisma)

@pytest.fixture
def sample_user():
    return {
        "id": "user123",
        "email": "test@example.com",
        "passwordHash": "hashed_password",
        "isActive": True,
        "role": "user"
    }

class TestAuthService:
    
    @pytest.mark.asyncio
    async def test_authenticate_success(self, auth_service, mock_prisma, sample_user):
        """Test successful authentication"""
        # Arrange
        email = "test@example.com"
        password = "password123"
        
        mock_prisma.user.find_unique.return_value = sample_user
        with patch('backend.services.auth_service.verify_password', return_value=True):
            # Act
            result = await auth_service.authenticate(email, password)
            
            # Assert
            assert result["id"] == sample_user["id"]
            assert result["email"] == sample_user["email"]
            mock_prisma.user.find_unique.assert_called_once_with(
                where={"email": email}
            )
    
    @pytest.mark.asyncio
    async def test_authenticate_invalid_password(self, auth_service, mock_prisma, sample_user):
        """Test authentication with invalid password"""
        # Arrange
        email = "test@example.com"
        password = "wrong_password"
        
        mock_prisma.user.find_unique.return_value = sample_user
        with patch('backend.services.auth_service.verify_password', return_value=False):
            # Act & Assert
            with pytest.raises(AuthenticationException):
                await auth_service.authenticate(email, password)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service, mock_prisma):
        """Test authentication with non-existent user"""
        # Arrange
        email = "nonexistent@example.com"
        password = "password123"
        
        mock_prisma.user.find_unique.return_value = None
        
        # Act & Assert
        with pytest.raises(AuthenticationException):
            await auth_service.authenticate(email, password)
    
    @pytest.mark.asyncio
    async def test_create_access_token(self, auth_service):
        """Test JWT token creation"""
        # Arrange
        user_data = {"id": "user123", "email": "test@example.com"}
        
        # Act
        token = await auth_service.create_access_token(user_data)
        
        # Assert
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.asyncio
    async def test_verify_access_token(self, auth_service):
        """Test JWT token verification"""
        # Arrange
        user_data = {"id": "user123", "email": "test@example.com"}
        token = await auth_service.create_access_token(user_data)
        
        # Act
        payload = await auth_service.verify_access_token(token)
        
        # Assert
        assert payload["sub"] == user_data["id"]
        assert payload["email"] == user_data["email"]
```

#### Frontend Unit Tests
```typescript
// frontend/src/components/__tests__/analysis-dashboard.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { AnalysisDashboard } from '../analysis-dashboard'
import { useRealTimeAnalysis } from '@/hooks/use-real-time-analysis'

// Mock the hook
jest.mock('@/hooks/use-real-time-analysis')
const mockUseRealTimeAnalysis = useRealTimeAnalysis as jest.MockedFunction<typeof useRealTimeAnalysis>

describe('AnalysisDashboard', () => {
  const mockStartAnalysis = jest.fn()
  const mockTasks = new Map()
  
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseRealTimeAnalysis.mockReturnValue({
      tasks: mockTasks,
      connectionStatus: { connected: true, connecting: false },
      startAnalysis: mockStartAnalysis,
      getTask: jest.fn(),
      getAllTasks: jest.fn(() => Array.from(mockTasks.values())),
    })
  })
  
  it('renders dashboard correctly', () => {
    render(<AnalysisDashboard />)
    
    expect(screen.getByText('BettaFish Analysis Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Start New Analysis')).toBeInTheDocument()
    expect(screen.getByText('Connection Status: Connected')).toBeInTheDocument()
  })
  
  it('starts insight analysis when button is clicked', async () => {
    render(<AnalysisDashboard />)
    
    // Fill in query
    const queryInput = screen.getByPlaceholderText('Enter your analysis query...')
    fireEvent.change(queryInput, { target: { value: 'test query' } })
    
    // Switch to insight tab
    const insightTab = screen.getByText('Insight')
    fireEvent.click(insightTab)
    
    // Click start button
    const startButton = screen.getByText('Start Insight Analysis')
    fireEvent.click(startButton)
    
    await waitFor(() => {
      expect(mockStartAnalysis).toHaveBeenCalledWith('insight', 'test query')
    })
  })
  
  it('disables start button when query is empty', () => {
    render(<AnalysisDashboard />)
    
    const startButton = screen.getByText('Start Insight Analysis')
    expect(startButton).toBeDisabled()
  })
})
```

### 2. Integration Testing

#### API Integration Tests
```python
# tests/integration/test_engines_api.py
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from backend.app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_token(async_client):
    """Create authentication token for testing"""
    # Register and login user
    await async_client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "Password123",
        "name": "Test User"
    })
    
    response = await async_client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "Password123"
    })
    
    return response.json()["token"]

class TestEnginesAPI:
    
    @pytest.mark.asyncio
    async def test_start_insight_analysis(self, async_client, auth_token):
        """Test starting insight analysis"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = await async_client.post(
            "/engines/insight/analyze",
            json={"query": "test analysis"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "taskId" in data
        assert data["status"] == "started"
    
    @pytest.mark.asyncio
    async def test_get_insight_status(self, async_client, auth_token):
        """Test getting insight analysis status"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Start analysis first
        start_response = await async_client.post(
            "/engines/insight/analyze",
            json={"query": "test analysis"},
            headers=headers
        )
        task_id = start_response.json()["taskId"]
        
        # Get status
        status_response = await async_client.get(
            f"/engines/insight/status/{task_id}",
            headers=headers
        )
        
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["taskId"] == task_id
        assert "status" in data
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, async_client):
        """Test unauthorized access to engine endpoints"""
        response = await async_client.post(
            "/engines/insight/analyze",
            json={"query": "test analysis"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_invalid_request_data(self, async_client, auth_token):
        """Test validation of request data"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Empty query
        response = await async_client.post(
            "/engines/insight/analyze",
            json={"query": ""},
            headers=headers
        )
        
        assert response.status_code == 422
        
        # Invalid platform
        response = await async_client.post(
            "/engines/insight/analyze",
            json={
                "query": "test",
                "platforms": ["invalid_platform"]
            },
            headers=headers
        )
        
        assert response.status_code == 422
```

### 3. End-to-End Testing

#### Playwright E2E Tests
```typescript
// tests/e2e/analysis-workflow.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Analysis Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login')
    await page.fill('[data-testid="email-input"]', 'test@example.com')
    await page.fill('[data-testid="password-input"]', 'Password123')
    await page.click('[data-testid="login-button"]')
    await expect(page).toHaveURL('/dashboard')
  })
  
  test('complete insight analysis workflow', async ({ page }) => {
    // Navigate to analysis dashboard
    await page.click('[data-testid="analysis-nav"]')
    await expect(page).toHaveURL('/analysis')
    
    // Start insight analysis
    await page.fill('[data-testid="query-input"]', 'public opinion about AI')
    await page.click('[data-testid="insight-tab"]')
    await page.click('[data-testid="start-insight-button"]')
    
    // Verify analysis started
    await expect(page.locator('[data-testid="analysis-status"]')).toContainText('running')
    
    // Wait for completion (mock in test environment)
    await page.waitForTimeout(2000)
    
    // Verify results displayed
    await expect(page.locator('[data-testid="analysis-results"]')).toBeVisible()
  })
  
  test('real-time updates during analysis', async ({ page }) => {
    // Start analysis
    await page.fill('[data-testid="query-input"]', 'test query')
    await page.click('[data-testid="media-tab"]')
    await page.click('[data-testid="start-media-button"]')
    
    // Verify real-time log updates
    await expect(page.locator('[data-testid="log-messages"]')).toBeVisible()
    
    // Check for connection status
    await expect(page.locator('[data-testid="connection-status"]')).toContainText('Connected')
  })
  
  test('report generation workflow', async ({ page }) => {
    // Complete multiple analyses first
    await page.fill('[data-testid="query-input"]', 'test query')
    await page.click('[data-testid="start-insight-button"]')
    await page.waitForTimeout(1000)
    
    await page.fill('[data-testid="query-input"]', 'another query')
    await page.click('[data-testid="start-media-button"]')
    await page.waitForTimeout(1000)
    
    // Generate report
    await page.click('[data-testid="generate-report-button"]')
    await page.selectOption('[data-testid="report-template"]', 'executive_summary')
    await page.click('[data-testid="confirm-report-button"]')
    
    // Verify report generation
    await expect(page.locator('[data-testid="report-status"]')).toContainText('generating')
    
    // Wait for completion
    await page.waitForTimeout(3000)
    
    // Verify report available
    await expect(page.locator('[data-testid="download-report-button"]')).toBeVisible()
  })
})
```

### 4. Performance Testing

#### Load Testing with Locust
```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import json
import random

class BettaFishUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login on start"""
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "Password123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(3)
    def start_insight_analysis(self):
        """Start insight analysis"""
        if not self.token:
            return
        
        queries = [
            "public opinion about climate change",
            "social media trends in technology",
            "customer sentiment analysis",
            "market research for new product"
        ]
        
        query = random.choice(queries)
        
        response = self.client.post(
            "/engines/insight/analyze",
            json={"query": query},
            headers=self.headers
        )
        
        if response.status_code == 200:
            task_id = response.json()["taskId"]
            # Check status
            self.client.get(
                f"/engines/insight/status/{task_id}",
                headers=self.headers
            )
    
    @task(2)
    def start_media_analysis(self):
        """Start media analysis"""
        if not self.token:
            return
        
        queries = [
            "viral marketing campaigns",
            "brand reputation monitoring",
            "content performance analysis"
        ]
        
        query = random.choice(queries)
        
        response = self.client.post(
            "/engines/media/analyze",
            json={"query": query},
            headers=self.headers
        )
    
    @task(1)
    def get_user_profile(self):
        """Get user profile"""
        if not self.token:
            return
        
        self.client.get("/auth/me", headers=self.headers)
    
    @task(1)
    def get_analysis_history(self):
        """Get analysis history"""
        if not self.token:
            return
        
        self.client.get("/engines/history", headers=self.headers)
```

## Deployment Strategy

### 1. Blue-Green Deployment

```mermaid
graph TD
    A[Load Balancer] --> B[Blue Environment]
    A --> C[Green Environment]
    
    B --> B1[Current Version]
    C --> C2[New Version]
    
    D[Database] --> B
    D --> C
    
    E[Smoke Tests] --> C
    F[Health Checks] --> C
    
    G[Traffic Switch] --> A
```

### 2. Canary Deployment

```yaml
# k8s/canary-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: bettafish-backend-rollout
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 10m}
      - setWeight: 40
      - pause: {duration: 10m}
      - setWeight: 60
      - pause: {duration: 10m}
      - setWeight: 80
      - pause: {duration: 10m}
      canaryService: bettafish-backend-canary
      stableService: bettafish-backend-stable
      trafficRouting:
        istio:
          virtualService:
            name: bettafish-backend-vsvc
            routes:
            - primary
  selector:
    matchLabels:
      app: bettafish
      component: backend
  template:
    metadata:
      labels:
        app: bettafish
        component: backend
    spec:
      containers:
      - name: backend
        image: bettafish/backend:latest
        ports:
        - containerPort: 8000
```

### 3. Monitoring and Alerting

```yaml
# monitoring/prometheus-config.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'bettafish-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'bettafish-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/api/metrics'
    scrape_interval: 5s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

```yaml
# monitoring/alert_rules.yml
groups:
  - name: bettafish-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }} seconds"
      
      - alert: DatabaseConnectionFailure
        expr: up{job="bettafish-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failure"
          description: "Backend service is down or cannot connect to database"
```

## Rollback Strategy

### 1. Automated Rollback

```yaml
# .github/workflows/rollback.yml
name: Rollback Deployment

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to rollback'
        required: true
        default: 'production'
      version:
        description: 'Version to rollback to'
        required: true

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Rollback deployment
      run: |
        # Get previous stable version
        VERSION=${{ github.event.inputs.version }}
        
        # Rollback Kubernetes deployment
        kubectl set image deployment/bettafish-backend backend=bettafish/backend:$VERSION
        
        # Wait for rollout
        kubectl rollout status deployment/bettafish-backend
        
        # Verify rollback
        kubectl get pods -l app=bettafish,component=backend
```

### 2. Manual Rollback Procedures

1. **Identify Issue**
   - Monitor error rates and response times
   - Check user feedback and support tickets
   - Review deployment logs

2. **Assess Impact**
   - Determine affected users and features
   - Estimate business impact
   - Decide on rollback scope

3. **Execute Rollback**
   - Switch traffic to previous version
   - Verify system stability
   - Communicate with stakeholders

4. **Post-Rollback**
   - Investigate root cause
   - Fix issues in new version
   - Plan redeployment

This comprehensive deployment and testing strategy ensures a reliable migration process with minimal risk and maximum system stability.
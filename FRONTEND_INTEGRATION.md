# Frontend Integration Guide

This document explains how the Next.js frontend has been integrated with the FastAPI backend for the BettaFish multi-agent public opinion analysis system.

## Overview

The frontend integration includes:

1. **Authentication System**: JWT-based authentication with token refresh
2. **API Client**: Axios-based HTTP client with interceptors
3. **WebSocket Client**: Real-time communication with backend
4. **Engine Management**: Interface to control and monitor analysis engines
5. **Responsive UI**: Modern dashboard with real-time updates

## Architecture

### Client-Side Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Next.js Frontend                    │
├─────────────────────────────────────────────────────────────┤
│  Components                                        │
│  ├── AuthProvider (authentication context)             │
│  ├── useEngines Hook (engine management)             │
│  ├── useWebSocket Hook (real-time communication)      │
│  └── API Client (HTTP requests)                   │
├─────────────────────────────────────────────────────────────┤
│  Services                                         │
│  ├── Authentication Service                          │
│  ├── Engine Service                                 │
│  ├── WebSocket Service                               │
│  └── API Client                                   │
├─────────────────────────────────────────────────────────────┤
│  Communication                                    │
│  ├── HTTP REST APIs                                │
│  ├── WebSocket (Socket.IO)                          │
│  └── JWT Authentication                            │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                      │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Authentication System

**Location**: `frontend/src/contexts/auth-context.tsx`

The authentication system provides:
- User login/logout functionality
- JWT token management
- Automatic token refresh
- Protected route handling

**Usage**:
```typescript
import { useAuth } from '@/contexts/auth-context';

const { user, isAuthenticated, login, logout } = useAuth();
```

### 2. API Client

**Location**: `frontend/src/lib/api/client.ts`

Features:
- Axios-based HTTP client
- Request/response interceptors
- Automatic token injection
- Error handling
- Token refresh logic

**Usage**:
```typescript
import { api } from '@/lib/api/client';

const response = await api.get('/api/engines/status');
```

### 3. WebSocket Client

**Location**: `frontend/src/lib/websocket/client.ts`

Features:
- Socket.IO integration
- Automatic reconnection
- Room-based communication
- Real-time event handling

**Usage**:
```typescript
import { useWebSocket } from '@/lib/websocket/client';

const { connect, joinAnalysisRoom, on } = useWebSocket();
```

### 4. Engine Management Hook

**Location**: `frontend/src/hooks/use-engines.ts`

Features:
- Engine status monitoring
- Analysis management
- Progress tracking
- WebSocket integration

**Usage**:
```typescript
import { useEngines } from '@/hooks/use-engines';

const { 
  engines, 
  startAnalysis, 
  stopAnalysis, 
  progress 
} = useEngines();
```

## API Integration

### Authentication Endpoints

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/me` - Get current user

### Engine Endpoints

- `GET /api/engines/status` - Get all engine statuses
- `POST /api/engines/analyze` - Start analysis
- `POST /api/engines/analysis/{id}/stop` - Stop analysis
- `GET /api/engines/analysis/{id}/results` - Get analysis results

### WebSocket Events

- `engine_progress` - Engine progress updates
- `engine_status` - Engine status changes
- `analysis_complete` - Analysis completion
- `notification` - System notifications

## Environment Configuration

### Frontend Environment Variables

**File**: `frontend/.env.local`

```bash
# FastAPI Backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# WebSocket URL
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Database URL
DATABASE_URL="postgresql://postgres:password@localhost:5432/bettafish"
```

### Backend Environment Variables

**File**: `.env`

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/bettafish
REDIS_URL=redis://redis:6379

# Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
OPENAI_API_KEY=your-openai-key
TAVILY_API_KEY=your-tavily-key
BOCHA_API_KEY=your-bocha-key
```

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Node.js 18+
- Python 3.9+

### Quick Start

You have two options for development: Docker-based or no-Docker setup.

#### Option 1: Docker Setup (Recommended for beginners)

1. **Clone and Setup**:
   ```bash
   git clone <repository>
   cd BettaFish
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   cp frontend/.env.local.example frontend/.env.local
   # Edit both files with your API keys
   ```

3. **Start Development Environment**:
   ```bash
   ./scripts/dev-start.sh
   ```

4. **Access Applications**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

#### Option 2: No-Docker Setup (For advanced users)

1. **Install Prerequisites**:
   - PostgreSQL 13+ running on localhost:5432
   - Redis 6+ running on localhost:6379
   - Python 3.9+
   - Node.js 18+

2. **Clone and Setup**:
   ```bash
   git clone <repository>
   cd BettaFish
   ```

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   cp frontend/.env.local.example frontend/.env.local
   # Edit both files with your API keys and local database settings
   ```

4. **Start Development Environment**:
   ```bash
   ./scripts/dev-start-no-docker.sh
   ```

5. **Access Applications**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

6. **Stop Development Environment**:
   ```bash
   ./scripts/dev-stop.sh
   ```

For detailed no-Docker setup instructions, see [NO_DOCKER_DEVELOPMENT.md](NO_DOCKER_DEVELOPMENT.md).

### Manual Development Setup

If you prefer to run services manually:

1. **Start Database**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d postgres redis
   ```

2. **Initialize Database**:
   ```bash
   cd backend
   python scripts/init_db.py
   cd ..
   ```

3. **Start Backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Features

### Real-Time Dashboard

- Live engine status monitoring
- Real-time progress tracking
- Interactive charts and visualizations
- Responsive design for all devices

### Analysis Management

- Start/stop analyses
- Monitor progress across engines
- View historical analyses
- Download reports in multiple formats

### User Management

- Secure authentication
- User profile management
- Session persistence
- Automatic logout on token expiration

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Ensure `NEXT_PUBLIC_API_URL` is correctly set
   - Check backend CORS configuration

2. **WebSocket Connection Issues**:
   - Verify `NEXT_PUBLIC_WS_URL` is accessible
   - Check firewall settings

3. **Authentication Issues**:
   - Clear browser localStorage
   - Verify JWT secret configuration
   - Check token expiration settings

4. **Database Connection Issues**:
   - Ensure PostgreSQL is running
   - Verify connection string
   - Check database credentials

### Debug Mode

Enable debug logging by setting:
```bash
NODE_ENV=development
LOG_LEVEL=debug
```

## Production Deployment

### Docker Deployment

1. **Build Images**:
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

2. **Start Services**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Environment Variables

Production requires additional security settings:
- Strong JWT secrets
- HTTPS URLs
- Database SSL configuration
- API rate limiting

## Testing

### Frontend Tests

```bash
cd frontend
npm run test
npm run test:coverage
```

### Integration Tests

```bash
npm run test:e2e
```

## Contributing

When contributing to the frontend:

1. Follow TypeScript strict mode
2. Use proper component structure
3. Maintain responsive design
4. Test with different screen sizes
5. Update documentation for new features

## Future Enhancements

- PWA support for mobile devices
- Offline mode capabilities
- Advanced filtering and search
- Custom dashboard widgets
- Multi-language support
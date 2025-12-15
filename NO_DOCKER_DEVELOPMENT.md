# No-Docker Development Guide

This guide explains how to set up and run the BettaFish development environment without using Docker containers.

## Overview

The no-Docker setup allows you to run BettaFish directly on your host machine, which can be beneficial for:
- Faster development iteration
- Direct access to logs and processes
- Easier debugging
- Reduced resource usage
- Custom development environment

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows (with WSL2)
- **Python**: 3.9 or higher
- **Node.js**: 18 or higher
- **PostgreSQL**: 13 or higher
- **Redis**: 6 or higher

### Required Tools

- **Python Package Manager**: pip
- **Node.js Package Manager**: npm
- **Database Tools**: psql (PostgreSQL client)
- **Process Management**: ps, kill, nohup
- **Rust Compiler**: Required for tiktoken package (automatically installed by setup script)

## Installation Guide

### 1. Install PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Windows
Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Install Redis

#### Ubuntu/Debian
```bash
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS
```bash
brew install redis
brew services start redis
```

#### Windows
Download and install Redis from [redis.io](https://redis.io/download)

### 3. Setup Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE bettafish;
CREATE USER bettafish WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bettafish TO bettafish;
\q
```

### 4. Install Python Dependencies

```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Install Node.js Dependencies

```bash
cd frontend
npm install
```

## Configuration

### Backend Configuration

Create `.env` file in root directory:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Database
DATABASE_URL=postgresql://bettafish:your_password@localhost:5432/bettafish

# Redis
REDIS_URL=redis://localhost:6379

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
OPENAI_API_KEY=your-openai-key
TAVILY_API_KEY=your-tavily-key
BOCHA_API_KEY=your-bocha-key
ANSPIRE_API_KEY=your-anspire-key
DEEPSEEK_API_KEY=your-deepseek-key
MOONSHOT_API_KEY=your-moonshot-key
```

### Frontend Configuration

Create `frontend/.env.local` file:

```bash
cp frontend/.env.local.example frontend/.env.local
```

Edit `frontend/.env.local`:

```bash
# Backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# WebSocket URL
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Database (if using Prisma client)
DATABASE_URL="postgresql://bettafish:your_password@localhost:5432/bettafish"
```

## Running the Application

### Quick Start

Use the provided script for easy startup:

```bash
./scripts/dev-start-no-docker.sh
```

### Verify Setup

After running the setup script, you can verify everything is working correctly:

```bash
# Run the test script to check all components
./scripts/test-no-docker-setup.sh
```

This test script will verify:
- All prerequisites are installed
- Configuration files exist
- Dependencies are properly installed
- Services are running correctly
- Database connection is working

### Manual Start

If you prefer to start services manually:

#### 1. Initialize Database

```bash
cd backend
source venv/bin/activate
python scripts/init_db.py init
cd ..
```

The initialization script will:
- Generate Prisma client
- Run database migrations
- Create default admin user (admin@bettafish.com / admin123)
- Create basic system settings

#### 2. Seed Database with Sample Data

```bash
cd backend
source venv/bin/activate
python scripts/init_db.py seed
cd ..
```

The seeding script will:
- Create sample users for testing
- Create sample analysis tasks
- Create sample agent outputs
- Create sample reports

#### 2. Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Start Frontend

```bash
cd frontend
npm run dev
```

## Development Workflow

### Running Services

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432
- **Redis**: localhost:6379

### Monitoring

#### View Logs

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log
```

#### Check Processes

```bash
# Check running processes
ps aux | grep -E "(uvicorn|next)"

# Check specific process
ps aux | grep uvicorn  # Backend
ps aux | grep next     # Frontend
```

#### Database Access

```bash
# Connect to database
psql -h localhost -p 5432 -U bettafish -d bettafish

# Check database status
sudo -u postgres pg_isready
```

### Stopping Services

Use the provided stop script:

```bash
./scripts/dev-stop.sh
```

Or manually stop:

```bash
# Stop backend
pkill -f "uvicorn app.main:app"

# Stop frontend
pkill -f "next dev"
```

## Troubleshooting

### Common Issues

#### Port Conflicts

If ports 3000 or 8000 are in use:

```bash
# Check what's using the ports
lsof -i :3000
lsof -i :8000

# Kill the processes
kill -9 <PID>
```

#### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check if database exists
sudo -u postgres psql -l

# Test connection
psql -h localhost -p 5432 -U bettafish -d bettafish
```

#### Permission Issues

```bash
# Fix file permissions
chmod +x scripts/*.sh

# Fix virtual environment permissions
chmod -R 755 backend/venv/
```

#### Dependency Issues

```bash
# Reinstall Python dependencies
cd backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Reinstall Node.js dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Tiktoken Installation Error

**Error**: `ERROR: Could not build wheels for tiktoken, which is required to install pyproject.toml-based projects`

**Solution**: The development script automatically installs Rust compiler, but if you encounter this issue:

```bash
# Install Rust manually
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# Then retry installation
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Performance Issues

#### Backend Performance

```bash
# Check system resources
htop
iostat -x 1

# Optimize PostgreSQL
sudo -u postgres psql -d bettafish -c "ALTER SYSTEM SET shared_buffers = '256MB';"
```

#### Frontend Performance

```bash
# Check Node.js memory usage
ps aux | grep next

# Increase Node.js memory limit
cd frontend
export NODE_OPTIONS="--max-old-space-size-size=4096"
npm run dev
```

## Development Tips

### Code Quality

```bash
# Python linting
cd backend
flake8 .
black .

# TypeScript checking
cd frontend
npm run lint
npm run type-check
```

### Database Management

```bash
# Reset database
cd backend
source venv/bin/activate
python scripts/init_db.py --reset

# Create migrations
python scripts/init_db.py --migrate-only
```

### API Testing

```bash
# Test backend endpoints
curl http://localhost:8000/health

# Test WebSocket connection
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: SGVsbG8ub3Vyc3RlcFhZGxpY2E=" \
     -H "Sec-WebSocket-Version: 13" \
     http://localhost:8000/ws
```

## IDE Configuration

### VS Code

Recommended extensions:
- Python
- TypeScript and JavaScript Language Features
- Prisma
- Docker (if you switch back to Docker)
- GitLens
- Thunder Client (for API testing)

### PyCharm

Recommended plugins:
- Database Navigator
- .env files support
- GitToolBox
- Key Promoter X

## Production Considerations

When moving to production:

1. **Use Process Managers**:
   - Backend: PM2 or Supervisor
   - Frontend: PM2 or systemd

2. **Configure Reverse Proxy**:
   - Nginx or Apache for SSL termination
   - Load balancing for multiple instances

3. **Environment Variables**:
   - Use production secrets management
   - Enable all security features
   - Configure proper CORS origins

4. **Database Optimization**:
   - Configure connection pooling
   - Set appropriate memory limits
   - Enable query logging

## Migration to Docker

If you later decide to switch to Docker:

1. **Export Database**:
   ```bash
   pg_dump -h localhost -p 5432 -U bettafish bettafish > bettafish.sql
   ```

2. **Import to Docker**:
   ```bash
   docker exec -i bettafish-postgres psql -U postgres -d bettafish < bettafish.sql
   ```

3. **Use Docker Scripts**:
   ```bash
   ./scripts/dev-start.sh
   ```

## Support

For issues with no-Docker setup:

1. Check logs in `logs/` directory
2. Verify all prerequisites are installed
3. Ensure ports 3000, 8000, 5432, and 6379 are available
4. Test database connection manually
5. Check environment variable configuration

For additional help, refer to the main documentation or create an issue in the project repository.
#!/bin/bash

# BettaFish Development Start Script (No Docker)
# This script starts the entire BettaFish development environment without Docker

set -e

echo "🐠 Starting BettaFish Development Environment (No Docker)..."

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 -U postgres 2>/dev/null; then
    echo "❌ PostgreSQL is not running on localhost:5432. Please start PostgreSQL first."
    echo "💡 You can start PostgreSQL with: pg_ctl -D /usr/local/var/postgresql/data start"
    exit 1
fi

# Check if Redis is running
if ! redis-cli ping 2>/dev/null; then
    echo "❌ Redis is not running on localhost:6379. Please start Redis first."
    echo "💡 You can start Redis with: redis-server"
    exit 1
fi

# Create necessary directories if they don't exist
mkdir -p logs
mkdir -p reports

# Check if .env file exists, create from example if not
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before running the system again."
    echo "🔑 Required settings:"
    echo "   - DATABASE_URL (should be: postgresql://postgres:password@localhost:5432/bettafish)"
    echo "   - REDIS_URL (should be: redis://localhost:6379)"
    echo "   - All API keys (OpenAI, Tavily, etc.)"
    exit 0
fi

# Check if frontend .env.local exists, create from example if not
if [ ! -f frontend/.env.local ]; then
    echo "📝 Creating frontend/.env.local file from example..."
    cp frontend/.env.local.example frontend/.env.local
    echo "⚠️  Please edit frontend/.env.local with your API URL"
    echo "🔧 Required settings:"
    echo "   - NEXT_PUBLIC_API_URL (should be: http://localhost:8065)"
    echo "   - NEXT_PUBLIC_WS_URL (should be: ws://localhost:8065)"
fi

# Install Python dependencies if needed
if [ ! -d "backend/venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    cd backend
    python -m venv venv
    cd ..
fi

echo "📦 Installing Python dependencies..."
cd backend
source venv/bin/activate

# First install Rust compiler for tiktoken
echo "🔧 Installing Rust compiler for tiktoken..."
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Install Node.js dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo "🗄️ Initializing database..."
cd backend && source venv/bin/activate
python scripts/simple_init_db.py init
cd ..

echo "🚀 Starting FastAPI backend..."
cd backend && source venv/bin/activate
# Start backend in background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8065 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Check if backend started successfully
if ! curl -s http://localhost:8065/health > /dev/null; then
    echo "❌ Backend failed to start. Check logs/backend.log for details."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "🎨 Starting Next.js frontend..."
cd frontend
# Start frontend in background with port 3065
nohup npm run dev -- --port 3065 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
sleep 15

# Check if frontend started successfully
if ! curl -s http://localhost:3065 > /dev/null; then
    echo "❌ Frontend failed to start. Check logs/frontend.log for details."
    kill $FRONTEND_PID 2>/dev/null
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "✅ BettaFish Development Environment is starting up!"
echo ""
echo "🌐 Frontend: http://localhost:3065"
echo "🔧 Backend API: http://localhost:8065"
echo "📊 API Docs: http://localhost:8065/docs"
echo "🗄️ Database: postgresql://postgres:password@localhost:5432/bettafish"
echo ""
echo "🐠 Default login credentials:"
echo "   Email: admin@bettafish.com"
echo "   Password: admin123"
echo ""
echo "📋 Useful commands:"
echo "   View backend logs: tail -f logs/backend.log"
echo "   View frontend logs: tail -f logs/frontend.log"
echo "   Stop all: kill $BACKEND_PID $FRONTEND_PID"
echo "   Stop backend: kill $BACKEND_PID"
echo "   Stop frontend: kill $FRONTEND_PID"
echo ""
echo "🔍 To monitor the system:"
echo "   Backend logs: tail -f logs/backend.log"
echo "   Frontend logs: tail -f logs/frontend.log"
echo "   Process status: ps aux | grep -E '(uvicorn|next)'"
echo ""
echo "💡 To stop the development environment:"
echo "   ./scripts/dev-stop.sh"
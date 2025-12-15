#!/bin/bash

# BettaFish Development Start Script
# This script starts the entire BettaFish development environment

set -e

echo "🐠 Starting BettaFish Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Create necessary directories if they don't exist
mkdir -p logs
mkdir -p reports
mkdir -p postgres_data

# Check if .env file exists, create from example if not
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before running the system again."
    exit 0
fi

# Check if frontend .env.local exists, create from example if not
if [ ! -f frontend/.env.local ]; then
    echo "📝 Creating frontend/.env.local file from example..."
    cp frontend/.env.local.example frontend/.env.local
fi

echo "🐳 Starting PostgreSQL and Redis..."
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🗄️ Running database migrations..."
cd backend
python scripts/init_db.py
cd ..

echo "🚀 Starting FastAPI backend..."
docker-compose -f docker-compose.dev.yml up -d backend

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 15

echo "🎨 Starting Next.js frontend..."
docker-compose -f docker-compose.dev.yml up -d frontend

echo ""
echo "✅ BettaFish Development Environment is starting up!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo "🗄️ Database: postgresql://postgres:password@localhost:5432/bettafish"
echo ""
echo "🐠 Default login credentials:"
echo "   Email: admin@bettafish.com"
echo "   Password: admin123"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.dev.yml logs -f [service]"
echo "   Stop all: docker-compose -f docker-compose.dev.yml down"
echo "   Restart service: docker-compose -f docker-compose.dev.yml restart [service]"
echo ""
echo "🔍 To monitor the system:"
echo "   Frontend logs: docker-compose -f docker-compose.dev.yml logs -f frontend"
echo "   Backend logs: docker-compose -f docker-compose.dev.yml logs -f backend"
echo "   Database logs: docker-compose -f docker-compose.dev.yml logs -f postgres"
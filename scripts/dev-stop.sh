#!/bin/bash

# BettaFish Development Stop Script
# This script stops the BettaFish development environment (both Docker and non-Docker)

set -e

echo "🛑 Stopping BettaFish Development Environment..."

# Stop Docker services if running
if docker-compose -f docker-compose.dev.yml ps -q | grep -q "Up"; then
    echo "🐳 Stopping Docker services..."
    docker-compose -f docker-compose.dev.yml down
fi

# Stop non-Docker services if running
if [ -f logs/backend.pid ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "🔧 Stopping FastAPI backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm logs/backend.pid
    fi
fi

if [ -f logs/frontend.pid ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "🎨 Stopping Next.js frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm logs/frontend.pid
    fi
fi

# Clean up any remaining processes
echo "🧹 Cleaning up remaining processes..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true
pkill -f "node.*next" 2>/dev/null || true

echo "✅ BettaFish Development Environment stopped successfully!"
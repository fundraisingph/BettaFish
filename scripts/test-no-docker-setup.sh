#!/bin/bash

# Test script for no-Docker development setup
# This script verifies that all components are properly configured

echo "🧪 Testing BettaFish No-Docker Development Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_step() {
    local step_name=$1
    local command=$2
    local expected_result=$3
    
    echo -n "Testing $step_name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo -e "  ${YELLOW}Command: $command${NC}"
        return 1
    fi
}

# Check prerequisites
echo "📋 Checking prerequisites..."

test_step "Python 3.9+" "python3 --version | grep -E 'Python 3\.[9-9]|Python 3\.[1-9][0-9]|Python 4\.[0-9]'"
test_step "Node.js 18+" "node --version | grep -E 'v1[8-9]\.|v[2-9][0-9]\.'"
test_step "PostgreSQL" "pg_isready -h localhost -p 5432"
test_step "Redis" "redis-cli ping"
test_step "Rust Compiler" "rustc --version"

# Check directories and files
echo ""
echo "📁 Checking directories and files..."

test_step "Backend directory exists" "test -d backend"
test_step "Frontend directory exists" "test -d frontend"
test_step "Backend requirements.txt exists" "test -f backend/requirements.txt"
test_step "Frontend package.json exists" "test -f frontend/package.json"
test_step "No-Docker script exists" "test -f scripts/dev-start-no-docker.sh"
test_step "Stop script exists" "test -f scripts/dev-stop.sh"

# Check configuration files
echo ""
echo "⚙️ Checking configuration files..."

test_step ".env.example exists" "test -f .env.example"
test_step "Frontend .env.local.example exists" "test -f frontend/.env.local.example"

# Check if virtual environment exists
if [ -d "backend/venv" ]; then
    echo -e "Virtual environment exists... ${GREEN}✓ PASS${NC}"
    
    # Check if key packages are installed
    echo ""
    echo "📦 Checking Python packages..."
    
    source backend/venv/bin/activate
    
    test_step "FastAPI installed" "pip show fastapi > /dev/null"
    test_step "Uvicorn installed" "pip show uvicorn > /dev/null"
    test_step "Prisma installed" "pip show prisma > /dev/null"
    test_step "OpenAI installed" "pip show openai > /dev/null"
    test_step "Tiktoken installed" "pip show tiktoken > /dev/null"
    
    deactivate
else
    echo -e "Virtual environment exists... ${YELLOW}⚠ SKIP (run ./scripts/dev-start-no-docker.sh first)${NC}"
fi

# Check if node_modules exists
if [ -d "frontend/node_modules" ]; then
    echo ""
    echo "📦 Checking Node.js packages..."
    
    test_step "Next.js installed" "test -d frontend/node_modules/next"
    test_step "React installed" "test -d frontend/node_modules/react"
    test_step "TypeScript installed" "test -f frontend/node_modules/.bin/tsc"
else
    echo -e "Node.js modules exist... ${YELLOW}⚠ SKIP (run ./scripts/dev-start-no-docker.sh first)${NC}"
fi

# Check if services are running
echo ""
echo "🚀 Checking services..."

test_step "Backend running" "curl -s http://localhost:8000/health > /dev/null"
test_step "Frontend running" "curl -s http://localhost:3000 > /dev/null"

# Check database
echo ""
echo "🗄️ Checking database..."

test_step "Database exists" "psql -h localhost -p 5432 -U bettafish -d bettafish -c 'SELECT 1' > /dev/null 2>&1"

# Check if database is properly seeded
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
    
    # Check if admin user exists
    ADMIN_EXISTS=$(python -c "
import asyncio
import sys
sys.path.append('backend')
from core.database import get_db_connection

async def check_admin():
    conn = await get_db_connection()
    result = await conn.fetchrow('SELECT id FROM users WHERE email = \$1', 'admin@bettafish.com')
    await conn.close()
    return result is not None

result = asyncio.run(check_admin())
print('YES' if result else 'NO')
")
    
    if [ "$ADMIN_EXISTS" = "YES" ]; then
        echo -e "Database admin user... ${GREEN}✓ PASS${NC}"
    else
        echo -e "Database admin user... ${RED}✗ FAIL${NC}"
    fi
    
    # Check if sample data exists
    SAMPLE_DATA_EXISTS=$(python -c "
import asyncio
import sys
sys.path.append('backend')
from core.database import get_db_connection

async def check_sample_data():
    conn = await get_db_connection()
    result = await conn.fetchrow('SELECT COUNT(*) as count FROM analysis_tasks WHERE title = \$1', 'Sample Public Opinion Analysis')
    await conn.close()
    return result['count'] > 0 if result else 0

result = asyncio.run(check_sample_data())
print('YES' if result > 0 else 'NO')
")
    
    if [ "$SAMPLE_DATA_EXISTS" = "YES" ]; then
        echo -e "Database sample data... ${GREEN}✓ PASS${NC}"
    else
        echo -e "Database sample data... ${RED}✗ FAIL${NC}"
    fi
    
    deactivate
else
    echo -e "Database seeding... ${YELLOW}⚠ SKIP (run ./scripts/dev-start-no-docker.sh first)${NC}"
fi

# Summary
echo ""
echo "📊 Test Summary:"
echo "If any tests failed, please check the troubleshooting section in NO_DOCKER_DEVELOPMENT.md"
echo "or run the setup script again: ./scripts/dev-start-no-docker.sh"

echo ""
echo "🎉 No-Docker setup test completed!"
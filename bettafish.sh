#!/bin/bash

# BettaFish Service Management Script
# This script manages the BettaFish backend and frontend services

# Configuration
BACKEND_PORT=8065
FRONTEND_PORT=3065
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
LOGS_DIR="logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if a service is running on a specific port
is_service_running() {
    local port=$1
    local service_name=$2
    
    # Check if port is in use by any process
    if lsof -i:$port > /dev/null 2>&1 || netstat -tulpn 2>/dev/null | grep -q ":$port "; then
        return 0  # Service is running
    else
        return 1  # Service is not running
    fi
}

# Function to get process ID for a service
get_service_pid() {
    local port=$1
    lsof -ti:$port 2>/dev/null | head -1
}

# Function to stop services
stop_services() {
    print_header "Stopping BettaFish Services"
    
    # Stop backend service
    if is_service_running $BACKEND_PORT "Backend"; then
        backend_pid=$(get_service_pid $BACKEND_PORT)
        print_status "Stopping backend service (PID: $backend_pid) on port $BACKEND_PORT..."
        kill -TERM $backend_pid 2>/dev/null
        
        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! is_service_running $BACKEND_PORT "Backend"; then
                print_status "Backend service stopped successfully"
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if is_service_running $BACKEND_PORT "Backend"; then
            print_warning "Force killing backend service..."
            kill -KILL $backend_pid 2>/dev/null
        fi
    else
        print_warning "Backend service is not running on port $BACKEND_PORT"
    fi
    
    # Stop frontend service
    if is_service_running $FRONTEND_PORT "Frontend"; then
        frontend_pid=$(get_service_pid $FRONTEND_PORT)
        print_status "Stopping frontend service (PID: $frontend_pid) on port $FRONTEND_PORT..."
        kill -TERM $frontend_pid 2>/dev/null
        
        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! is_service_running $FRONTEND_PORT "Frontend"; then
                print_status "Frontend service stopped successfully"
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if is_service_running $FRONTEND_PORT "Frontend"; then
            print_warning "Force killing frontend service..."
            kill -KILL $frontend_pid 2>/dev/null
        fi
    else
        print_warning "Frontend service is not running on port $FRONTEND_PORT"
    fi
    
    print_status "All services stopped"
}

# Function to start services
start_services() {
    print_header "Starting BettaFish Services"
    
    # Create logs directory if it doesn't exist
    mkdir -p $LOGS_DIR
    
    # Check if services are already running
    if is_service_running $BACKEND_PORT "Backend"; then
        print_warning "Backend service is already running on port $BACKEND_PORT"
        print_warning "Please stop the service first or use 'restart' command"
        return 1
    fi
    
    if is_service_running $FRONTEND_PORT "Frontend"; then
        print_warning "Frontend service is already running on port $FRONTEND_PORT"
        print_warning "Please stop the service first or use 'restart' command"
        return 1
    fi
    
    # Start backend service
    print_status "Starting backend service on port $BACKEND_PORT..."
    cd $BACKEND_DIR
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > ../$LOGS_DIR/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    for i in {1..30}; do
        if is_service_running $BACKEND_PORT "Backend"; then
            print_status "Backend service started successfully (PID: $BACKEND_PID)"
            break
        fi
        sleep 1
    done
    
    if ! is_service_running $BACKEND_PORT "Backend"; then
        print_error "Backend service failed to start. Check logs: $LOGS_DIR/backend.log"
        return 1
    fi
    
    # Start frontend service
    print_status "Starting frontend service on port $FRONTEND_PORT..."
    cd $FRONTEND_DIR
    nohup npm run dev > ../$LOGS_DIR/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    print_status "Waiting for frontend to start..."
    for i in {1..30}; do
        if is_service_running $FRONTEND_PORT "Frontend"; then
            print_status "Frontend service started successfully (PID: $FRONTEND_PID)"
            break
        fi
        sleep 1
    done
    
    if ! is_service_running $FRONTEND_PORT "Frontend"; then
        print_error "Frontend service failed to start. Check logs: $LOGS_DIR/frontend.log"
        return 1
    fi
    
    print_status "All services started successfully"
    print_status "Frontend: http://localhost:$FRONTEND_PORT"
    print_status "Backend API: http://localhost:$BACKEND_PORT"
    print_status "API Docs: http://localhost:$BACKEND_PORT/docs"
}

# Function to restart services
restart_services() {
    print_header "Restarting BettaFish Services"
    stop_services
    sleep 2
    start_services
}

# Function to show service status
show_status() {
    print_header "BettaFish Service Status"
    
    # Check backend status
    if is_service_running $BACKEND_PORT "Backend"; then
        backend_pid=$(get_service_pid $BACKEND_PORT)
        print_status "Backend: RUNNING (PID: $backend_pid) on port $BACKEND_PORT"
        
        # Check if backend is responding
        if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            print_status "Backend Health: HEALTHY"
        else
            print_warning "Backend Health: NOT RESPONDING"
        fi
    else
        print_error "Backend: NOT RUNNING on port $BACKEND_PORT"
    fi
    
    # Check frontend status
    if is_service_running $FRONTEND_PORT "Frontend"; then
        frontend_pid=$(get_service_pid $FRONTEND_PORT)
        print_status "Frontend: RUNNING (PID: $frontend_pid) on port $FRONTEND_PORT"
        
        # Check if frontend is responding
        if curl -s -I http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            print_status "Frontend Health: RESPONDING"
        else
            print_warning "Frontend Health: NOT RESPONDING"
        fi
    else
        print_error "Frontend: NOT RUNNING on port $FRONTEND_PORT"
    fi
}

# Function to show logs
show_logs() {
    local service=$1
    local lines=${2:-50}
    
    case $service in
        "backend"|"b")
            print_header "Backend Logs (Last $lines lines)"
            tail -n $lines $LOGS_DIR/backend.log 2>/dev/null || print_error "Backend log file not found"
            ;;
        "frontend"|"f")
            print_header "Frontend Logs (Last $lines lines)"
            tail -n $lines $LOGS_DIR/frontend.log 2>/dev/null || print_error "Frontend log file not found"
            ;;
        "all"|"a")
            print_header "All Logs"
            echo -e "${BLUE}=== Backend Logs ===${NC}"
            tail -n $lines $LOGS_DIR/backend.log 2>/dev/null || print_error "Backend log file not found"
            echo
            echo -e "${BLUE}=== Frontend Logs ===${NC}"
            tail -n $lines $LOGS_DIR/frontend.log 2>/dev/null || print_error "Frontend log file not found"
            ;;
        *)
            print_error "Invalid service. Use 'backend', 'frontend', or 'all'"
            return 1
            ;;
    esac
}

# Function to show help
show_help() {
    echo "BettaFish Service Management Script"
    echo
    echo "Usage: $0 {start|stop|restart|status|logs|help}"
    echo
    echo "Commands:"
    echo "  start    Start both backend and frontend services"
    echo "  stop     Stop both backend and frontend services"
    echo "  restart  Restart both backend and frontend services"
    echo "  status   Show status of all services"
    echo "  logs     Show logs for services"
    echo "           Usage: $0 logs [backend|frontend|all] [lines]"
    echo "           Default lines: 50"
    echo "  help     Show this help message"
    echo
    echo "Configuration:"
    echo "  Backend Port:  $BACKEND_PORT"
    echo "  Frontend Port: $FRONTEND_PORT"
    echo "  Logs Directory: $LOGS_DIR"
}

# Main script logic
case "${1:-help}" in
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "${2:-all}" "${3:-50}"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Invalid command: $1"
        show_help
        exit 1
        ;;
esac
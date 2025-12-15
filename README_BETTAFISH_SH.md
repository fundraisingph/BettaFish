# BettaFish Service Management Script

This document explains how to use the `bettafish.sh` script for managing BettaFish services.

## Overview

The `bettafish.sh` script provides a convenient way to start, stop, restart, and monitor the BettaFish backend and frontend services.

## Prerequisites

- BettaFish backend and frontend directories
- PostgreSQL database running
- Node.js installed (for frontend)
- Python installed (for backend)
- Bash shell

## Configuration

The script uses the following configuration:
- **Backend Port**: 8065
- **Frontend Port**: 3065
- **Backend Directory**: `backend`
- **Frontend Directory**: `frontend`
- **Logs Directory**: `logs`

## Usage

```bash
./bettafish.sh {command}
```

### Available Commands

| Command | Description |
|----------|-------------|
| `start` | Start both backend and frontend services |
| `stop` | Stop both backend and frontend services |
| `restart` | Restart both backend and frontend services |
| `status` | Show status of all services |
| `logs` | Show logs for services |
| `help` | Show help message |

### Examples

```bash
# Start all services
./bettafish.sh start

# Stop all services
./bettafish.sh stop

# Restart all services
./bettafish.sh restart

# Check service status
./bettafish.sh status

# View backend logs
./bettafish.sh logs backend

# View frontend logs
./bettafish.sh logs frontend

# View all logs
./bettafish.sh logs all

# View last 100 lines of backend logs
./bettafish.sh logs backend 100
```

## Service URLs

When services are running, you can access them at:

- **Frontend**: http://localhost:3065
- **Backend API**: http://localhost:8065
- **API Documentation**: http://localhost:8065/docs
- **Health Check**: http://localhost:8065/health

## Troubleshooting

### Services Not Starting

If services fail to start:

1. Check the logs:
   ```bash
   ./bettafish.sh logs backend
   ./bettafish.sh logs frontend
   ```

2. Check port conflicts:
   ```bash
   lsof -i:8065  # Check backend port
   lsof -i:3065  # Check frontend port
   ```

3. Ensure dependencies are installed:
   ```bash
   # Check Python
   python --version
   
   # Check Node.js
   node --version
   ```

### Port Already in Use

If you get a "port already in use" error:

1. Stop existing services:
   ```bash
   ./bettafish.sh stop
   ```

2. Or kill the process using the port:
   ```bash
   # For backend (port 8065)
   kill -9 $(lsof -ti:8065)
   
   # For frontend (port 3065)
   kill -9 $(lsof -ti:3065)
   ```

### Service Not Responding

If a service shows as running but not responding:

1. Check service logs for errors:
   ```bash
   ./bettafish.sh logs backend  # or frontend
   ```

2. Restart the service:
   ```bash
   ./bettafish.sh restart
   ```

## Development Workflow

For development, you typically use:

1. Start services: `./bettafish.sh start`
2. Make changes to code
3. Restart services: `./bettafish.sh restart`
4. Check logs: `./bettafish.sh logs`

## Notes

- The script creates log files in the `logs` directory
- Services run in the background using `nohup`
- The script uses colored output for better readability
- All operations include proper error handling and status checking
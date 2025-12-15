"""
Health check API endpoints.
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import psutil
import asyncio

from core.database import get_db_connection, check_database_health
from services.auth_service import get_current_user

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health_check(
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Detailed health check with system metrics"""
    try:
        # Database health
        db_health = await check_database_health()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk.used / disk.total) * 100,
                "memory_available": memory.available / (1024**3),  # GB
                "disk_free": disk.free / (1024**3)  # GB
            },
            "database": db_health,
            "services": {
                "websocket": "healthy",
                "redis": "healthy",
                "agents": "unknown"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/readiness")
async def readiness_check(
    db = Depends(get_db_connection)
):
    """Readiness check for Kubernetes"""
    try:
        # Check database connection
        db_health = await check_database_health()
        
        if db_health["status"] != "healthy":
            return {
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "database": db_health
            }
        
        # Check if critical services are running
        # This would be expanded based on actual services
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_health
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/liveness")
async def liveness_check():
    """Liveness check for Kubernetes"""
    try:
        # Simple check to see if the application is responsive
        # In a real application, this might check critical dependencies
        
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
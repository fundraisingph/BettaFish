"""
WebSocket API endpoints - Matching Flask SocketIO functionality for full frontend parity.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from pydantic import BaseModel

from core.database import get_db_connection
from services.websocket_manager import manager
from services.auth_service import get_current_user_ws, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Message models
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]

class BroadcastMessage(BaseModel):
    message: Dict[str, Any]

class AgentMessage(BaseModel):
    message: Dict[str, Any]


# Flask SocketIO compatibility layer
class SocketIOCompatibility:
    """Compatibility layer to match Flask SocketIO events"""
    
    @staticmethod
    async def emit_connect(websocket: WebSocket, connection_id: str):
        """Emit connect event (matching SocketIO 'connect')"""
        await websocket.send_text(json.dumps({
            "type": "connect",
            "data": {
                "connection_id": connection_id,
                "message": "Connected to BettaFish WebSocket server"
            }
        }))
    
    @staticmethod
    async def emit_status(websocket: WebSocket, status_data: Dict[str, Any]):
        """Emit status update (matching SocketIO 'status')"""
        await websocket.send_text(json.dumps({
            "type": "status",
            "data": status_data
        }))
    
    @staticmethod
    async def emit_status_update(websocket: WebSocket, status_data: Dict[str, Any]):
        """Emit status update (matching SocketIO 'status_update')"""
        await websocket.send_text(json.dumps({
            "type": "status_update",
            "data": status_data
        }))
    
    @staticmethod
    async def emit_console_output(websocket: WebSocket, app: str, line: str):
        """Emit console output (matching SocketIO 'console_output')"""
        await websocket.send_text(json.dumps({
            "type": "console_output",
            "data": {
                "app": app,
                "line": line
            }
        }))
    
    @staticmethod
    async def emit_forum_message(websocket: WebSocket, message_data: Dict[str, Any]):
        """Emit forum message (matching SocketIO 'forum_message')"""
        await websocket.send_text(json.dumps({
            "type": "forum_message",
            "data": message_data
        }))


# WebSocket endpoints
@router.websocket("/frontend")
async def websocket_frontend_endpoint(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """WebSocket endpoint for frontend clients (matching Flask SocketIO)"""
    connection_id = None
    try:
        # Accept the WebSocket connection
        await websocket.accept()
        
        # Authenticate user if token provided
        user = None
        user_id = "anonymous"
        user_name = "Anonymous User"
        
        if token:
            try:
                user = await get_current_user_ws(token)
                if user:
                    user_id = str(user.get("id", "unknown"))
                    user_name = user.get("username", "Unknown User")
            except Exception as e:
                logger.warning(f"WebSocket authentication failed: {e}")
        
        # Connect to WebSocket manager
        connection_id = await manager.connect_frontend(websocket, user_id, user_name)
        
        # Send initial connection event
        await SocketIOCompatibility.emit_connect(websocket, connection_id)
        
        # Send current system status
        from api.engines import PROCESSES
        status_data = {
            app_name: {
                'status': info['status'],
                'port': info['port']
            }
            for app_name, info in PROCESSES.items()
        }
        await SocketIOCompatibility.emit_status_update(websocket, status_data)
        
        # Handle WebSocket messages
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                
                # Parse message
                try:
                    message_data = json.loads(data)
                except json.JSONDecodeError:
                    # Handle plain text messages
                    message_data = {"type": "text", "data": data}
                
                # Handle different message types
                message_type = message_data.get("type", "unknown")
                
                if message_type == "request_status":
                    # Handle status request (matching SocketIO 'request_status')
                    from api.engines import check_app_status
                    check_app_status()
                    status_data = {
                        app_name: {
                            'status': info['status'],
                            'port': info['port']
                        }
                        for app_name, info in PROCESSES.items()
                    }
                    await SocketIOCompatibility.emit_status_update(websocket, status_data)
                
                elif message_type == "subscribe_engine":
                    # Handle engine subscription
                    engine_type = message_data.get("data", {}).get("engine_type")
                    if engine_type:
                        await manager.join_room(connection_id, f"engine_{engine_type}")
                
                elif message_type == "unsubscribe_engine":
                    # Handle engine unsubscription
                    engine_type = message_data.get("data", {}).get("engine_type")
                    if engine_type:
                        await manager.leave_room(connection_id, f"engine_{engine_type}")
                
                elif message_type == "agent_message":
                    # Forward message to agent
                    agent_type = message_data.get("data", {}).get("agent_type")
                    message = message_data.get("data", {}).get("message")
                    if agent_type and message:
                        await manager.send_to_engine(message, agent_type)
                
                else:
                    logger.warning(f"Unknown WebSocket message type: {message_type}")
            
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                break
    
    except WebSocketDisconnect:
        logger.info(f"Frontend WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=1000, reason=str(e))
    finally:
        if connection_id:
            await manager.disconnect(connection_id)


@router.websocket("/agents/{agent_type}")
async def websocket_agent_endpoint(
    websocket: WebSocket,
    agent_type: str,
    api_key: Optional[str] = None
):
    """WebSocket endpoint for agent processes (matching Flask SocketIO)"""
    connection_id = None
    try:
        await websocket.accept()
        
        # Authenticate agent
        if not api_key:
            await websocket.close(code=4001, reason="API key required")
            return
        
        # Validate agent type
        valid_agents = ['insight', 'media', 'query', 'report']
        if agent_type not in valid_agents:
            await websocket.close(code=4004, reason="Invalid agent type")
            return
        
        # Connect to WebSocket manager
        connection_id = await manager.connect_agent(websocket, agent_type)
        
        # Handle WebSocket messages
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                
                # Parse message
                try:
                    message_data = json.loads(data)
                except json.JSONDecodeError:
                    message_data = {"type": "text", "data": data}
                
                # Handle message
                response = await manager.handle_message(connection_id, message_data)
                
                # Send response if available
                if response:
                    await websocket.send_text(json.dumps(response))
            
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error handling agent WebSocket message: {e}")
                break
    
    except WebSocketDisconnect:
        logger.info(f"Agent WebSocket disconnected: {agent_type} ({connection_id})")
    except Exception as e:
        logger.error(f"Agent WebSocket connection error: {e}")
        await websocket.close(code=1000, reason=str(e))
    finally:
        if connection_id:
            await manager.disconnect(connection_id)


# REST API endpoints for WebSocket management
@router.get("/connections")
async def get_websocket_connections(
    user: dict = Depends(get_current_user)
):
    """Get active WebSocket connections"""
    try:
        status = manager.get_connection_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/broadcast")
async def broadcast_message(
    message: BroadcastMessage,
    user: dict = Depends(get_current_user)
):
    """Broadcast message to all frontend connections"""
    try:
        await manager.broadcast_to_frontend(message.message)
        return {
            "success": True,
            "message": "Broadcast sent successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/send-to-agent/{agent_type}")
async def send_to_agent(
    agent_type: str,
    message: AgentMessage,
    user: dict = Depends(get_current_user)
):
    """Send message to specific agent"""
    try:
        await manager.send_to_engine(message.message, agent_type)
        return {
            "success": True,
            "message": f"Message sent to {agent_type} agent"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/send-to-frontend")
async def send_to_frontend(
    message: BroadcastMessage,
    user: dict = Depends(get_current_user)
):
    """Send message to all frontend connections"""
    try:
        await manager.send_to_frontend(message.message)
        return {
            "success": True,
            "message": "Message sent to frontend"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/send-to-room/{room_id}")
async def send_to_room(
    room_id: str,
    message: BroadcastMessage,
    user: dict = Depends(get_current_user)
):
    """Send message to specific room"""
    try:
        await manager.broadcast_to_room(message.message, room_id)
        return {
            "success": True,
            "message": f"Message sent to room {room_id}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/rooms")
async def get_rooms(
    user: dict = Depends(get_current_user)
):
    """Get all active rooms and their connections"""
    try:
        status = manager.get_connection_status()
        return {
            "success": True,
            "data": {
                "rooms": status.get("rooms", {}),
                "total_rooms": len(status.get("rooms", {}))
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Helper functions for compatibility
async def handle_frontend_message(websocket: WebSocket, data: str, user: Optional[dict]):
    """Handle frontend message (compatibility with Flask)"""
    try:
        message_data = json.loads(data)
        message_type = message_data.get("type", "unknown")
        
        if message_type == "request_status":
            # Handle status request
            from api.engines import check_app_status, PROCESSES
            check_app_status()
            status_data = {
                app_name: {
                    'status': info['status'],
                    'port': info['port']
                }
                for app_name, info in PROCESSES.items()
            }
            await SocketIOCompatibility.emit_status_update(websocket, status_data)
    
    except Exception as e:
        logger.error(f"Error handling frontend message: {e}")


async def handle_agent_message(websocket: WebSocket, data: str, agent_type: str):
    """Handle agent message (compatibility with Flask)"""
    try:
        message_data = json.loads(data)
        
        # Broadcast agent message to frontend
        await manager.send_to_frontend({
            "type": "agent_message",
            "agent_type": agent_type,
            "data": message_data
        })
    
    except Exception as e:
        logger.error(f"Error handling agent message: {e}")


async def disconnect_frontend(websocket: WebSocket):
    """Disconnect frontend client"""
    try:
        await websocket.close()
    except Exception:
        pass


async def disconnect_agent(websocket: WebSocket, agent_type: str):
    """Disconnect agent"""
    try:
        await websocket.close()
    except Exception:
        pass


async def get_active_connections() -> List[Dict[str, Any]]:
    """Get active connections (compatibility)"""
    status = manager.get_connection_status()
    connections = []
    
    for connection_id, metadata in status.get("connections", {}).items():
        connections.append({
            "id": connection_id,
            "type": metadata.get("type"),
            "connected_at": metadata.get("connected_at"),
            "last_ping": metadata.get("last_ping")
        })
    
    return connections


async def send_to_agent(agent_type: str, message: Dict[str, Any]) -> bool:
    """Send message to agent (compatibility)"""
    try:
        await manager.send_to_engine(message, agent_type)
        return True
    except Exception:
        return False
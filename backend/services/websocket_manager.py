"""
WebSocket manager for real-time communication between frontend and agents.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from fastapi import WebSocket, WebSocketDisconnect

from core.database import get_db_connection
from core.exceptions import WebSocketException

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        # Store active connections
        self.frontend_connections: Dict[str, WebSocket] = {}
        self.agent_connections: Dict[str, WebSocket] = {}
        
        # Store connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Store room subscriptions
        self.rooms: Dict[str, List[str]] = {}
        
        self.db = None
    
    async def _get_db(self):
        """Get database connection lazily"""
        if self.db is None:
            self.db = await get_db_connection()
        return self.db
    
    async def connect_frontend(
        self,
        websocket: WebSocket,
        user_id: str,
        user_name: str
    ) -> str:
        """Connect a frontend client"""
        connection_id = str(uuid.uuid4())
        
        await websocket.accept()
        
        # Store connection
        self.frontend_connections[connection_id] = websocket
        
        # Store metadata
        self.connection_metadata[connection_id] = {
            "type": "frontend",
            "user_id": user_id,
            "user_name": user_name,
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow()
        }
        
        # Join user-specific room
        await self.join_room(connection_id, f"user_{user_id}")
        
        logger.info(f"Frontend client connected: {connection_id} (user: {user_name})")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "message": "Connected to BettaFish WebSocket server",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
        
        return connection_id
    
    async def connect_agent(
        self,
        websocket: WebSocket,
        engine_type: str,
        task_id: Optional[str] = None
    ) -> str:
        """Connect an agent"""
        connection_id = str(uuid.uuid4())
        
        await websocket.accept()
        
        # Store connection
        self.agent_connections[connection_id] = websocket
        
        # Store metadata
        self.connection_metadata[connection_id] = {
            "type": "agent",
            "engine_type": engine_type,
            "task_id": task_id,
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow()
        }
        
        # Join engine-specific room
        await self.join_room(connection_id, f"engine_{engine_type}")
        
        # Join task-specific room if provided
        if task_id:
            await self.join_room(connection_id, f"task_{task_id}")
        
        logger.info(f"Agent connected: {connection_id} (engine: {engine_type})")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "message": "Connected to BettaFish WebSocket server",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Disconnect a client"""
        if connection_id in self.frontend_connections:
            del self.frontend_connections[connection_id]
            logger.info(f"Frontend client disconnected: {connection_id}")
        
        elif connection_id in self.agent_connections:
            del self.agent_connections[connection_id]
            logger.info(f"Agent disconnected: {connection_id}")
        
        # Remove from all rooms
        if connection_id in self.connection_metadata:
            metadata = self.connection_metadata[connection_id]
            del self.connection_metadata[connection_id]
            
            # Remove from rooms
            for room_id, connections in self.rooms.items():
                if connection_id in connections:
                    connections.remove(connection_id)
    
    async def join_room(self, connection_id: str, room_id: str):
        """Add connection to a room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = []
        
        if connection_id not in self.rooms[room_id]:
            self.rooms[room_id].append(connection_id)
            
            logger.debug(f"Connection {connection_id} joined room {room_id}")
    
    async def leave_room(self, connection_id: str, room_id: str):
        """Remove connection from a room"""
        if room_id in self.rooms and connection_id in self.rooms[room_id]:
            self.rooms[room_id].remove(connection_id)
            
            # Clean up empty rooms
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            
            logger.debug(f"Connection {connection_id} left room {room_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], connection_id: str):
        """Send message to specific connection"""
        websocket = None
        
        if connection_id in self.frontend_connections:
            websocket = self.frontend_connections[connection_id]
        elif connection_id in self.agent_connections:
            websocket = self.agent_connections[connection_id]
        
        if websocket:
            try:
                # Ensure message is properly serialized and ordered
                message_str = json.dumps(message, ensure_ascii=False, separators=(',', ':'))
                await websocket.send_text(message_str)
                # Small delay to ensure message ordering in ASGI
                await asyncio.sleep(0.001)
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                await self.disconnect(connection_id)
    
    async def broadcast_to_room(self, message: Dict[str, Any], room_id: str):
        """Broadcast message to all connections in a room"""
        if room_id not in self.rooms:
            return
        
        # Create copy of connections to avoid modification during iteration
        connections = self.rooms[room_id].copy()
        
        for connection_id in connections:
            await self.send_personal_message(message, connection_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        # Send to frontend clients
        for connection_id in list(self.frontend_connections.keys()):
            await self.send_personal_message(message, connection_id)
        
        # Send to agent connections
        for connection_id in list(self.agent_connections.keys()):
            await self.send_personal_message(message, connection_id)
    
    async def broadcast_to_frontend(self, message: Dict[str, Any]):
        """Broadcast message to all frontend clients"""
        await self.send_to_frontend(message)
    
    async def send_to_frontend(self, message: Dict[str, Any]):
        """Send message to all frontend clients"""
        for connection_id in list(self.frontend_connections.keys()):
            await self.send_personal_message(message, connection_id)
    
    async def send_to_agents(self, message: Dict[str, Any]):
        """Send message to all agent connections"""
        for connection_id in list(self.agent_connections.keys()):
            await self.send_personal_message(message, connection_id)
    
    async def send_to_engine(self, message: Dict[str, Any], engine_type: str):
        """Send message to specific engine type"""
        room_id = f"engine_{engine_type}"
        await self.broadcast_to_room(message, room_id)
    
    async def send_to_task(self, message: Dict[str, Any], task_id: str):
        """Send message to specific task"""
        room_id = f"task_{task_id}"
        await self.broadcast_to_room(message, room_id)
    
    async def send_to_user(self, message: Dict[str, Any], user_id: str):
        """Send message to specific user"""
        room_id = f"user_{user_id}"
        await self.broadcast_to_room(message, room_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients (alias for broadcast_to_all)"""
        await self.broadcast_to_all(message)
    
    async def handle_message(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle incoming message from connection"""
        message_type = message.get("type", "unknown")
        
        # Update last ping
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]["last_ping"] = datetime.utcnow()
        
        # Handle different message types
        if message_type == "ping":
            return {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
        
        elif message_type == "log":
            # Handle log message from agent
            await self.handle_log_message(connection_id, message)
            return {"type": "log_ack", "timestamp": datetime.utcnow().isoformat()}
        
        elif message_type == "progress":
            # Handle progress update from agent
            await self.handle_progress_message(connection_id, message)
            return {"type": "progress_ack", "timestamp": datetime.utcnow().isoformat()}
        
        elif message_type == "result":
            # Handle result message from agent
            await self.handle_result_message(connection_id, message)
            return {"type": "result_ack", "timestamp": datetime.utcnow().isoformat()}
        
        elif message_type == "error":
            # Handle error message from agent
            await self.handle_error_message(connection_id, message)
            return {"type": "error_ack", "timestamp": datetime.utcnow().isoformat()}
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
            return {
                "type": "error",
                "message": f"Unknown message type: {message_type}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def handle_log_message(self, connection_id: str, message: Dict[str, Any]):
        """Handle log message from agent"""
        metadata = self.connection_metadata.get(connection_id, {})
        
        if metadata.get("type") != "agent":
            logger.warning(f"Log message from non-agent connection: {connection_id}")
            return
        
        # Store log in database
        db = await self._get_db()
        
        try:
            await db.execute(
                """
                INSERT INTO agent_logs (agent_id, engine_type, task_id, level, message, data, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
                """,
                connection_id,
                metadata.get("engine_type"),
                metadata.get("task_id"),
                message.get("level", "INFO"),
                message.get("message", ""),
                json.dumps(message.get("data", {}))
            )
        except Exception as e:
            logger.error(f"Error storing log message: {e}")
        
        # Broadcast log to frontend clients
        await self.send_to_frontend({
            "type": "agent_log",
            "engine_type": metadata.get("engine_type"),
            "task_id": metadata.get("task_id"),
            "level": message.get("level", "INFO"),
            "message": message.get("message", ""),
            "data": message.get("data", {}),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def handle_progress_message(self, connection_id: str, message: Dict[str, Any]):
        """Handle progress update from agent"""
        metadata = self.connection_metadata.get(connection_id, {})
        
        if metadata.get("type") != "agent":
            logger.warning(f"Progress message from non-agent connection: {connection_id}")
            return
        
        # Update task progress in database
        task_id = metadata.get("task_id")
        if task_id:
            db = await self._get_db()
            
            try:
                await db.execute(
                    """
                    UPDATE analysis_tasks
                    SET progress = $1, status = $2, updated_at = NOW()
                    WHERE id = $3
                    """,
                    message.get("progress", 0),
                    message.get("status", "RUNNING"),
                    task_id
                )
            except Exception as e:
                logger.error(f"Error updating task progress: {e}")
        
        # Broadcast progress to frontend clients
        await self.send_to_frontend({
            "type": "agent_progress",
            "engine_type": metadata.get("engine_type"),
            "task_id": task_id,
            "progress": message.get("progress", 0),
            "status": message.get("status", "RUNNING"),
            "message": message.get("message", ""),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def handle_result_message(self, connection_id: str, message: Dict[str, Any]):
        """Handle result message from agent"""
        metadata = self.connection_metadata.get(connection_id, {})
        
        if metadata.get("type") != "agent":
            logger.warning(f"Result message from non-agent connection: {connection_id}")
            return
        
        # Store result in database
        task_id = metadata.get("task_id")
        if task_id:
            db = await self._get_db()
            
            try:
                await db.execute(
                    """
                    INSERT INTO agent_outputs (task_id, engine_type, output_type, content, metadata, timestamp)
                    VALUES ($1, $2, $3, $4, $5, NOW())
                    """,
                    task_id,
                    metadata.get("engine_type"),
                    message.get("output_type", "result"),
                    message.get("content", ""),
                    json.dumps(message.get("metadata", {}))
                )
                
                # Update task status
                await db.execute(
                    """
                    UPDATE analysis_tasks
                    SET status = 'COMPLETED', progress = 100, updated_at = NOW()
                    WHERE id = $1
                    """,
                    task_id
                )
            except Exception as e:
                logger.error(f"Error storing result: {e}")
        
        # Broadcast result to frontend clients
        await self.send_to_frontend({
            "type": "agent_result",
            "engine_type": metadata.get("engine_type"),
            "task_id": task_id,
            "output_type": message.get("output_type", "result"),
            "content": message.get("content", ""),
            "metadata": message.get("metadata", {}),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def handle_error_message(self, connection_id: str, message: Dict[str, Any]):
        """Handle error message from agent"""
        metadata = self.connection_metadata.get(connection_id, {})
        
        if metadata.get("type") != "agent":
            logger.warning(f"Error message from non-agent connection: {connection_id}")
            return
        
        # Store error in database
        task_id = metadata.get("task_id")
        if task_id:
            db = await self._get_db()
            
            try:
                await db.execute(
                    """
                    INSERT INTO agent_outputs (task_id, engine_type, output_type, content, metadata, timestamp)
                    VALUES ($1, $2, 'error', $3, $4, NOW())
                    """,
                    task_id,
                    metadata.get("engine_type"),
                    message.get("error", ""),
                    json.dumps({
                        "error_type": message.get("error_type", "unknown"),
                        "stack_trace": message.get("stack_trace", "")
                    })
                )
                
                # Update task status
                await db.execute(
                    """
                    UPDATE analysis_tasks
                    SET status = 'FAILED', updated_at = NOW()
                    WHERE id = $1
                    """,
                    task_id
                )
            except Exception as e:
                logger.error(f"Error storing error: {e}")
        
        # Broadcast error to frontend clients
        await self.send_to_frontend({
            "type": "agent_error",
            "engine_type": metadata.get("engine_type"),
            "task_id": task_id,
            "error": message.get("error", ""),
            "error_type": message.get("error_type", "unknown"),
            "stack_trace": message.get("stack_trace", ""),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get status of all connections"""
        return {
            "frontend_connections": len(self.frontend_connections),
            "agent_connections": len(self.agent_connections),
            "total_connections": len(self.frontend_connections) + len(self.agent_connections),
            "rooms": {room_id: len(connections) for room_id, connections in self.rooms.items()},
            "connections": {
                connection_id: {
                    "type": metadata.get("type"),
                    "connected_at": metadata.get("connected_at").isoformat() if metadata.get("connected_at") else None,
                    "last_ping": metadata.get("last_ping").isoformat() if metadata.get("last_ping") else None
                }
                for connection_id, metadata in self.connection_metadata.items()
            }
        }


# Global connection manager instance
manager = ConnectionManager()


# Dependency injection function
def get_websocket_manager() -> ConnectionManager:
    """Get WebSocket manager instance"""
    return manager
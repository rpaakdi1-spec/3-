"""
Advanced WebSocket Connection Manager

Features:
- Multiple channels support
- Automatic heartbeat/ping-pong
- Connection tracking per user/channel
- Broadcast to specific channels
- Redis Pub/Sub integration
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Advanced WebSocket Connection Manager
    
    Manages multiple WebSocket connections across different channels
    with automatic heartbeat, reconnection support, and Redis Pub/Sub.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        # Active connections per channel
        # Format: {channel: {connection_id: WebSocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = defaultdict(dict)
        
        # User ID to connection mapping
        # Format: {user_id: {channel: connection_id}}
        self.user_connections: Dict[int, Dict[str, str]] = defaultdict(dict)
        
        # Connection metadata
        # Format: {connection_id: {user_id, channel, connected_at, last_ping}}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Redis for Pub/Sub
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        self.pubsub_task: Optional[asyncio.Task] = None
        
        # Heartbeat interval (seconds)
        self.heartbeat_interval = 30
        self.heartbeat_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize Redis connection and start background tasks"""
        if self.redis_url:
            try:
                self.redis_client = await aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                logger.info("✅ Redis connection established for WebSocket")
                
                # Start Pub/Sub listener
                self.pubsub_task = asyncio.create_task(self._redis_pubsub_listener())
            except Exception as e:
                logger.error(f"❌ Failed to connect to Redis: {e}")
        
        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("✅ WebSocket Connection Manager initialized")
    
    async def shutdown(self):
        """Shutdown and cleanup"""
        if self.pubsub_task:
            self.pubsub_task.cancel()
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("✅ WebSocket Connection Manager shutdown")
    
    def generate_connection_id(self, user_id: int, channel: str) -> str:
        """Generate unique connection ID"""
        timestamp = datetime.utcnow().timestamp()
        return f"{channel}:{user_id}:{int(timestamp)}"
    
    async def connect(
        self,
        websocket: WebSocket,
        channel: str,
        user_id: Optional[int] = None
    ) -> str:
        """
        Accept new WebSocket connection
        
        Args:
            websocket: WebSocket connection
            channel: Channel name (dashboard, dispatches, vehicles, etc.)
            user_id: User ID (optional)
        
        Returns:
            connection_id: Unique connection identifier
        """
        await websocket.accept()
        
        connection_id = self.generate_connection_id(user_id or 0, channel)
        
        # Store connection
        self.active_connections[channel][connection_id] = websocket
        
        # Store metadata
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "channel": channel,
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow()
        }
        
        # Map user to connection
        if user_id:
            self.user_connections[user_id][channel] = connection_id
        
        logger.info(
            f"🔌 WebSocket connected: "
            f"channel={channel}, user_id={user_id}, "
            f"connection_id={connection_id}"
        )
        
        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connected",
                "connection_id": connection_id,
                "channel": channel,
                "timestamp": datetime.utcnow().isoformat()
            },
            websocket
        )
        
        return connection_id
    
    def disconnect(self, connection_id: str):
        """
        Remove connection
        
        Args:
            connection_id: Connection identifier
        """
        if connection_id not in self.connection_metadata:
            return
        
        metadata = self.connection_metadata[connection_id]
        channel = metadata["channel"]
        user_id = metadata["user_id"]
        
        # Remove from active connections
        if channel in self.active_connections:
            if connection_id in self.active_connections[channel]:
                del self.active_connections[channel][connection_id]
            
            # Clean up empty channels
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        
        # Remove from user connections
        if user_id and user_id in self.user_connections:
            if channel in self.user_connections[user_id]:
                del self.user_connections[user_id][channel]
            
            # Clean up empty user mappings
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove metadata
        del self.connection_metadata[connection_id]
        
        logger.info(
            f"🔌 WebSocket disconnected: "
            f"channel={channel}, user_id={user_id}, "
            f"connection_id={connection_id}"
        )
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"❌ Failed to send personal message: {e}")
    
    async def broadcast_to_channel(self, channel: str, message: dict):
        """
        Broadcast message to all connections in a channel
        
        Args:
            channel: Channel name
            message: Message dictionary
        """
        if channel not in self.active_connections:
            return
        
        disconnected = []
        
        for connection_id, websocket in self.active_connections[channel].items():
            try:
                await websocket.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection_id)
            except Exception as e:
                logger.error(f"❌ Error broadcasting to {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    async def send_to_user(self, user_id: int, channel: str, message: dict):
        """
        Send message to specific user on a channel
        
        Args:
            user_id: User ID
            channel: Channel name
            message: Message dictionary
        """
        if user_id not in self.user_connections:
            return
        
        if channel not in self.user_connections[user_id]:
            return
        
        connection_id = self.user_connections[user_id][channel]
        
        if channel not in self.active_connections:
            return
        
        if connection_id not in self.active_connections[channel]:
            return
        
        websocket = self.active_connections[channel][connection_id]
        
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"❌ Failed to send to user {user_id}: {e}")
            self.disconnect(connection_id)
    
    async def broadcast_to_all(self, message: dict, exclude_channel: Optional[str] = None):
        """
        Broadcast message to all channels
        
        Args:
            message: Message dictionary
            exclude_channel: Channel to exclude (optional)
        """
        for channel in list(self.active_connections.keys()):
            if exclude_channel and channel == exclude_channel:
                continue
            await self.broadcast_to_channel(channel, message)
    
    async def publish_to_redis(self, channel: str, message: dict):
        """
        Publish message to Redis Pub/Sub
        
        This allows multiple server instances to communicate
        
        Args:
            channel: Redis channel
            message: Message dictionary
        """
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.publish(
                f"ws:{channel}",
                json.dumps(message, default=str)
            )
        except Exception as e:
            logger.error(f"❌ Failed to publish to Redis: {e}")
    
    async def _redis_pubsub_listener(self):
        """Background task to listen for Redis Pub/Sub messages"""
        if not self.redis_client:
            return
        
        try:
            pubsub = self.redis_client.pubsub()
            
            # Subscribe to all WebSocket channels
            await pubsub.psubscribe("ws:*")
            
            logger.info("👂 Redis Pub/Sub listener started")
            
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    try:
                        channel = message["channel"].decode().replace("ws:", "")
                        data = json.loads(message["data"].decode())
                        
                        # Broadcast to WebSocket channel
                        await self.broadcast_to_channel(channel, data)
                    except Exception as e:
                        logger.error(f"❌ Error processing Pub/Sub message: {e}")
        except asyncio.CancelledError:
            logger.info("🛑 Redis Pub/Sub listener stopped")
        except Exception as e:
            logger.error(f"❌ Redis Pub/Sub listener error: {e}")
    
    async def _heartbeat_loop(self):
        """Background task to send periodic heartbeat/ping"""
        try:
            while True:
                await asyncio.sleep(self.heartbeat_interval)
                
                disconnected = []
                
                for channel, connections in list(self.active_connections.items()):
                    for connection_id, websocket in list(connections.items()):
                        try:
                            # Send ping
                            await websocket.send_json({
                                "type": "ping",
                                "timestamp": datetime.utcnow().isoformat()
                            })
                            
                            # Update last ping time
                            if connection_id in self.connection_metadata:
                                self.connection_metadata[connection_id]["last_ping"] = datetime.utcnow()
                        except Exception:
                            disconnected.append(connection_id)
                
                # Clean up disconnected
                for connection_id in disconnected:
                    self.disconnect(connection_id)
                
                if disconnected:
                    logger.info(f"🧹 Cleaned up {len(disconnected)} stale connections")
        except asyncio.CancelledError:
            logger.info("🛑 Heartbeat loop stopped")
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        total_connections = sum(
            len(connections) for connections in self.active_connections.values()
        )
        
        return {
            "total_connections": total_connections,
            "channels": len(self.active_connections),
            "active_users": len(self.user_connections),
            "connections_per_channel": {
                channel: len(connections)
                for channel, connections in self.active_connections.items()
            }
        }


# Global instance
manager = ConnectionManager()

"""
WebSocket connection manager for handling real-time connections
"""
from fastapi import WebSocket
from typing import Dict, List, Set, Optional, Any
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Manages WebSocket connections, user subscriptions, and message broadcasting
    """
    
    def __init__(self):
        # Active connections: {user_id: websocket}
        self.active_connections: Dict[int, WebSocket] = {}
        
        # User information: {user_id: {"email": str, "is_admin": bool, "connected_at": datetime}}
        self.user_info: Dict[int, Dict[str, Any]] = {}
        
        # Channel subscriptions: {channel_name: {user_id}}
        self.channel_subscriptions: Dict[str, Set[int]] = {
            "dashboard": set(),
            "products": set(),
            "stock_movements": set(),
            "stock_transfers": set(),
        }
        
        # User subscriptions: {user_id: {channel_name}}
        self.user_subscriptions: Dict[int, Set[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, email: str, is_admin: bool):
        """
        Add a new WebSocket connection
        """
        self.active_connections[user_id] = websocket
        self.user_info[user_id] = {
            "email": email,
            "is_admin": is_admin,
            "connected_at": datetime.utcnow()
        }
        self.user_subscriptions[user_id] = set()
        
        logger.info(f"WebSocket connection added for user {user_id} ({email})")

    async def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Remove a WebSocket connection
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            
        if user_id in self.user_info:
            del self.user_info[user_id]
            
        # Remove user from all channel subscriptions
        if user_id in self.user_subscriptions:
            for channel in self.user_subscriptions[user_id]:
                if channel in self.channel_subscriptions:
                    self.channel_subscriptions[channel].discard(user_id)
            del self.user_subscriptions[user_id]
            
        logger.info(f"WebSocket connection removed for user {user_id}")

    async def send_personal_message(self, message: Dict[str, Any], user_id: int):
        """
        Send a message to a specific user
        """
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                # Remove disconnected connection
                await self.disconnect(self.active_connections.get(user_id), user_id)
                return False
        return False

    async def broadcast_to_all(self, message: Dict[str, Any], exclude_user_id: Optional[int] = None):
        """
        Broadcast a message to all connected users
        """
        if not self.active_connections:
            return
            
        disconnected_users = []
        
        for user_id, websocket in self.active_connections.items():
            if exclude_user_id and user_id == exclude_user_id:
                continue
                
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # Clean up disconnected connections
        for user_id in disconnected_users:
            await self.disconnect(self.active_connections.get(user_id), user_id)

    async def broadcast_to_admins(self, message: Dict[str, Any], exclude_user_id: Optional[int] = None):
        """
        Broadcast a message to all admin users
        """
        if not self.active_connections:
            return
            
        disconnected_users = []
        
        for user_id, websocket in self.active_connections.items():
            if exclude_user_id and user_id == exclude_user_id:
                continue
                
            if user_id in self.user_info and self.user_info[user_id].get("is_admin"):
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to admin {user_id}: {e}")
                    disconnected_users.append(user_id)
        
        # Clean up disconnected connections
        for user_id in disconnected_users:
            await self.disconnect(self.active_connections.get(user_id), user_id)

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any], exclude_user_id: Optional[int] = None):
        """
        Broadcast a message to all users subscribed to a specific channel
        """
        if channel not in self.channel_subscriptions:
            logger.warning(f"Channel {channel} does not exist")
            return
            
        subscribed_users = self.channel_subscriptions[channel].copy()
        disconnected_users = []
        
        for user_id in subscribed_users:
            if exclude_user_id and user_id == exclude_user_id:
                continue
                
            if user_id in self.active_connections:
                try:
                    websocket = self.active_connections[user_id]
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id} in channel {channel}: {e}")
                    disconnected_users.append(user_id)
        
        # Clean up disconnected connections
        for user_id in disconnected_users:
            await self.disconnect(self.active_connections.get(user_id), user_id)

    async def subscribe_to_channel(self, user_id: int, channel: str):
        """
        Subscribe a user to a specific channel
        """
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()
            
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()
            
        self.channel_subscriptions[channel].add(user_id)
        self.user_subscriptions[user_id].add(channel)
        
        logger.info(f"User {user_id} subscribed to channel {channel}")

    async def unsubscribe_from_channel(self, user_id: int, channel: str):
        """
        Unsubscribe a user from a specific channel
        """
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(user_id)
            
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].discard(channel)
            
        logger.info(f"User {user_id} unsubscribed from channel {channel}")

    def get_online_users(self) -> List[Dict[str, Any]]:
        """
        Get list of all online users (for admin purposes)
        """
        online_users = []
        for user_id, info in self.user_info.items():
            if user_id in self.active_connections:
                online_users.append({
                    "id": user_id,
                    "email": info["email"],
                    "is_admin": info["is_admin"],
                    "connected_at": info["connected_at"].isoformat(),
                    "subscribed_channels": list(self.user_subscriptions.get(user_id, set()))
                })
        return online_users

    def get_channel_stats(self) -> Dict[str, int]:
        """
        Get statistics about channel subscriptions
        """
        stats = {}
        for channel, users in self.channel_subscriptions.items():
            stats[channel] = len(users)
        return stats

    def get_connection_count(self) -> int:
        """
        Get total number of active connections
        """
        return len(self.active_connections)

    async def send_system_message(self, message: str, message_type: str = "info"):
        """
        Send a system message to all connected users
        """
        system_message = {
            "type": "system_message",
            "message_type": message_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_all(system_message)
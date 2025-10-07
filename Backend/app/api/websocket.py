"""
WebSocket API endpoint for real-time communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, List, Set, Optional, Any
import json
import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_database
from app.core.security import verify_token
from app.models.models import User
from app.services.websocket_manager import WebSocketManager

router = APIRouter()
security = HTTPBearer()

# Initialize WebSocket manager
ws_manager = WebSocketManager()

logger = logging.getLogger(__name__)

async def get_current_user_websocket(websocket: WebSocket, token: str, db: Session) -> Optional[User]:
    """
    Get current user from WebSocket token for authentication
    """
    try:
        payload = verify_token(token)
        if payload is None:
            return None

        user_id = payload.get("user_id")
        if user_id is None:
            return None

        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        return None

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_database)):
    """
    Main WebSocket endpoint for real-time communication
    """
    await websocket.accept()
    user = None
    
    try:
        # Wait for authentication message
        auth_data = await websocket.receive_text()
        auth_message = json.loads(auth_data)
        
        if auth_message.get("type") != "authenticate":
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Authentication required"
            }))
            await websocket.close()
            return
            
        token = auth_message.get("token")
        if not token:
            await websocket.send_text(json.dumps({
                "type": "error", 
                "message": "Token required"
            }))
            await websocket.close()
            return
            
        # Authenticate user
        user = await get_current_user_websocket(websocket, token, db)
        if not user:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Invalid token"
            }))
            await websocket.close()
            return
            
        # Add connection to manager
        await ws_manager.connect(websocket, user.id, user.email, user.is_admin)
        
        # Send authentication success
        await websocket.send_text(json.dumps({
            "type": "authenticated",
            "user": {
                "id": user.id,
                "email": user.email,
                "is_admin": user.is_admin
            }
        }))
        
        logger.info(f"WebSocket connected: User {user.email} (ID: {user.id})")
        
        # Broadcast user connection to admins
        if user.is_admin:
            await ws_manager.broadcast_to_admins({
                "type": "admin_connected",
                "user": {"id": user.id, "email": user.email},
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_user_id=user.id)
        
        # Listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await handle_websocket_message(websocket, user, message, db)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Internal server error"
                }))
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if user:
            await ws_manager.disconnect(websocket, user.id)
            logger.info(f"WebSocket disconnected: User {user.email} (ID: {user.id})")

async def handle_websocket_message(websocket: WebSocket, user: User, message: Dict[str, Any], db: Session):
    """
    Handle incoming WebSocket messages
    """
    message_type = message.get("type")
    
    if message_type == "ping":
        await websocket.send_text(json.dumps({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    elif message_type == "subscribe_dashboard":
        # Subscribe user to dashboard updates
        await ws_manager.subscribe_to_channel(user.id, "dashboard")
        await websocket.send_text(json.dumps({
            "type": "subscribed",
            "channel": "dashboard"
        }))
    
    elif message_type == "unsubscribe_dashboard":
        # Unsubscribe user from dashboard updates
        await ws_manager.unsubscribe_from_channel(user.id, "dashboard")
        await websocket.send_text(json.dumps({
            "type": "unsubscribed",
            "channel": "dashboard"
        }))
    
    elif message_type == "subscribe_products":
        # Subscribe user to product updates
        await ws_manager.subscribe_to_channel(user.id, "products")
        await websocket.send_text(json.dumps({
            "type": "subscribed", 
            "channel": "products"
        }))
    
    elif message_type == "unsubscribe_products":
        # Unsubscribe user from product updates
        await ws_manager.unsubscribe_from_channel(user.id, "products")
        await websocket.send_text(json.dumps({
            "type": "unsubscribed",
            "channel": "products"
        }))
    
    elif message_type == "subscribe_stock_movements":
        # Subscribe user to stock movement updates
        await ws_manager.subscribe_to_channel(user.id, "stock_movements")
        await websocket.send_text(json.dumps({
            "type": "subscribed",
            "channel": "stock_movements"
        }))
    
    elif message_type == "unsubscribe_stock_movements":
        # Unsubscribe user from stock movement updates
        await ws_manager.unsubscribe_from_channel(user.id, "stock_movements")
        await websocket.send_text(json.dumps({
            "type": "unsubscribed",
            "channel": "stock_movements"
        }))
    
    elif message_type == "subscribe_stock_transfers":
        # Subscribe user to stock transfer updates
        await ws_manager.subscribe_to_channel(user.id, "stock_transfers")
        await websocket.send_text(json.dumps({
            "type": "subscribed",
            "channel": "stock_transfers"
        }))
    
    elif message_type == "unsubscribe_stock_transfers":
        # Unsubscribe user from stock transfer updates
        await ws_manager.unsubscribe_from_channel(user.id, "stock_transfers")
        await websocket.send_text(json.dumps({
            "type": "unsubscribed",
            "channel": "stock_transfers"
        }))
    
    elif message_type == "get_online_users" and user.is_admin:
        # Get list of online users (admin only)
        online_users = ws_manager.get_online_users()
        await websocket.send_text(json.dumps({
            "type": "online_users",
            "users": online_users
        }))
    
    else:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }))

# Helper functions for other parts of the application to broadcast events
async def broadcast_product_update(product_data: Dict[str, Any]):
    """Broadcast product update to subscribed users"""
    await ws_manager.broadcast_to_channel("products", {
        "type": "product_updated",
        "data": product_data,
        "timestamp": datetime.utcnow().isoformat()
    })

async def broadcast_stock_movement(movement_data: Dict[str, Any]):
    """Broadcast stock movement to subscribed users"""
    await ws_manager.broadcast_to_channel("stock_movements", {
        "type": "stock_movement_created",
        "data": movement_data,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Also broadcast to dashboard for live stats
    await ws_manager.broadcast_to_channel("dashboard", {
        "type": "dashboard_update",
        "update_type": "stock_movement",
        "data": movement_data,
        "timestamp": datetime.utcnow().isoformat()
    })

async def broadcast_stock_transfer(transfer_data: Dict[str, Any]):
    """Broadcast stock transfer to subscribed users"""
    await ws_manager.broadcast_to_channel("stock_transfers", {
        "type": "stock_transfer_updated", 
        "data": transfer_data,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Also broadcast to dashboard for live stats
    await ws_manager.broadcast_to_channel("dashboard", {
        "type": "dashboard_update",
        "update_type": "stock_transfer",
        "data": transfer_data,
        "timestamp": datetime.utcnow().isoformat()
    })

async def broadcast_low_stock_alert(product_data: Dict[str, Any]):
    """Broadcast low stock alert to all users"""
    await ws_manager.broadcast_to_all({
        "type": "low_stock_alert",
        "data": product_data,
        "timestamp": datetime.utcnow().isoformat()
    })

async def broadcast_dashboard_stats(stats_data: Dict[str, Any]):
    """Broadcast dashboard statistics update"""
    await ws_manager.broadcast_to_channel("dashboard", {
        "type": "dashboard_stats_update",
        "data": stats_data,
        "timestamp": datetime.utcnow().isoformat()
    })
"""
WebSocket API Endpoints

Real-time WebSocket connections for various channels
"""

import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional

from app.websocket.connection_manager import manager
from app.services.realtime_metrics_service import metrics_service
from app.api.auth import get_current_user_websocket

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/dashboard")
async def websocket_dashboard(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time dashboard updates
    
    Broadcasts:
    - Active dispatches count
    - Completed dispatches today
    - Pending orders count
    - Vehicles in transit
    - Temperature alerts
    - Fleet utilization
    
    Updates every 5 seconds
    """
    # Authenticate user (optional for dashboard)
    user_id = None
    if token:
        try:
            # You would validate token here
            # user = await get_current_user_websocket(token)
            # user_id = user.id
            pass
        except Exception as e:
            await websocket.close(code=1008, reason="Authentication failed")
            return
    
    connection_id = await manager.connect(websocket, "dashboard", user_id)
    
    try:
        while True:
            # Wait for messages from client with timeout
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=300.0)
                
                # Handle ping/pong
                if data.get("type") == "pong":
                    logger.debug(f"Received pong from {connection_id}")
                    continue
                
                # Echo message back (for testing)
                await manager.send_personal_message(
                    {"type": "echo", "data": data},
                    websocket
                )
            except asyncio.TimeoutError:
                # Keep connection alive even without messages
                await manager.send_personal_message(
                    {"type": "keepalive", "timestamp": datetime.utcnow().isoformat()},
                    websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        logger.info(f"Dashboard WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"Dashboard WebSocket error: {e}")
        manager.disconnect(connection_id)


@router.websocket("/dispatches")
async def websocket_dispatches(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time dispatch updates
    
    Broadcasts:
    - New dispatch created
    - Dispatch status changed
    - Dispatch assigned to driver
    - Dispatch completed
    """
    user_id = None
    if token:
        try:
            # Validate token
            pass
        except Exception:
            await websocket.close(code=1008, reason="Authentication failed")
            return
    
    connection_id = await manager.connect(websocket, "dispatches", user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "pong":
                continue
            
            # Handle specific dispatch subscription
            if data.get("type") == "subscribe" and "dispatch_id" in data:
                dispatch_id = data["dispatch_id"]
                logger.info(f"Client {connection_id} subscribed to dispatch {dispatch_id}")
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Dispatches WebSocket error: {e}")
        manager.disconnect(connection_id)


@router.websocket("/vehicles/{vehicle_id}")
async def websocket_vehicle(
    vehicle_id: int,
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time vehicle tracking
    
    Broadcasts for specific vehicle:
    - GPS location updates
    - Speed and heading
    - Temperature readings
    - Battery level
    - Door status
    - Alerts
    
    Updates every 5-10 seconds
    """
    user_id = None
    if token:
        try:
            # Validate token
            pass
        except Exception:
            await websocket.close(code=1008, reason="Authentication failed")
            return
    
    channel = f"vehicles/{vehicle_id}"
    connection_id = await manager.connect(websocket, channel, user_id)
    
    try:
        # Send initial vehicle data
        await manager.send_personal_message(
            {
                "type": "vehicle_info",
                "vehicle_id": vehicle_id,
                "message": f"Connected to vehicle {vehicle_id} tracking"
            },
            websocket
        )
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "pong":
                continue
            
            # Handle vehicle commands (future feature)
            if data.get("type") == "command":
                logger.info(f"Vehicle {vehicle_id} command: {data.get('command')}")
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Vehicle WebSocket error: {e}")
        manager.disconnect(connection_id)


@router.websocket("/drivers/{driver_id}")
async def websocket_driver(
    driver_id: int,
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for driver-specific updates
    
    Broadcasts for specific driver:
    - New dispatch assigned
    - Dispatch instructions
    - Route updates
    - Customer notes
    - Alerts
    """
    user_id = None
    if token:
        try:
            # Validate token and check if user is the driver
            pass
        except Exception:
            await websocket.close(code=1008, reason="Authentication failed")
            return
    
    channel = f"drivers/{driver_id}"
    connection_id = await manager.connect(websocket, channel, user_id)
    
    try:
        await manager.send_personal_message(
            {
                "type": "driver_info",
                "driver_id": driver_id,
                "message": f"Connected to driver {driver_id} channel"
            },
            websocket
        )
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "pong":
                continue
            
            # Handle driver status updates
            if data.get("type") == "status_update":
                logger.info(f"Driver {driver_id} status: {data.get('status')}")
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Driver WebSocket error: {e}")
        manager.disconnect(connection_id)


@router.websocket("/orders/{order_id}")
async def websocket_order(
    order_id: int,
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for order-specific updates
    
    Broadcasts for specific order:
    - Status changes
    - Dispatch assignment
    - Delivery updates
    - ETA changes
    """
    user_id = None
    if token:
        try:
            # Validate token
            pass
        except Exception:
            await websocket.close(code=1008, reason="Authentication failed")
            return
    
    channel = f"orders/{order_id}"
    connection_id = await manager.connect(websocket, channel, user_id)
    
    try:
        await manager.send_personal_message(
            {
                "type": "order_info",
                "order_id": order_id,
                "message": f"Connected to order {order_id} tracking"
            },
            websocket
        )
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "pong":
                continue
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Order WebSocket error: {e}")
        manager.disconnect(connection_id)


@router.websocket("/alerts")
async def websocket_alerts(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time alerts
    
    Broadcasts:
    - Temperature alerts
    - GPS accuracy warnings
    - Battery warnings
    - Door status alerts
    - Refrigeration failures
    - All critical system alerts
    """
    user_id = None
    if token:
        try:
            # Validate token
            pass
        except Exception:
            await websocket.close(code=1008, reason="Authentication failed")
            return
    
    connection_id = await manager.connect(websocket, "alerts", user_id)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message(
            {
                "type": "connected",
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            websocket
        )
        
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=300.0)
                
                if data.get("type") == "pong":
                    continue
                
                # Handle alert acknowledgment
                if data.get("type") == "acknowledge":
                    alert_id = data.get("alert_id")
                    logger.info(f"Alert {alert_id} acknowledged by {connection_id}")
            except asyncio.TimeoutError:
                await manager.send_personal_message(
                    {"type": "keepalive", "timestamp": datetime.utcnow().isoformat()},
                    websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Alerts WebSocket error: {e}")
        manager.disconnect(connection_id)


@router.websocket("/analytics")
async def websocket_analytics(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time analytics updates
    
    Broadcasts:
    - Real-time KPI updates
    - Performance metrics
    - Fleet utilization
    - Cost metrics
    """
    user_id = None
    if token:
        try:
            # Validate token
            pass
        except Exception:
            await websocket.close(code=1008, reason="Authentication failed")
            return
    
    connection_id = await manager.connect(websocket, "analytics", user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "pong":
                continue
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"Analytics WebSocket error: {e}")
        manager.disconnect(connection_id)


@router.get("/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics
    
    Returns:
    - Total connections
    - Connections per channel
    - Active users
    """
    return manager.get_stats()

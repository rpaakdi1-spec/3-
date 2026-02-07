"""
Real-time Metrics Broadcast Service

Collects and broadcasts real-time metrics to WebSocket clients
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.websocket.connection_manager import manager
from app.core.database import get_db

from app.models.vehicle import Vehicle, VehicleStatus
from app.models.dispatch import Dispatch
from app.models.order import Order
logger = logging.getLogger(__name__)


class RealtimeMetricsService:
    """
    Real-time Metrics Broadcasting Service
    
    Periodically collects system metrics and broadcasts them
    to connected WebSocket clients.
    """
    
    def __init__(self):
        self.broadcast_interval = 5  # seconds
        self.broadcast_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    async def start(self):
        """Start broadcasting metrics"""
        if self.is_running:
            logger.warning("⚠️  Metrics broadcast already running")
            return
        
        self.is_running = True
        self.broadcast_task = asyncio.create_task(self._broadcast_loop())
        logger.info("✅ Real-time metrics broadcast started")
    
    async def stop(self):
        """Stop broadcasting metrics"""
        self.is_running = False
        
        if self.broadcast_task:
            self.broadcast_task.cancel()
            try:
                await self.broadcast_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 Real-time metrics broadcast stopped")
    
    async def _broadcast_loop(self):
        """Main broadcast loop"""
        try:
            while self.is_running:
                try:
                    # Collect and broadcast dashboard metrics
                    await self._broadcast_dashboard_metrics()
                    
                    # Collect and broadcast vehicle locations (if any active)
                    await self._broadcast_vehicle_updates()
                    
                    # Collect and broadcast alerts
                    await self._broadcast_alerts()
                    
                except Exception as e:
                    logger.error(f"❌ Error in broadcast loop: {e}")
                
                # Wait for next interval
                await asyncio.sleep(self.broadcast_interval)
        except asyncio.CancelledError:
            logger.info("🛑 Broadcast loop cancelled")
    
    async def _broadcast_dashboard_metrics(self):
        """Broadcast dashboard metrics to /ws/dashboard channel"""
        try:
            # Use next() to get single DB session from generator
            db_gen = get_db()
            db = next(db_gen)
            try:
                metrics = self._collect_dashboard_metrics(db)
                
                await manager.broadcast_to_channel(
                    "dashboard",
                    {
                        "type": "dashboard_update",
                        "data": metrics,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                # Also publish to Redis for multi-server setup
                await manager.publish_to_redis("dashboard", {
                    "type": "dashboard_update",
                    "data": metrics,
                    "timestamp": datetime.utcnow().isoformat()
                })
            finally:
                # Close the session
                try:
                    next(db_gen)
                except StopIteration:
                    pass
        except Exception as e:
            logger.error(f"❌ Error broadcasting dashboard metrics: {str(e)}")
    
    def _collect_dashboard_metrics(self, db: Session) -> dict:
        """Collect dashboard metrics from database"""
        from app.models.dispatch import Dispatch, DispatchStatus
        from app.models.order import Order, OrderStatus
        from app.models.vehicle import Vehicle
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Active dispatches
        active_dispatches_query = select(func.count(Dispatch.id)).where(
            Dispatch.status.in_([
                DispatchStatus.ASSIGNED,
                DispatchStatus.IN_PROGRESS
            ])
        )
        active_dispatches = db.scalar(active_dispatches_query) or 0
        
        # Completed today
        completed_today_query = select(func.count(Dispatch.id)).where(
            and_(
                Dispatch.status == DispatchStatus.COMPLETED,
                Dispatch.completed_at >= today_start
            )
        )
        completed_today = db.scalar(completed_today_query) or 0
        
        # Pending orders
        pending_orders_query = select(func.count(Order.id)).where(
            Order.status == OrderStatus.PENDING
        )
        pending_orders = db.scalar(pending_orders_query) or 0
        
        # Vehicles in transit
        vehicles_in_transit_query = select(func.count(Vehicle.id)).where(
            Vehicle.status == VehicleStatus.IN_USE
        )
        vehicles_in_transit = db.scalar(vehicles_in_transit_query) or 0
        
        # Temperature alerts (mock data for now)
        temperature_alerts = 0
        
        return {
            "active_dispatches": active_dispatches,
            "completed_today": completed_today,
            "pending_orders": pending_orders,
            "vehicles_in_transit": vehicles_in_transit,
            "temperature_alerts": temperature_alerts,
            "timestamp": now.isoformat()
        }
    
    async def _broadcast_vehicle_updates(self):
        """Broadcast vehicle location updates"""
        try:
            # Use next() to get single DB session from generator
            db_gen = get_db()
            db = next(db_gen)
            try:
                # Get vehicles that have active tracking
                from app.models.vehicle import Vehicle
                
                vehicles_query = select(Vehicle).where(
                    Vehicle.status == VehicleStatus.IN_USE
                ).limit(50)
                
                result = db.execute(vehicles_query)
                vehicles = list(result.scalars().all())  # Convert to list to avoid ChunkedIteratorResult error
                
                for vehicle in vehicles:
                    # Broadcast to vehicle-specific channel
                    vehicle_data = {
                        "type": "vehicle_location",
                        "vehicle_id": vehicle.id,
                        "license_plate": vehicle.license_plate,
                        "status": vehicle.status,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await manager.broadcast_to_channel(
                        f"vehicles/{vehicle.id}",
                        vehicle_data
                    )
            finally:
                # Close the session
                try:
                    next(db_gen)
                except StopIteration:
                    pass
        except Exception as e:
            logger.error(f"❌ Error broadcasting vehicle updates: {str(e)}")
    
    async def _broadcast_alerts(self):
        """Broadcast new alerts"""
        try:
            # This would query recent alerts from database
            # For now, skip if no active connections on alerts channel
            if "alerts" not in manager.active_connections:
                return
            
            # Mock alert data
            # In production, query from TemperatureAlert or other alert tables
            pass
        except Exception as e:
            logger.error(f"❌ Error broadcasting alerts: {e}")
    
    async def broadcast_dispatch_update(self, dispatch_id: int, dispatch_data: dict):
        """
        Broadcast dispatch update
        
        Args:
            dispatch_id: Dispatch ID
            dispatch_data: Dispatch data dictionary
        """
        message = {
            "type": "dispatch_update",
            "dispatch_id": dispatch_id,
            "data": dispatch_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to dispatches channel
        await manager.broadcast_to_channel("dispatches", message)
        
        # Publish to Redis
        await manager.publish_to_redis("dispatches", message)
    
    async def broadcast_order_update(self, order_id: int, order_data: dict):
        """
        Broadcast order update
        
        Args:
            order_id: Order ID
            order_data: Order data dictionary
        """
        message = {
            "type": "order_update",
            "order_id": order_id,
            "data": order_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to orders channel
        await manager.broadcast_to_channel(f"orders/{order_id}", message)
        
        # Also broadcast to general orders channel
        await manager.broadcast_to_channel("orders", message)
        
        # Publish to Redis
        await manager.publish_to_redis("orders", message)
    
    async def broadcast_vehicle_location(
        self,
        vehicle_id: int,
        latitude: float,
        longitude: float,
        speed: float = 0.0,
        heading: float = 0.0,
        temperature: Optional[float] = None
    ):
        """
        Broadcast vehicle location update
        
        Args:
            vehicle_id: Vehicle ID
            latitude: GPS latitude
            longitude: GPS longitude
            speed: Vehicle speed (km/h)
            heading: Heading direction (0-360)
            temperature: Cargo temperature (optional)
        """
        message = {
            "type": "vehicle_location",
            "vehicle_id": vehicle_id,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "speed": speed,
                "heading": heading,
                "temperature": temperature
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to vehicle-specific channel
        await manager.broadcast_to_channel(f"vehicles/{vehicle_id}", message)
        
        # Publish to Redis
        await manager.publish_to_redis(f"vehicles/{vehicle_id}", message)
    
    async def broadcast_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        entity_type: str,
        entity_id: int,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Broadcast alert
        
        Args:
            alert_type: Alert type (temperature, gps, battery, etc.)
            severity: Alert severity (info, warning, critical)
            message: Alert message
            entity_type: Entity type (vehicle, dispatch, order)
            entity_id: Entity ID
            data: Additional data (optional)
        """
        alert_message = {
            "type": "alert",
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to alerts channel
        await manager.broadcast_to_channel("alerts", alert_message)
        
        # Publish to Redis
        await manager.publish_to_redis("alerts", alert_message)
    
    async def broadcast_analytics_update(self, analytics_data: dict):
        """
        Broadcast analytics update
        
        Args:
            analytics_data: Analytics data dictionary
        """
        message = {
            "type": "analytics_update",
            "data": analytics_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to analytics channel
        await manager.broadcast_to_channel("analytics", message)
        
        # Publish to Redis
        await manager.publish_to_redis("analytics", message)


# Global instance
metrics_service = RealtimeMetricsService()

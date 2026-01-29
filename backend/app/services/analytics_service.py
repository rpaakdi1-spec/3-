"""
Analytics service for dispatch history analysis
"""
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from app.models import Dispatch, Order, Vehicle, Client, DispatchRoute
from app.models.dispatch import DispatchStatus
from app.models.order import OrderStatus
from app.schemas.analytics import (
    DispatchStatistics,
    PeriodStatistics,
    VehiclePerformance,
    VehicleAnalytics,
    ClientDeliveryStats,
    ClientAnalytics,
    RegionDistribution,
    DashboardSummary
)
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """배차 이력 분석 서비스"""
    
    def get_dispatch_statistics(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        period: str = "daily"
    ) -> PeriodStatistics:
        """
        기간별 배차 통계 조회
        
        Args:
            db: Database session
            start_date: 시작 날짜
            end_date: 종료 날짜
            period: 집계 단위 (daily/weekly/monthly)
        """
        logger.info(f"Getting dispatch statistics: {start_date} to {end_date}, period={period}")
        
        statistics = []
        
        if period == "daily":
            # 일별 통계
            current_date = start_date
            while current_date <= end_date:
                daily_stats = self._get_daily_statistics(db, current_date)
                statistics.append(daily_stats)
                current_date += timedelta(days=1)
        
        elif period == "weekly":
            # 주별 통계 (월요일 기준)
            current_date = start_date - timedelta(days=start_date.weekday())
            while current_date <= end_date:
                week_end = current_date + timedelta(days=6)
                weekly_stats = self._get_period_statistics(db, current_date, week_end)
                statistics.append(weekly_stats)
                current_date += timedelta(weeks=1)
        
        elif period == "monthly":
            # 월별 통계
            current_date = start_date.replace(day=1)
            while current_date <= end_date:
                # Get last day of month
                if current_date.month == 12:
                    month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
                
                monthly_stats = self._get_period_statistics(db, current_date, month_end)
                statistics.append(monthly_stats)
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        # Calculate summary
        summary = self._calculate_summary(statistics)
        
        return PeriodStatistics(
            period=period,
            start_date=start_date,
            end_date=end_date,
            statistics=statistics,
            summary=summary
        )
    
    def _get_daily_statistics(self, db: Session, target_date: date) -> DispatchStatistics:
        """일별 통계 조회"""
        # Get dispatches for the day
        dispatches = db.query(Dispatch).filter(
            Dispatch.dispatch_date == target_date
        ).all()
        
        if not dispatches:
            return DispatchStatistics(
                date=target_date,
                total_dispatches=0,
                total_orders=0,
                total_pallets=0,
                total_weight_kg=0.0,
                total_distance_km=0.0,
                unique_vehicles=0,
                unique_clients=0,
                avg_pallets_per_dispatch=0.0
            )
        
        # Calculate statistics
        total_dispatches = len(dispatches)
        total_orders = sum(d.total_orders for d in dispatches)
        total_pallets = sum(d.total_pallets for d in dispatches)
        total_weight = sum(d.total_weight_kg for d in dispatches)
        total_distance = sum(d.initial_distance_km or 0.0 for d in dispatches)
        unique_vehicles = len(set(d.vehicle_id for d in dispatches))
        
        # Get unique clients from routes
        route_client_ids = set()
        for dispatch in dispatches:
            for route in dispatch.routes:
                if route.order_id:
                    order = db.query(Order).filter(Order.id == route.order_id).first()
                    if order:
                        if order.pickup_client_id:
                            route_client_ids.add(order.pickup_client_id)
                        if order.delivery_client_id:
                            route_client_ids.add(order.delivery_client_id)
        
        unique_clients = len(route_client_ids)
        avg_pallets = total_pallets / total_dispatches if total_dispatches > 0 else 0.0
        
        return DispatchStatistics(
            date=target_date,
            total_dispatches=total_dispatches,
            total_orders=total_orders,
            total_pallets=total_pallets,
            total_weight_kg=total_weight,
            total_distance_km=total_distance,
            unique_vehicles=unique_vehicles,
            unique_clients=unique_clients,
            avg_pallets_per_dispatch=avg_pallets
        )
    
    def _get_period_statistics(self, db: Session, start_date: date, end_date: date) -> DispatchStatistics:
        """기간 통계 조회"""
        dispatches = db.query(Dispatch).filter(
            and_(
                Dispatch.dispatch_date >= start_date,
                Dispatch.dispatch_date <= end_date
            )
        ).all()
        
        if not dispatches:
            return DispatchStatistics(
                date=start_date,
                total_dispatches=0,
                total_orders=0,
                total_pallets=0,
                total_weight_kg=0.0,
                total_distance_km=0.0,
                unique_vehicles=0,
                unique_clients=0,
                avg_pallets_per_dispatch=0.0
            )
        
        total_dispatches = len(dispatches)
        total_orders = sum(d.total_orders for d in dispatches)
        total_pallets = sum(d.total_pallets for d in dispatches)
        total_weight = sum(d.total_weight_kg for d in dispatches)
        total_distance = sum(d.initial_distance_km or 0.0 for d in dispatches)
        unique_vehicles = len(set(d.vehicle_id for d in dispatches))
        
        # Get unique clients
        route_client_ids = set()
        for dispatch in dispatches:
            for route in dispatch.routes:
                if route.order_id:
                    order = db.query(Order).filter(Order.id == route.order_id).first()
                    if order:
                        if order.pickup_client_id:
                            route_client_ids.add(order.pickup_client_id)
                        if order.delivery_client_id:
                            route_client_ids.add(order.delivery_client_id)
        
        unique_clients = len(route_client_ids)
        avg_pallets = total_pallets / total_dispatches if total_dispatches > 0 else 0.0
        
        return DispatchStatistics(
            date=start_date,
            total_dispatches=total_dispatches,
            total_orders=total_orders,
            total_pallets=total_pallets,
            total_weight_kg=total_weight,
            total_distance_km=total_distance,
            unique_vehicles=unique_vehicles,
            unique_clients=unique_clients,
            avg_pallets_per_dispatch=avg_pallets
        )
    
    def _calculate_summary(self, statistics: List[DispatchStatistics]) -> Dict[str, Any]:
        """통계 요약 계산"""
        if not statistics:
            return {
                "total_dispatches": 0,
                "total_orders": 0,
                "total_pallets": 0,
                "total_distance_km": 0.0,
                "avg_dispatches_per_day": 0.0
            }
        
        total_dispatches = sum(s.total_dispatches for s in statistics)
        total_orders = sum(s.total_orders for s in statistics)
        total_pallets = sum(s.total_pallets for s in statistics)
        total_distance = sum(s.total_distance_km or 0.0 for s in statistics)
        
        days = len(statistics)
        avg_dispatches = total_dispatches / days if days > 0 else 0.0
        
        return {
            "total_dispatches": total_dispatches,
            "total_orders": total_orders,
            "total_pallets": total_pallets,
            "total_distance_km": total_distance,
            "avg_dispatches_per_day": avg_dispatches
        }
    
    def get_vehicle_analytics(
        self,
        db: Session,
        start_date: date,
        end_date: date
    ) -> VehicleAnalytics:
        """
        차량별 운행 분석
        
        Args:
            db: Database session
            start_date: 시작 날짜
            end_date: 종료 날짜
        """
        logger.info(f"Getting vehicle analytics: {start_date} to {end_date}")
        
        # Get all dispatches in period
        dispatches = db.query(Dispatch).filter(
            and_(
                Dispatch.dispatch_date >= start_date,
                Dispatch.dispatch_date <= end_date
            )
        ).all()
        
        # Group by vehicle
        vehicle_data = {}
        for dispatch in dispatches:
            vehicle_id = dispatch.vehicle_id
            if vehicle_id not in vehicle_data:
                vehicle_data[vehicle_id] = {
                    'vehicle': dispatch.vehicle,
                    'dispatches': [],
                    'total_orders': 0,
                    'total_pallets': 0,
                    'total_weight': 0.0,
                    'total_distance': 0.0
                }
            
            vehicle_data[vehicle_id]['dispatches'].append(dispatch)
            vehicle_data[vehicle_id]['total_orders'] += dispatch.total_orders
            vehicle_data[vehicle_id]['total_pallets'] += dispatch.total_pallets
            vehicle_data[vehicle_id]['total_weight'] += dispatch.total_weight_kg
            vehicle_data[vehicle_id]['total_distance'] += dispatch.initial_distance_km or 0.0
        
        # Build vehicle performance list
        vehicles = []
        for vehicle_id, data in vehicle_data.items():
            vehicle = data['vehicle']
            total_dispatches = len(data['dispatches'])
            total_distance = data['total_distance']
            total_pallets = data['total_pallets']
            total_weight = data['total_weight']
            
            avg_pallets = total_pallets / total_dispatches if total_dispatches > 0 else 0.0
            avg_distance = total_distance / total_dispatches if total_dispatches > 0 else 0.0
            
            # Calculate capacity utilization (assuming max_pallets from vehicle)
            max_pallets = vehicle.max_pallets if hasattr(vehicle, 'max_pallets') and vehicle.max_pallets else 20
            capacity_utilization = (avg_pallets / max_pallets * 100) if max_pallets > 0 else 0.0
            
            vehicles.append(VehiclePerformance(
                vehicle_id=vehicle.id,
                vehicle_code=vehicle.code,
                vehicle_type=vehicle.vehicle_type.value if hasattr(vehicle.vehicle_type, 'value') else str(vehicle.vehicle_type),
                total_dispatches=total_dispatches,
                total_distance_km=total_distance,
                total_orders=data['total_orders'],
                total_pallets=total_pallets,
                total_weight_kg=total_weight,
                avg_pallets_per_dispatch=avg_pallets,
                avg_distance_per_dispatch=avg_distance,
                capacity_utilization=capacity_utilization
            ))
        
        # Sort by total dispatches (descending)
        vehicles.sort(key=lambda x: x.total_dispatches, reverse=True)
        
        # Calculate summary
        summary = {
            "total_vehicles": len(vehicles),
            "total_dispatches": sum(v.total_dispatches for v in vehicles),
            "total_distance_km": sum(v.total_distance_km for v in vehicles),
            "avg_capacity_utilization": sum(v.capacity_utilization for v in vehicles) / len(vehicles) if vehicles else 0.0
        }
        
        return VehicleAnalytics(
            period=f"{start_date} to {end_date}",
            start_date=start_date,
            end_date=end_date,
            vehicles=vehicles,
            summary=summary
        )
    
    def get_client_analytics(
        self,
        db: Session,
        start_date: date,
        end_date: date
    ) -> ClientAnalytics:
        """
        거래처별 배송 통계
        
        Args:
            db: Database session
            start_date: 시작 날짜
            end_date: 종료 날짜
        """
        logger.info(f"Getting client analytics: {start_date} to {end_date}")
        
        # Get all orders in period
        orders = db.query(Order).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date
            )
        ).all()
        
        # Group by delivery client
        client_data = {}
        for order in orders:
            if not order.delivery_client_id:
                continue
            
            client_id = order.delivery_client_id
            if client_id not in client_data:
                client = db.query(Client).filter(Client.id == client_id).first()
                if not client:
                    continue
                
                client_data[client_id] = {
                    'client': client,
                    'orders': [],
                    'total_pallets': 0,
                    'total_weight': 0.0
                }
            
            client_data[client_id]['orders'].append(order)
            client_data[client_id]['total_pallets'] += order.pallet_count
            client_data[client_id]['total_weight'] += order.weight_kg
        
        # Build client stats list
        clients = []
        total_days = (end_date - start_date).days + 1
        months = total_days / 30.0  # Approximate months
        
        for client_id, data in client_data.items():
            client = data['client']
            total_orders = len(data['orders'])
            total_pallets = data['total_pallets']
            total_weight = data['total_weight']
            
            delivery_frequency = total_orders / months if months > 0 else total_orders
            avg_pallets = total_pallets / total_orders if total_orders > 0 else 0.0
            
            # Extract region from address (simplified)
            region = None
            if client.delivery_address:
                # Extract first part of address (시/도)
                parts = client.delivery_address.split()
                if parts:
                    region = parts[0]
            
            clients.append(ClientDeliveryStats(
                client_id=client.id,
                client_code=client.code,
                client_name=client.name,
                client_type=client.client_type.value if hasattr(client.client_type, 'value') else str(client.client_type),
                total_orders=total_orders,
                total_pallets=total_pallets,
                total_weight_kg=total_weight,
                delivery_frequency=delivery_frequency,
                avg_pallets_per_order=avg_pallets,
                region=region
            ))
        
        # Sort by total orders (descending)
        clients.sort(key=lambda x: x.total_orders, reverse=True)
        
        # Calculate summary
        summary = {
            "total_clients": len(clients),
            "total_orders": sum(c.total_orders for c in clients),
            "total_pallets": sum(c.total_pallets for c in clients),
            "avg_delivery_frequency": sum(c.delivery_frequency for c in clients) / len(clients) if clients else 0.0
        }
        
        return ClientAnalytics(
            period=f"{start_date} to {end_date}",
            start_date=start_date,
            end_date=end_date,
            clients=clients,
            summary=summary
        )
    
    def get_dashboard_summary(self, db: Session, target_date: Optional[date] = None) -> DashboardSummary:
        """
        대시보드 요약 통계
        
        Args:
            db: Database session
            target_date: 기준 날짜 (기본값: 오늘)
        """
        if target_date is None:
            target_date = date.today()
        
        logger.info(f"Getting dashboard summary for {target_date}")
        
        # Today stats
        today_dispatches = db.query(func.count(Dispatch.id)).filter(
            Dispatch.dispatch_date == target_date
        ).scalar() or 0
        
        today_orders_sum = db.query(func.sum(Dispatch.total_orders)).filter(
            Dispatch.dispatch_date == target_date
        ).scalar() or 0
        
        today_pallets_sum = db.query(func.sum(Dispatch.total_pallets)).filter(
            Dispatch.dispatch_date == target_date
        ).scalar() or 0
        
        # This week stats (Monday to Sunday)
        week_start = target_date - timedelta(days=target_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        week_dispatches = db.query(func.count(Dispatch.id)).filter(
            and_(
                Dispatch.dispatch_date >= week_start,
                Dispatch.dispatch_date <= week_end
            )
        ).scalar() or 0
        
        week_orders = db.query(func.sum(Dispatch.total_orders)).filter(
            and_(
                Dispatch.dispatch_date >= week_start,
                Dispatch.dispatch_date <= week_end
            )
        ).scalar() or 0
        
        week_distance = db.query(func.sum(Dispatch.initial_distance_km)).filter(
            and_(
                Dispatch.dispatch_date >= week_start,
                Dispatch.dispatch_date <= week_end
            )
        ).scalar() or 0.0
        
        # This month stats
        month_start = target_date.replace(day=1)
        
        month_dispatches = db.query(func.count(Dispatch.id)).filter(
            extract('year', Dispatch.dispatch_date) == target_date.year,
            extract('month', Dispatch.dispatch_date) == target_date.month
        ).scalar() or 0
        
        month_orders = db.query(func.sum(Dispatch.total_orders)).filter(
            extract('year', Dispatch.dispatch_date) == target_date.year,
            extract('month', Dispatch.dispatch_date) == target_date.month
        ).scalar() or 0
        
        month_pallets = db.query(func.sum(Dispatch.total_pallets)).filter(
            extract('year', Dispatch.dispatch_date) == target_date.year,
            extract('month', Dispatch.dispatch_date) == target_date.month
        ).scalar() or 0
        
        # Vehicle stats
        active_vehicles = db.query(func.count(Vehicle.id)).filter(
            Vehicle.is_active == True
        ).scalar() or 0
        
        total_vehicles = db.query(func.count(Vehicle.id)).scalar() or 0
        
        # Client stats
        active_clients = db.query(func.count(Client.id)).filter(
            Client.is_active == True
        ).scalar() or 0
        
        total_clients = db.query(func.count(Client.id)).scalar() or 0
        
        # Last month for growth rate
        if target_date.month == 1:
            last_month_start = date(target_date.year - 1, 12, 1)
        else:
            last_month_start = date(target_date.year, target_date.month - 1, 1)
        
        # Get last day of last month
        if last_month_start.month == 12:
            last_month_end = date(last_month_start.year + 1, 1, 1) - timedelta(days=1)
        else:
            last_month_end = date(last_month_start.year, last_month_start.month + 1, 1) - timedelta(days=1)
        
        last_month_dispatches = db.query(func.count(Dispatch.id)).filter(
            and_(
                Dispatch.dispatch_date >= last_month_start,
                Dispatch.dispatch_date <= last_month_end
            )
        ).scalar() or 0
        
        last_month_orders = db.query(func.sum(Dispatch.total_orders)).filter(
            and_(
                Dispatch.dispatch_date >= last_month_start,
                Dispatch.dispatch_date <= last_month_end
            )
        ).scalar() or 0
        
        # Calculate growth rates
        dispatch_growth = ((month_dispatches - last_month_dispatches) / last_month_dispatches * 100) if last_month_dispatches > 0 else 0.0
        order_growth = ((month_orders - last_month_orders) / last_month_orders * 100) if last_month_orders > 0 else 0.0
        
        return DashboardSummary(
            today=target_date,
            today_dispatches=today_dispatches,
            today_orders=today_orders_sum,
            today_pallets=today_pallets_sum,
            week_dispatches=week_dispatches,
            week_orders=week_orders,
            week_distance_km=week_distance,
            month_dispatches=month_dispatches,
            month_orders=month_orders,
            month_pallets=month_pallets,
            active_vehicles=active_vehicles,
            total_vehicles=total_vehicles,
            active_clients=active_clients,
            total_clients=total_clients,
            dispatch_growth_rate=dispatch_growth,
            order_growth_rate=order_growth
        )


# Singleton instance
analytics_service = AnalyticsService()

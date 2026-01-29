"""
모니터링 서비스

시스템 상태 모니터링 및 메트릭 수집:
1. 시스템 헬스 체크
2. 데이터베이스 상태
3. API 응답 시간
4. 메모리/CPU 사용률
5. 에러율 추적
6. 활성 사용자 수
"""

import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from loguru import logger

from app.models.order import Order, OrderStatus
from app.models.dispatch import Dispatch, DispatchStatus
from app.models.vehicle import Vehicle
from app.models.driver import Driver


class MonitoringService:
    """시스템 모니터링 서비스"""
    
    @staticmethod
    def get_system_health(db: Session) -> Dict[str, Any]:
        """
        전체 시스템 헬스 체크
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            Dict: 시스템 상태 정보
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # 1. 데이터베이스 체크
        db_health = MonitoringService._check_database(db)
        health_status["checks"]["database"] = db_health
        
        # 2. 시스템 리소스 체크
        resource_health = MonitoringService._check_system_resources()
        health_status["checks"]["system_resources"] = resource_health
        
        # 3. 애플리케이션 상태 체크
        app_health = MonitoringService._check_application_status(db)
        health_status["checks"]["application"] = app_health
        
        # 전체 상태 결정
        all_checks = [db_health, resource_health, app_health]
        if any(check["status"] == "unhealthy" for check in all_checks):
            health_status["status"] = "unhealthy"
        elif any(check["status"] == "degraded" for check in all_checks):
            health_status["status"] = "degraded"
        
        return health_status
    
    @staticmethod
    def _check_database(db: Session) -> Dict[str, Any]:
        """데이터베이스 연결 및 성능 체크"""
        try:
            start_time = time.time()
            
            # 간단한 쿼리로 연결 테스트
            db.execute(text("SELECT 1"))
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            # 응답 시간 기반 상태 판단
            if response_time < 100:
                status = "healthy"
            elif response_time < 500:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "response_time_ms": round(response_time, 2),
                "message": "Database connection OK"
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "response_time_ms": None,
                "error": str(e),
                "message": "Database connection failed"
            }
    
    @staticmethod
    def _check_system_resources() -> Dict[str, Any]:
        """시스템 리소스 사용률 체크"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # 상태 판단
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                status = "unhealthy"
            elif cpu_percent > 70 or memory_percent > 70 or disk_percent > 80:
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory_percent, 1),
                "disk_percent": round(disk_percent, 1),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
            
        except Exception as e:
            logger.error(f"System resources check failed: {e}")
            return {
                "status": "unknown",
                "error": str(e)
            }
    
    @staticmethod
    def _check_application_status(db: Session) -> Dict[str, Any]:
        """애플리케이션 상태 체크"""
        try:
            # 최근 24시간 내 주문 수
            yesterday = datetime.now() - timedelta(days=1)
            recent_orders = db.query(Order).filter(
                Order.created_at >= yesterday
            ).count()
            
            # 진행 중인 배차 수
            active_dispatches = db.query(Dispatch).filter(
                Dispatch.status.in_([DispatchStatus.CONFIRMED, DispatchStatus.IN_PROGRESS])
            ).count()
            
            # 활성 차량 수
            active_vehicles = db.query(Vehicle).filter(
                Vehicle.status == "available"
            ).count()
            
            return {
                "status": "healthy",
                "recent_orders_24h": recent_orders,
                "active_dispatches": active_dispatches,
                "active_vehicles": active_vehicles
            }
            
        except Exception as e:
            logger.error(f"Application status check failed: {e}")
            return {
                "status": "degraded",
                "error": str(e)
            }
    
    @staticmethod
    def get_metrics(db: Session, period_hours: int = 24) -> Dict[str, Any]:
        """
        시스템 메트릭 수집
        
        Args:
            db: 데이터베이스 세션
            period_hours: 수집 기간 (시간)
            
        Returns:
            Dict: 메트릭 데이터
        """
        since = datetime.now() - timedelta(hours=period_hours)
        
        # 주문 메트릭
        order_metrics = MonitoringService._get_order_metrics(db, since)
        
        # 배차 메트릭
        dispatch_metrics = MonitoringService._get_dispatch_metrics(db, since)
        
        # 차량 메트릭
        vehicle_metrics = MonitoringService._get_vehicle_metrics(db, since)
        
        # 시스템 메트릭
        system_metrics = MonitoringService._get_system_metrics()
        
        return {
            "period_hours": period_hours,
            "timestamp": datetime.now().isoformat(),
            "orders": order_metrics,
            "dispatches": dispatch_metrics,
            "vehicles": vehicle_metrics,
            "system": system_metrics
        }
    
    @staticmethod
    def _get_order_metrics(db: Session, since: datetime) -> Dict[str, Any]:
        """주문 관련 메트릭"""
        # 전체 주문 수
        total_orders = db.query(Order).filter(Order.created_at >= since).count()
        
        # 상태별 주문 수
        status_counts = {}
        for status in OrderStatus:
            count = db.query(Order).filter(
                Order.created_at >= since,
                Order.status == status
            ).count()
            status_counts[status.value] = count
        
        # 평균 주문 처리 시간
        completed_orders = db.query(Order).filter(
            Order.created_at >= since,
            Order.status == OrderStatus.DELIVERED
        ).all()
        
        avg_processing_time = None
        if completed_orders:
            processing_times = []
            for order in completed_orders:
                if order.updated_at and order.created_at:
                    delta = order.updated_at - order.created_at
                    processing_times.append(delta.total_seconds() / 3600)  # hours
            
            if processing_times:
                avg_processing_time = round(sum(processing_times) / len(processing_times), 2)
        
        return {
            "total": total_orders,
            "by_status": status_counts,
            "avg_processing_hours": avg_processing_time,
            "completion_rate": round((status_counts.get("배송완료", 0) / total_orders * 100), 1) if total_orders > 0 else 0
        }
    
    @staticmethod
    def _get_dispatch_metrics(db: Session, since: datetime) -> Dict[str, Any]:
        """배차 관련 메트릭"""
        # 전체 배차 수
        total_dispatches = db.query(Dispatch).filter(Dispatch.created_at >= since).count()
        
        # 상태별 배차 수
        status_counts = {}
        for status in DispatchStatus:
            count = db.query(Dispatch).filter(
                Dispatch.created_at >= since,
                Dispatch.status == status
            ).count()
            status_counts[status.value] = count
        
        # 평균 배차 거리
        dispatches = db.query(Dispatch).filter(
            Dispatch.created_at >= since,
            Dispatch.total_distance_km.isnot(None)
        ).all()
        
        avg_distance = None
        if dispatches:
            distances = [d.total_distance_km for d in dispatches if d.total_distance_km]
            if distances:
                avg_distance = round(sum(distances) / len(distances), 2)
        
        return {
            "total": total_dispatches,
            "by_status": status_counts,
            "avg_distance_km": avg_distance
        }
    
    @staticmethod
    def _get_vehicle_metrics(db: Session, since: datetime) -> Dict[str, Any]:
        """차량 관련 메트릭"""
        # 전체 차량 수
        total_vehicles = db.query(Vehicle).count()
        
        # 상태별 차량 수
        available_vehicles = db.query(Vehicle).filter(Vehicle.status == "available").count()
        in_use_vehicles = db.query(Vehicle).filter(Vehicle.status == "in_use").count()
        maintenance_vehicles = db.query(Vehicle).filter(Vehicle.status == "maintenance").count()
        
        # 차량 활용률
        utilization_rate = round((in_use_vehicles / total_vehicles * 100), 1) if total_vehicles > 0 else 0
        
        return {
            "total": total_vehicles,
            "available": available_vehicles,
            "in_use": in_use_vehicles,
            "maintenance": maintenance_vehicles,
            "utilization_rate": utilization_rate
        }
    
    @staticmethod
    def _get_system_metrics() -> Dict[str, Any]:
        """시스템 리소스 메트릭"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # 메모리
        memory = psutil.virtual_memory()
        
        # 디스크
        disk = psutil.disk_usage('/')
        
        # 네트워크
        net_io = psutil.net_io_counters()
        
        return {
            "cpu": {
                "percent": round(cpu_percent, 1),
                "count": cpu_count
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent": round(memory.percent, 1)
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": round(disk.percent, 1)
            },
            "network": {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2)
            }
        }
    
    @staticmethod
    def get_alerts(db: Session) -> List[Dict[str, Any]]:
        """
        시스템 알림 조회
        
        이상 상황 자동 감지 및 알림 생성
        
        Returns:
            List[Dict]: 알림 목록
        """
        alerts = []
        
        # 1. 시스템 리소스 알림
        resource_alerts = MonitoringService._check_resource_alerts()
        alerts.extend(resource_alerts)
        
        # 2. 데이터베이스 알림
        db_alerts = MonitoringService._check_database_alerts(db)
        alerts.extend(db_alerts)
        
        # 3. 비즈니스 로직 알림
        business_alerts = MonitoringService._check_business_alerts(db)
        alerts.extend(business_alerts)
        
        return alerts
    
    @staticmethod
    def _check_resource_alerts() -> List[Dict[str, Any]]:
        """시스템 리소스 알림 체크"""
        alerts = []
        
        # CPU 체크
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            alerts.append({
                "level": "critical",
                "category": "system",
                "title": "CPU 사용률 높음",
                "message": f"CPU 사용률이 {cpu_percent}%로 높습니다",
                "timestamp": datetime.now().isoformat()
            })
        elif cpu_percent > 70:
            alerts.append({
                "level": "warning",
                "category": "system",
                "title": "CPU 사용률 주의",
                "message": f"CPU 사용률이 {cpu_percent}%입니다",
                "timestamp": datetime.now().isoformat()
            })
        
        # 메모리 체크
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            alerts.append({
                "level": "critical",
                "category": "system",
                "title": "메모리 부족",
                "message": f"메모리 사용률이 {memory.percent}%로 높습니다",
                "timestamp": datetime.now().isoformat()
            })
        elif memory.percent > 70:
            alerts.append({
                "level": "warning",
                "category": "system",
                "title": "메모리 사용률 주의",
                "message": f"메모리 사용률이 {memory.percent}%입니다",
                "timestamp": datetime.now().isoformat()
            })
        
        # 디스크 체크
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            alerts.append({
                "level": "critical",
                "category": "system",
                "title": "디스크 공간 부족",
                "message": f"디스크 사용률이 {disk.percent}%로 높습니다",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    @staticmethod
    def _check_database_alerts(db: Session) -> List[Dict[str, Any]]:
        """데이터베이스 관련 알림 체크"""
        alerts = []
        
        try:
            start_time = time.time()
            db.execute(text("SELECT 1"))
            response_time = (time.time() - start_time) * 1000
            
            if response_time > 1000:
                alerts.append({
                    "level": "critical",
                    "category": "database",
                    "title": "데이터베이스 응답 느림",
                    "message": f"데이터베이스 응답 시간이 {round(response_time, 0)}ms입니다",
                    "timestamp": datetime.now().isoformat()
                })
            elif response_time > 500:
                alerts.append({
                    "level": "warning",
                    "category": "database",
                    "title": "데이터베이스 응답 지연",
                    "message": f"데이터베이스 응답 시간이 {round(response_time, 0)}ms입니다",
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            alerts.append({
                "level": "critical",
                "category": "database",
                "title": "데이터베이스 연결 실패",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    @staticmethod
    def _check_business_alerts(db: Session) -> List[Dict[str, Any]]:
        """비즈니스 로직 알림 체크"""
        alerts = []
        
        # 1. 배차 대기 주문 체크
        pending_orders = db.query(Order).filter(
            Order.status == OrderStatus.PENDING,
            Order.created_at < datetime.now() - timedelta(hours=2)
        ).count()
        
        if pending_orders > 10:
            alerts.append({
                "level": "warning",
                "category": "business",
                "title": "배차 대기 주문 많음",
                "message": f"2시간 이상 배차 대기 중인 주문이 {pending_orders}건 있습니다",
                "timestamp": datetime.now().isoformat()
            })
        
        # 2. 차량 활용률 체크
        total_vehicles = db.query(Vehicle).count()
        in_use_vehicles = db.query(Vehicle).filter(Vehicle.status == "in_use").count()
        
        if total_vehicles > 0:
            utilization = (in_use_vehicles / total_vehicles) * 100
            if utilization < 30:
                alerts.append({
                    "level": "info",
                    "category": "business",
                    "title": "차량 활용률 낮음",
                    "message": f"차량 활용률이 {round(utilization, 1)}%로 낮습니다",
                    "timestamp": datetime.now().isoformat()
                })
        
        # 3. 진행 중인 배차 체크
        in_progress_dispatches = db.query(Dispatch).filter(
            Dispatch.status == DispatchStatus.IN_PROGRESS,
            Dispatch.dispatch_date < datetime.now().date()
        ).count()
        
        if in_progress_dispatches > 5:
            alerts.append({
                "level": "warning",
                "category": "business",
                "title": "지연된 배차 발견",
                "message": f"예정일을 넘긴 진행 중 배차가 {in_progress_dispatches}건 있습니다",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts

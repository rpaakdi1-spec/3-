"""
Phase 12: 배차 분석 서비스
배차 이력 추적, 성능 분석, 최적화 제안
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.dispatch import Dispatch
from app.models.order import Order
from app.models.vehicle import Vehicle
from app.models.driver import Driver

logger = logging.getLogger(__name__)


class DispatchAnalyticsService:
    """
    배차 분석 서비스
    
    기능:
    - 배차 성공률 분석
    - 평균 배차 시간 계산
    - 기사별 성과 분석
    - 최적화 제안
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dispatch_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        배차 통계 조회
        
        Returns:
            {
                "total_dispatches": int,
                "success_rate": float,
                "avg_distance_km": float,
                "avg_duration_min": float,
                "by_status": {...},
                "by_vehicle_type": {...}
            }
        """
        # 기본 기간: 최근 30일
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # 전체 배차 수
        query = self.db.query(Dispatch).filter(
            and_(
                Dispatch.created_at >= start_date,
                Dispatch.created_at <= end_date
            )
        )
        
        total_dispatches = query.count()
        
        if total_dispatches == 0:
            return {
                "total_dispatches": 0,
                "success_rate": 0.0,
                "avg_distance_km": 0.0,
                "avg_duration_min": 0.0,
                "by_status": {},
                "by_vehicle_type": {}
            }
        
        # 상태별 통계
        status_stats = self.db.query(
            Dispatch.status,
            func.count(Dispatch.id).label('count')
        ).filter(
            and_(
                Dispatch.created_at >= start_date,
                Dispatch.created_at <= end_date
            )
        ).group_by(Dispatch.status).all()
        
        by_status = {stat.status: stat.count for stat in status_stats}
        
        # 성공률 계산
        completed = by_status.get('completed', 0)
        success_rate = (completed / total_dispatches) * 100 if total_dispatches > 0 else 0.0
        
        # 평균 거리/시간
        avg_stats = self.db.query(
            func.avg(Dispatch.estimated_distance_km).label('avg_distance'),
            func.avg(Dispatch.estimated_duration_minutes).label('avg_duration')
        ).filter(
            and_(
                Dispatch.created_at >= start_date,
                Dispatch.created_at <= end_date,
                Dispatch.estimated_distance_km.isnot(None)
            )
        ).first()
        
        avg_distance_km = float(avg_stats.avg_distance) if avg_stats.avg_distance else 0.0
        avg_duration_min = float(avg_stats.avg_duration) if avg_stats.avg_duration else 0.0
        
        # 차량 타입별 통계
        vehicle_type_stats = self.db.query(
            Vehicle.vehicle_type,
            func.count(Dispatch.id).label('count')
        ).join(
            Dispatch, Vehicle.id == Dispatch.vehicle_id
        ).filter(
            and_(
                Dispatch.created_at >= start_date,
                Dispatch.created_at <= end_date
            )
        ).group_by(Vehicle.vehicle_type).all()
        
        by_vehicle_type = {stat.vehicle_type: stat.count for stat in vehicle_type_stats}
        
        return {
            "total_dispatches": total_dispatches,
            "success_rate": round(success_rate, 2),
            "avg_distance_km": round(avg_distance_km, 2),
            "avg_duration_min": round(avg_duration_min, 1),
            "by_status": by_status,
            "by_vehicle_type": by_vehicle_type,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    def get_driver_performance(
        self,
        driver_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        기사별 성과 분석
        
        Args:
            driver_id: 특정 기사 ID (없으면 상위 N명)
            limit: 반환할 기사 수
            
        Returns:
            [
                {
                    "driver_id": int,
                    "driver_name": str,
                    "total_dispatches": int,
                    "completed": int,
                    "completion_rate": float,
                    "avg_rating": float,
                    "total_distance_km": float
                },
                ...
            ]
        """
        # 기사별 집계
        query = self.db.query(
            Driver.id.label('driver_id'),
            Driver.name.label('driver_name'),
            # Driver.rating.label('avg_rating'),  # rating 컬럼 없음
            func.count(Dispatch.id).label('total_dispatches'),
            func.sum(
                func.cast(Dispatch.status == 'completed', type_=int)
            ).label('completed'),
            func.sum(Dispatch.estimated_distance_km).label('total_distance_km')
        ).join(
            Dispatch, Driver.id == Dispatch.driver_id
        )
        
        if driver_id:
            query = query.filter(Driver.id == driver_id)
        
        query = query.group_by(
            Driver.id, Driver.name
        ).order_by(
            func.count(Dispatch.id).desc()
        ).limit(limit)
        
        results = query.all()
        
        performance = []
        for result in results:
            total = result.total_dispatches or 0
            completed = result.completed or 0
            completion_rate = (completed / total * 100) if total > 0 else 0.0
            
            performance.append({
                "driver_id": result.driver_id,
                "driver_name": result.driver_name,
                "total_dispatches": total,
                "completed": completed,
                "completion_rate": round(completion_rate, 2),
                "avg_rating": float(result.avg_rating) if result.avg_rating else 0.0,
                "total_distance_km": float(result.total_distance_km) if result.total_distance_km else 0.0
            })
        
        return performance
    
    def get_optimization_suggestions(self) -> List[Dict]:
        """
        최적화 제안 생성
        
        Returns:
            [
                {
                    "type": "warning" | "info",
                    "title": str,
                    "description": str,
                    "action": str
                },
                ...
            ]
        """
        suggestions = []
        
        # 1. 평균 배차 시간 체크
        recent_dispatches = self.db.query(Dispatch).filter(
            Dispatch.created_at >= datetime.utcnow() - timedelta(days=7),
            Dispatch.estimated_duration_minutes.isnot(None)
        ).all()
        
        if recent_dispatches:
            avg_duration = sum(d.estimated_duration_minutes for d in recent_dispatches) / len(recent_dispatches)
            
            if avg_duration > 45:
                suggestions.append({
                    "type": "warning",
                    "title": "배차 시간이 평균보다 깁니다",
                    "description": f"최근 7일 평균 배차 시간: {avg_duration:.1f}분",
                    "action": "차량 추가 배치 또는 배차 규칙 최적화를 고려하세요"
                })
        
        # 2. 실패율 체크
        stats = self.get_dispatch_statistics(
            start_date=datetime.utcnow() - timedelta(days=7)
        )
        
        if stats['success_rate'] < 90:
            suggestions.append({
                "type": "warning",
                "title": "배차 성공률이 낮습니다",
                "description": f"최근 7일 성공률: {stats['success_rate']:.1f}%",
                "action": "배차 실패 원인을 분석하고 규칙을 조정하세요"
            })
        
        # 3. 차량 가용률 체크
        total_vehicles = self.db.query(Vehicle).filter(
            Vehicle.is_active == True
        ).count()
        
        available_vehicles = self.db.query(Vehicle).filter(
            Vehicle.is_active == True,
            Vehicle.status == 'available'
        ).count()
        
        if total_vehicles > 0:
            availability_rate = (available_vehicles / total_vehicles) * 100
            
            if availability_rate < 30:
                suggestions.append({
                    "type": "warning",
                    "title": "가용 차량이 부족합니다",
                    "description": f"현재 가용 차량: {available_vehicles}/{total_vehicles} ({availability_rate:.1f}%)",
                    "action": "차량 추가 배치 또는 배차 일정 조정이 필요합니다"
                })
        
        # 4. 성과가 낮은 기사 체크
        # low_performers = self.db.query(Driver).filter(
        #     Driver.is_active == True,
        #     Driver.rating < 3.0,
        #     Driver.rating.isnot(None)
        # ).count()
        low_performers = 0  # rating 컬럼 없음
        
        if low_performers > 0:
            suggestions.append({
                "type": "info",
                "title": "평점이 낮은 기사가 있습니다",
                "description": f"{low_performers}명의 기사가 평점 3.0 미만입니다",
                "action": "교육 또는 피드백이 필요할 수 있습니다"
            })
        
        # 5. 긍정적인 피드백
        if not suggestions:
            suggestions.append({
                "type": "info",
                "title": "모든 지표가 양호합니다",
                "description": "배차 시스템이 효율적으로 운영되고 있습니다",
                "action": "현재 운영 방식을 유지하세요"
            })
        
        return suggestions
    
    def get_hourly_dispatch_pattern(self) -> Dict:
        """
        시간대별 배차 패턴 분석
        
        Returns:
            {
                "0": 5,
                "1": 2,
                ...
                "23": 8
            }
        """
        from sqlalchemy import extract
        
        pattern = self.db.query(
            extract('hour', Dispatch.created_at).label('hour'),
            func.count(Dispatch.id).label('count')
        ).filter(
            Dispatch.created_at >= datetime.utcnow() - timedelta(days=30)
        ).group_by('hour').all()
        
        # 24시간 초기화
        hourly_pattern = {str(h): 0 for h in range(24)}
        
        for p in pattern:
            hourly_pattern[str(int(p.hour))] = p.count
        
        return hourly_pattern

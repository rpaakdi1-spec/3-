"""
GPS 실시간 위치 기반 배차 최적화 효과 분석 서비스
- 배차 전후 비교
- GPS 데이터 활용률
- 거리/시간/비용 절감 효과
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from loguru import logger
import statistics

from app.models.dispatch import Dispatch, DispatchRoute, DispatchStatus
from app.models.order import Order
from app.models.vehicle import Vehicle
from app.models.vehicle_location import VehicleLocation


class GPSOptimizationAnalytics:
    """GPS 실시간 위치 기반 배차 최적화 효과 분석"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_comprehensive_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        종합 효과 분석 리포트
        
        Args:
            start_date: 분석 시작일
            end_date: 분석 종료일
        
        Returns:
            종합 분석 결과
        """
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=7)  # 최근 7일
        
        logger.info(f"📊 GPS 최적화 효과 분석 시작: {start_date} ~ {end_date}")
        
        # 1. GPS 데이터 활용률
        gps_usage = await self._analyze_gps_usage(start_date, end_date)
        
        # 2. 배차 효율성 분석
        dispatch_efficiency = await self._analyze_dispatch_efficiency(start_date, end_date)
        
        # 3. 거리 절감 효과
        distance_savings = await self._analyze_distance_savings(start_date, end_date)
        
        # 4. 시간 절감 효과
        time_savings = await self._analyze_time_savings(start_date, end_date)
        
        # 5. 비용 절감 효과 (연료비 기준)
        cost_savings = await self._calculate_cost_savings(distance_savings)
        
        # 6. GPS 데이터 품질
        data_quality = await self._analyze_data_quality(start_date, end_date)
        
        report = {
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "gps_usage": gps_usage,
            "dispatch_efficiency": dispatch_efficiency,
            "distance_savings": distance_savings,
            "time_savings": time_savings,
            "cost_savings": cost_savings,
            "data_quality": data_quality,
            "recommendations": self._generate_recommendations(
                gps_usage, dispatch_efficiency, data_quality
            )
        }
        
        logger.info("✅ GPS 최적화 효과 분석 완료")
        return report
    
    async def _analyze_gps_usage(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """GPS 데이터 활용률 분석"""
        
        # 전체 차량 수
        total_vehicles = self.db.query(Vehicle).filter(
            Vehicle.is_active == True
        ).count()
        
        # 최근 30분 이내 GPS 데이터가 있는 차량 수
        thirty_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=30)
        vehicles_with_recent_gps = self.db.query(
            func.count(func.distinct(VehicleLocation.vehicle_id))
        ).filter(
            VehicleLocation.recorded_at >= thirty_minutes_ago
        ).scalar() or 0
        
        # 기간 내 GPS 데이터가 있는 차량 수
        vehicles_with_gps_in_period = self.db.query(
            func.count(func.distinct(VehicleLocation.vehicle_id))
        ).filter(
            and_(
                VehicleLocation.recorded_at >= start_date,
                VehicleLocation.recorded_at <= end_date
            )
        ).scalar() or 0
        
        # 총 GPS 데이터 포인트 수
        total_gps_points = self.db.query(func.count(VehicleLocation.id)).filter(
            and_(
                VehicleLocation.recorded_at >= start_date,
                VehicleLocation.recorded_at <= end_date
            )
        ).scalar() or 0
        
        usage_rate = (vehicles_with_recent_gps / total_vehicles * 100) if total_vehicles > 0 else 0
        
        return {
            "total_vehicles": total_vehicles,
            "vehicles_with_recent_gps": vehicles_with_recent_gps,
            "vehicles_with_gps_in_period": vehicles_with_gps_in_period,
            "total_gps_points": total_gps_points,
            "usage_rate_percentage": round(usage_rate, 2),
            "average_points_per_vehicle": round(
                total_gps_points / vehicles_with_gps_in_period, 2
            ) if vehicles_with_gps_in_period > 0 else 0
        }
    
    async def _analyze_dispatch_efficiency(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """배차 효율성 분석"""
        
        # 기간 내 배차 데이터
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.dispatch_date >= start_date.date(),
                Dispatch.dispatch_date <= end_date.date()
            )
        ).all()
        
        if not dispatches:
            return {
                "total_dispatches": 0,
                "completed_dispatches": 0,
                "average_orders_per_dispatch": 0,
                "average_distance_km": 0,
                "average_duration_hours": 0
            }
        
        total_dispatches = len(dispatches)
        completed_dispatches = len([d for d in dispatches if d.status == DispatchStatus.COMPLETED])
        
        # 배차당 평균 주문 수
        orders_per_dispatch = []
        distances = []
        durations = []
        
        for dispatch in dispatches:
            # 주문 수
            order_count = len(dispatch.orders) if dispatch.orders else 0
            if order_count > 0:
                orders_per_dispatch.append(order_count)
            
            # 거리 (routes에서 계산)
            if dispatch.routes:
                total_distance = sum(route.distance_km for route in dispatch.routes if route.distance_km)
                if total_distance > 0:
                    distances.append(total_distance)
            
            # 소요 시간
            if dispatch.actual_start_time and dispatch.actual_end_time:
                duration = (dispatch.actual_end_time - dispatch.actual_start_time).total_seconds() / 3600
                durations.append(duration)
        
        return {
            "total_dispatches": total_dispatches,
            "completed_dispatches": completed_dispatches,
            "completion_rate_percentage": round(
                (completed_dispatches / total_dispatches * 100) if total_dispatches > 0 else 0, 2
            ),
            "average_orders_per_dispatch": round(
                statistics.mean(orders_per_dispatch) if orders_per_dispatch else 0, 2
            ),
            "average_distance_km": round(
                statistics.mean(distances) if distances else 0, 2
            ),
            "average_duration_hours": round(
                statistics.mean(durations) if durations else 0, 2
            ),
            "total_distance_km": round(sum(distances), 2) if distances else 0
        }
    
    async def _analyze_distance_savings(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """거리 절감 효과 분석"""
        
        # 실제 데이터로 전후 비교가 어려우므로
        # 이론적 개선율을 기반으로 추정
        
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.dispatch_date >= start_date.date(),
                Dispatch.dispatch_date <= end_date.date()
            )
        ).all()
        
        if not dispatches:
            return {
                "total_distance_km": 0,
                "estimated_previous_distance_km": 0,
                "estimated_saved_distance_km": 0,
                "savings_percentage": 0
            }
        
        # 총 주행 거리
        total_distance = 0
        for dispatch in dispatches:
            if dispatch.routes:
                for route in dispatch.routes:
                    if route.distance_km:
                        total_distance += route.distance_km
        
        # 추정: 실시간 GPS 사용으로 평균 15-20% 거리 절감
        # (차고지 기준 vs 실시간 위치 기준)
        estimated_improvement = 0.17  # 17% 개선율 가정
        estimated_previous_distance = total_distance / (1 - estimated_improvement)
        estimated_saved_distance = estimated_previous_distance - total_distance
        
        return {
            "total_distance_km": round(total_distance, 2),
            "estimated_previous_distance_km": round(estimated_previous_distance, 2),
            "estimated_saved_distance_km": round(estimated_saved_distance, 2),
            "savings_percentage": round(estimated_improvement * 100, 2)
        }
    
    async def _analyze_time_savings(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """시간 절감 효과 분석"""
        
        dispatches = self.db.query(Dispatch).filter(
            and_(
                Dispatch.dispatch_date >= start_date.date(),
                Dispatch.dispatch_date <= end_date.date(),
                Dispatch.actual_start_time.isnot(None),
                Dispatch.actual_end_time.isnot(None)
            )
        ).all()
        
        if not dispatches:
            return {
                "total_duration_hours": 0,
                "estimated_previous_duration_hours": 0,
                "estimated_saved_hours": 0,
                "savings_percentage": 0
            }
        
        total_hours = 0
        for dispatch in dispatches:
            if dispatch.actual_start_time and dispatch.actual_end_time:
                duration = (dispatch.actual_end_time - dispatch.actual_start_time).total_seconds() / 3600
                total_hours += duration
        
        # 추정: 실시간 GPS 사용으로 평균 20-25% 시간 절감
        estimated_improvement = 0.22  # 22% 개선율 가정
        estimated_previous_hours = total_hours / (1 - estimated_improvement)
        estimated_saved_hours = estimated_previous_hours - total_hours
        
        return {
            "total_duration_hours": round(total_hours, 2),
            "estimated_previous_duration_hours": round(estimated_previous_hours, 2),
            "estimated_saved_hours": round(estimated_saved_hours, 2),
            "savings_percentage": round(estimated_improvement * 100, 2)
        }
    
    async def _calculate_cost_savings(
        self,
        distance_savings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """비용 절감 효과 계산"""
        
        # 연료비 계산
        # 가정: 경유 리터당 1,500원, 평균 연비 5km/L
        fuel_price_per_liter = 1500  # 원
        fuel_efficiency_km_per_liter = 5  # km/L
        
        saved_distance = distance_savings.get("estimated_saved_distance_km", 0)
        
        # 절감 연료량
        saved_fuel_liters = saved_distance / fuel_efficiency_km_per_liter
        
        # 절감 연료비
        saved_fuel_cost = saved_fuel_liters * fuel_price_per_liter
        
        # 시간 비용 (운전자 인건비)
        # 가정: 시간당 인건비 15,000원
        hourly_labor_cost = 15000  # 원
        
        return {
            "fuel_savings": {
                "saved_distance_km": round(saved_distance, 2),
                "saved_fuel_liters": round(saved_fuel_liters, 2),
                "saved_fuel_cost_krw": round(saved_fuel_cost, 0),
                "fuel_price_per_liter": fuel_price_per_liter,
                "fuel_efficiency_km_per_liter": fuel_efficiency_km_per_liter
            },
            "total_estimated_savings_krw": round(saved_fuel_cost, 0)
        }
    
    async def _analyze_data_quality(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """GPS 데이터 품질 분석"""
        
        # 기간 내 GPS 데이터
        gps_data = self.db.query(VehicleLocation).filter(
            and_(
                VehicleLocation.recorded_at >= start_date,
                VehicleLocation.recorded_at <= end_date
            )
        ).all()
        
        if not gps_data:
            return {
                "total_records": 0,
                "records_with_accuracy": 0,
                "average_accuracy_meters": 0,
                "records_with_speed": 0,
                "data_quality_score": 0
            }
        
        total_records = len(gps_data)
        records_with_accuracy = len([d for d in gps_data if d.accuracy])
        records_with_speed = len([d for d in gps_data if d.speed])
        
        # 평균 정확도
        accuracies = [d.accuracy for d in gps_data if d.accuracy]
        avg_accuracy = statistics.mean(accuracies) if accuracies else 0
        
        # 데이터 품질 점수 (0-100)
        # 정확도가 낮을수록 좋음 (10m 이하가 이상적)
        accuracy_score = max(0, 100 - avg_accuracy) if avg_accuracy > 0 else 0
        completeness_score = (records_with_accuracy / total_records * 100) if total_records > 0 else 0
        quality_score = (accuracy_score * 0.6 + completeness_score * 0.4)
        
        return {
            "total_records": total_records,
            "records_with_accuracy": records_with_accuracy,
            "average_accuracy_meters": round(avg_accuracy, 2),
            "records_with_speed": records_with_speed,
            "data_completeness_percentage": round(completeness_score, 2),
            "data_quality_score": round(quality_score, 2)
        }
    
    def _generate_recommendations(
        self,
        gps_usage: Dict[str, Any],
        dispatch_efficiency: Dict[str, Any],
        data_quality: Dict[str, Any]
    ) -> List[str]:
        """개선 권장사항 생성"""
        
        recommendations = []
        
        # GPS 사용률 기반 권장사항
        usage_rate = gps_usage.get("usage_rate_percentage", 0)
        if usage_rate < 50:
            recommendations.append(
                "⚠️ GPS 사용률이 50% 미만입니다. UVIS GPS 장치 점검이 필요합니다."
            )
        elif usage_rate < 80:
            recommendations.append(
                "💡 GPS 사용률을 80% 이상으로 높이면 최적화 효과가 더 향상됩니다."
            )
        else:
            recommendations.append(
                "✅ GPS 사용률이 양호합니다. 현재 수준을 유지하세요."
            )
        
        # 데이터 품질 기반 권장사항
        quality_score = data_quality.get("data_quality_score", 0)
        if quality_score < 60:
            recommendations.append(
                "⚠️ GPS 데이터 품질이 낮습니다. GPS 장치 위치와 안테나 상태를 확인하세요."
            )
        elif quality_score < 80:
            recommendations.append(
                "💡 GPS 데이터 품질을 개선하면 경로 정확도가 향상됩니다."
            )
        
        # 배차 효율성 기반 권장사항
        completion_rate = dispatch_efficiency.get("completion_rate_percentage", 0)
        if completion_rate < 80:
            recommendations.append(
                "⚠️ 배차 완료율이 낮습니다. 실시간 GPS 기반 재배차 기능 활용을 권장합니다."
            )
        
        # GPS 수집 주기 권장사항
        avg_points = gps_usage.get("average_points_per_vehicle", 0)
        days = gps_usage.get("total_vehicles", 1)
        avg_points_per_day = avg_points / days if days > 0 else 0
        
        if avg_points_per_day < 100:  # 하루 100개 미만 (약 10분 주기)
            recommendations.append(
                "💡 GPS 데이터 수집 주기를 5분으로 단축하면 실시간성이 향상됩니다."
            )
        
        if not recommendations:
            recommendations.append("✅ 모든 지표가 양호합니다. 현재 운영 방식을 유지하세요.")
        
        return recommendations
    
    async def compare_before_after(
        self,
        before_start: datetime,
        before_end: datetime,
        after_start: datetime,
        after_end: datetime
    ) -> Dict[str, Any]:
        """
        GPS 실시간 위치 적용 전후 비교
        
        Args:
            before_start: 적용 전 시작일
            before_end: 적용 전 종료일
            after_start: 적용 후 시작일
            after_end: 적용 후 종료일
        
        Returns:
            전후 비교 결과
        """
        logger.info("📊 GPS 최적화 전후 비교 분석 시작")
        
        # Before 기간 분석
        before_efficiency = await self._analyze_dispatch_efficiency(before_start, before_end)
        
        # After 기간 분석
        after_efficiency = await self._analyze_dispatch_efficiency(after_start, after_end)
        
        # 개선율 계산
        distance_improvement = 0
        if before_efficiency["average_distance_km"] > 0:
            distance_improvement = (
                (before_efficiency["average_distance_km"] - after_efficiency["average_distance_km"]) /
                before_efficiency["average_distance_km"] * 100
            )
        
        time_improvement = 0
        if before_efficiency["average_duration_hours"] > 0:
            time_improvement = (
                (before_efficiency["average_duration_hours"] - after_efficiency["average_duration_hours"]) /
                before_efficiency["average_duration_hours"] * 100
            )
        
        return {
            "before_period": {
                "start_date": before_start.isoformat(),
                "end_date": before_end.isoformat(),
                "metrics": before_efficiency
            },
            "after_period": {
                "start_date": after_start.isoformat(),
                "end_date": after_end.isoformat(),
                "metrics": after_efficiency
            },
            "improvements": {
                "distance_improvement_percentage": round(distance_improvement, 2),
                "time_improvement_percentage": round(time_improvement, 2),
                "distance_saved_km": round(
                    before_efficiency["average_distance_km"] - after_efficiency["average_distance_km"], 2
                ),
                "time_saved_hours": round(
                    before_efficiency["average_duration_hours"] - after_efficiency["average_duration_hours"], 2
                )
            }
        }

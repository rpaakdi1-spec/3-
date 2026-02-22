"""
GPS 데이터 수집 주기 최적화 서비스
- 동적 수집 주기 조정
- 차량 상태별 수집 전략
- 데이터 품질 모니터링
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from loguru import logger
import statistics

from app.models.vehicle import Vehicle, VehicleStatus
from app.models.vehicle_location import VehicleLocation
from app.models.dispatch import Dispatch, DispatchStatus


class GPSCollectionOptimizer:
    """GPS 데이터 수집 주기 최적화"""
    
    # 차량 상태별 권장 수집 주기 (분)
    COLLECTION_INTERVALS = {
        VehicleStatus.IN_USE: 3,       # 운행 중: 3분 (높은 정확도 필요)
        VehicleStatus.AVAILABLE: 10,   # 운행 가능: 10분 (중간 정확도)
        VehicleStatus.MAINTENANCE: 60, # 정비 중: 60분 (최소 수집)
        VehicleStatus.EMERGENCY_MAINTENANCE: 60, # 긴급 정비: 60분
        VehicleStatus.BREAKDOWN: 120,  # 고장: 120분 (최소 수집)
        VehicleStatus.OUT_OF_SERVICE: 120  # 운행 불가: 120분 (최소 수집)
    }
    
    # 데이터 품질 기준
    MIN_ACCURACY_METERS = 50        # 최소 정확도 50m
    MAX_TIME_GAP_MINUTES = 30       # 최대 데이터 공백 30분
    MIN_DAILY_POINTS = 100          # 일일 최소 데이터 포인트 100개
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_collection_strategy(self) -> Dict[str, Any]:
        """
        차량별 GPS 수집 전략 분석
        
        Returns:
            차량별 권장 수집 주기 및 현황
        """
        logger.info("📊 GPS 수집 전략 분석 시작")
        
        vehicles = self.db.query(Vehicle).filter(
            Vehicle.is_active == True
        ).all()
        
        strategies = []
        
        for vehicle in vehicles:
            # 현재 상태
            current_status = vehicle.status
            
            # 권장 수집 주기
            recommended_interval = self.COLLECTION_INTERVALS.get(
                current_status,
                10  # 기본값 10분
            )
            
            # 최근 배차 여부
            active_dispatch = self.db.query(Dispatch).filter(
                and_(
                    Dispatch.vehicle_id == vehicle.id,
                    Dispatch.status.in_([
                        DispatchStatus.CONFIRMED,
                        DispatchStatus.IN_PROGRESS
                    ])
                )
            ).first()
            
            # 배차 중이면 더 짧은 주기
            if active_dispatch:
                recommended_interval = min(recommended_interval, 3)
            
            # 최근 GPS 데이터 확인
            latest_gps = self.db.query(VehicleLocation).filter(
                VehicleLocation.vehicle_id == vehicle.id
            ).order_by(VehicleLocation.recorded_at.desc()).first()
            
            time_since_last_update = None
            if latest_gps:
                # 현재 시간을 timezone-naive로 변환 (데이터베이스가 UTC로 저장)
                now = datetime.now(timezone.utc).replace(tzinfo=None)
                
                time_since_last_update = (
                    now - latest_gps.recorded_at
                ).total_seconds() / 60  # 분 단위
            
            # 데이터 품질 평가
            quality_score = await self._evaluate_vehicle_data_quality(vehicle.id)
            
            strategies.append({
                "vehicle_id": vehicle.id,
                "vehicle_code": vehicle.code,
                "current_status": current_status.value if current_status else "UNKNOWN",
                "has_active_dispatch": active_dispatch is not None,
                "recommended_interval_minutes": recommended_interval,
                "time_since_last_update_minutes": round(time_since_last_update, 2) if time_since_last_update else None,
                "data_quality_score": quality_score,
                "needs_attention": time_since_last_update and time_since_last_update > self.MAX_TIME_GAP_MINUTES
            })
        
        # 통계
        total_vehicles = len(strategies)
        vehicles_with_attention = len([s for s in strategies if s["needs_attention"]])
        avg_quality = statistics.mean([s["data_quality_score"] for s in strategies]) if strategies else 0
        
        result = {
            "total_vehicles": total_vehicles,
            "vehicles_needing_attention": vehicles_with_attention,
            "average_quality_score": round(avg_quality, 2),
            "strategies": strategies,
            "collection_intervals": {
                status.value: interval
                for status, interval in self.COLLECTION_INTERVALS.items()
            }
        }
        
        logger.info(f"✅ GPS 수집 전략 분석 완료: {total_vehicles}대, 주의 필요 {vehicles_with_attention}대")
        return result
    
    async def _evaluate_vehicle_data_quality(self, vehicle_id: int) -> float:
        """
        차량 GPS 데이터 품질 평가
        
        Args:
            vehicle_id: 차량 ID
        
        Returns:
            품질 점수 (0-100)
        """
        # 최근 24시간 데이터
        since = datetime.now(timezone.utc) - timedelta(days=1)
        # timezone-naive로 변환하여 비교 (데이터베이스가 timezone-naive 저장)
        if since.tzinfo is not None:
            since = since.replace(tzinfo=None)
        
        gps_data = self.db.query(VehicleLocation).filter(
            and_(
                VehicleLocation.vehicle_id == vehicle_id,
                VehicleLocation.recorded_at >= since
            )
        ).order_by(VehicleLocation.recorded_at).all()
        
        if not gps_data:
            return 0
        
        # 1. 데이터 개수 (일일 최소 100개 기준)
        count_score = min(len(gps_data) / self.MIN_DAILY_POINTS * 100, 100)
        
        # 2. 정확도 (50m 이하가 양호)
        accuracies = [d.accuracy for d in gps_data if d.accuracy]
        if accuracies:
            avg_accuracy = statistics.mean(accuracies)
            accuracy_score = max(0, 100 - (avg_accuracy / self.MIN_ACCURACY_METERS * 100))
        else:
            accuracy_score = 50  # 정확도 정보 없으면 중간 점수
        
        # 3. 데이터 연속성 (최대 공백 30분 기준)
        gap_scores = []
        for i in range(1, len(gps_data)):
            # 두 날짜 모두 timezone-naive이므로 직접 비교 가능
            gap_minutes = (
                gps_data[i].recorded_at - gps_data[i-1].recorded_at
            ).total_seconds() / 60
            
            if gap_minutes <= self.MAX_TIME_GAP_MINUTES:
                gap_scores.append(100)
            else:
                # 공백이 길수록 점수 감소
                gap_scores.append(
                    max(0, 100 - ((gap_minutes - self.MAX_TIME_GAP_MINUTES) / self.MAX_TIME_GAP_MINUTES * 100))
                )
        
        continuity_score = statistics.mean(gap_scores) if gap_scores else 0
        
        # 최종 품질 점수 (가중 평균)
        quality_score = (
            count_score * 0.3 +
            accuracy_score * 0.4 +
            continuity_score * 0.3
        )
        
        return round(quality_score, 2)
    
    async def get_optimization_recommendations(self) -> Dict[str, Any]:
        """
        GPS 데이터 수집 최적화 권장사항
        
        Returns:
            최적화 권장사항 및 예상 효과
        """
        logger.info("💡 GPS 수집 최적화 권장사항 생성 시작")
        
        strategy = await self.get_collection_strategy()
        
        recommendations = []
        
        # 1. 차량 상태별 동적 수집 주기
        if strategy["vehicles_needing_attention"] > 0:
            recommendations.append({
                "priority": "HIGH",
                "category": "데이터 수집",
                "issue": f"{strategy['vehicles_needing_attention']}대 차량의 GPS 데이터 업데이트 지연",
                "recommendation": "UVIS GPS 장치 통신 상태 점검 및 수집 주기 단축 (5분 → 3분)",
                "expected_impact": "실시간 위치 정확도 30% 향상",
                "implementation": "scheduler_service.py의 IntervalTrigger를 3분으로 변경"
            })
        
        # 2. 배차 중 차량 우선 수집
        active_dispatches = self.db.query(func.count(Dispatch.id)).filter(
            Dispatch.status.in_([DispatchStatus.CONFIRMED, DispatchStatus.IN_PROGRESS])
        ).scalar() or 0
        
        if active_dispatches > 0:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "수집 전략",
                "issue": f"{active_dispatches}건 배차가 진행 중",
                "recommendation": "배차 중 차량은 1-2분 주기로 GPS 수집",
                "expected_impact": "배차 경로 추적 정확도 50% 향상",
                "implementation": "차량 상태별 동적 수집 주기 적용"
            })
        
        # 3. 데이터 품질 개선
        if strategy["average_quality_score"] < 70:
            recommendations.append({
                "priority": "HIGH",
                "category": "데이터 품질",
                "issue": f"평균 데이터 품질 점수 {strategy['average_quality_score']}/100",
                "recommendation": "GPS 장치 위치 조정 및 안테나 상태 점검",
                "expected_impact": "데이터 정확도 25% 향상, 위치 오차 50% 감소",
                "implementation": "물리적 GPS 장치 점검 및 재설치"
            })
        
        # 4. 배터리 및 통신 비용 최적화
        recommendations.append({
            "priority": "LOW",
            "category": "비용 최적화",
            "issue": "운휴/정비 중 차량도 동일 주기로 수집",
            "recommendation": "차량 상태별 차등 수집 (운행:3분, 대기:10분, 운휴:60분)",
            "expected_impact": "데이터 전송 비용 30% 절감, 배터리 수명 20% 연장",
            "implementation": "차량 상태 기반 동적 수집 주기 스케줄러 구현"
        })
        
        # 5. 데이터 저장소 최적화
        # 데이터베이스의 timezone에 맞춰 비교
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        # timezone-naive로 변환하여 비교 (데이터베이스가 timezone-naive 저장)
        if one_day_ago.tzinfo is not None:
            one_day_ago = one_day_ago.replace(tzinfo=None)
        
        total_points_per_day = self.db.query(func.count(VehicleLocation.id)).filter(
            VehicleLocation.recorded_at >= one_day_ago
        ).scalar() or 0
        
        recommendations.append({
            "priority": "LOW",
            "category": "스토리지 최적화",
            "issue": f"일일 {total_points_per_day:,}개 GPS 데이터 포인트 저장",
            "recommendation": "30일 이전 데이터는 1시간 단위로 집계하여 압축 저장",
            "expected_impact": "스토리지 사용량 70% 감소",
            "implementation": "GPS 데이터 아카이빙 스케줄러 추가"
        })
        
        result = {
            "analysis_date": datetime.now(timezone.utc).isoformat(),
            "current_metrics": {
                "total_vehicles": strategy["total_vehicles"],
                "vehicles_needing_attention": strategy["vehicles_needing_attention"],
                "average_quality_score": strategy["average_quality_score"],
                "daily_data_points": total_points_per_day
            },
            "recommendations": recommendations,
            "implementation_priority": [
                r["recommendation"] for r in sorted(
                    recommendations,
                    key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["priority"]]
                )
            ]
        }
        
        logger.info(f"✅ {len(recommendations)}개 권장사항 생성 완료")
        return result
    
    async def implement_dynamic_collection(
        self,
        vehicle_id: int,
        force_interval_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        특정 차량의 동적 수집 주기 적용
        
        Args:
            vehicle_id: 차량 ID
            force_interval_minutes: 강제 수집 주기 (None이면 자동 결정)
        
        Returns:
            적용 결과
        """
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        
        if not vehicle:
            return {"success": False, "error": "Vehicle not found"}
        
        # 수집 주기 결정
        if force_interval_minutes:
            interval = force_interval_minutes
        else:
            interval = self.COLLECTION_INTERVALS.get(vehicle.status, 10)
            
            # 배차 중이면 최소 주기
            active_dispatch = self.db.query(Dispatch).filter(
                and_(
                    Dispatch.vehicle_id == vehicle_id,
                    Dispatch.status.in_([
                        DispatchStatus.CONFIRMED,
                        DispatchStatus.IN_PROGRESS
                    ])
                )
            ).first()
            
            if active_dispatch:
                interval = min(interval, 3)
        
        logger.info(
            f"🔄 차량 {vehicle.code}: GPS 수집 주기 {interval}분으로 설정"
        )
        
        return {
            "success": True,
            "vehicle_id": vehicle_id,
            "vehicle_code": vehicle.code,
            "status": vehicle.status.value if vehicle.status else "UNKNOWN",
            "interval_minutes": interval,
            "has_active_dispatch": active_dispatch is not None if 'active_dispatch' in locals() else False
        }

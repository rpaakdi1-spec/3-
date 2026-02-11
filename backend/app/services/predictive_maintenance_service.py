"""
Predictive Maintenance Service for Phase 14
AI-based failure prediction and maintenance scheduling
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import random
import json

from app.models.iot_sensor import (
    MaintenanceRecord, MaintenancePrediction, VehicleHealth,
    PartInventory, MaintenanceSchedule, MaintenanceStatus,
    SensorReading, VehicleSensor
)


class PredictiveMaintenanceService:
    """예측 유지보수 서비스"""

    def __init__(self, db: Session):
        self.db = db
        self.model_version = "v1.0.0"

    async def predict_maintenance(
        self,
        vehicle_id: int,
        analyze_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        차량의 정비 필요성 예측
        
        Args:
            vehicle_id: 차량 ID
            analyze_days: 분석 기간 (일)
            
        Returns:
            예측된 정비 항목 목록
        """
        # 센서 데이터 수집
        cutoff_time = datetime.utcnow() - timedelta(days=analyze_days)
        
        sensor_readings = self.db.query(SensorReading).filter(
            and_(
                SensorReading.vehicle_id == vehicle_id,
                SensorReading.recorded_at >= cutoff_time
            )
        ).all()

        # 정비 이력 조회
        maintenance_history = self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.vehicle_id == vehicle_id
        ).order_by(desc(MaintenanceRecord.completed_at)).limit(10).all()

        # 부품별 예측
        predictions = []
        components = [
            "engine",
            "transmission",
            "brake_system",
            "suspension",
            "battery",
            "tire"
        ]

        for component in components:
            prediction = await self._predict_component_failure(
                vehicle_id,
                component,
                sensor_readings,
                maintenance_history
            )
            
            if prediction and prediction["failure_probability"] > 0.3:
                predictions.append(prediction)

        # 예측 결과 저장
        for pred in predictions:
            self._save_prediction(vehicle_id, pred)

        return predictions

    async def _predict_component_failure(
        self,
        vehicle_id: int,
        component: str,
        sensor_readings: List,
        maintenance_history: List
    ) -> Optional[Dict[str, Any]]:
        """부품별 고장 예측 (간단한 rule-based + ML 시뮬레이션)"""
        
        # 센서 데이터 분석
        anomaly_count = sum(1 for r in sensor_readings if r.is_anomaly)
        total_readings = len(sensor_readings)
        anomaly_rate = anomaly_count / total_readings if total_readings > 0 else 0

        # 정비 이력 분석
        days_since_last_maintenance = 365  # 기본값
        if maintenance_history:
            last_maintenance = maintenance_history[0]
            if last_maintenance.completed_at:
                days_since_last_maintenance = (
                    datetime.utcnow() - last_maintenance.completed_at
                ).days

        # 예측 로직 (실제로는 ML 모델 사용)
        base_probability = 0.1
        
        # 이상 감지율에 따른 확률 증가
        base_probability += anomaly_rate * 0.5
        
        # 마지막 정비 후 경과 일수에 따른 확률 증가
        if days_since_last_maintenance > 180:  # 6개월
            base_probability += 0.2
        if days_since_last_maintenance > 365:  # 1년
            base_probability += 0.3

        # 부품별 특성 반영
        component_factors = {
            "engine": 1.0,
            "transmission": 0.9,
            "brake_system": 1.1,
            "suspension": 0.8,
            "battery": 1.2,
            "tire": 1.0
        }
        
        failure_probability = min(
            base_probability * component_factors.get(component, 1.0),
            0.95
        )

        # 예측 신뢰도 계산
        confidence_score = 0.7 + (total_readings / 1000) * 0.3
        confidence_score = min(confidence_score, 0.95)

        # 예상 고장 일자 계산
        days_to_failure = int(100 * (1 - failure_probability))
        predicted_failure_date = datetime.utcnow() + timedelta(days=days_to_failure)

        # 권장 조치 및 비용
        component_names = {
            "engine": "엔진",
            "transmission": "변속기",
            "brake_system": "브레이크 시스템",
            "suspension": "서스펜션",
            "battery": "배터리",
            "tire": "타이어"
        }

        recommended_actions = {
            "engine": "엔진 오일 교체 및 점검",
            "transmission": "변속기 오일 교체",
            "brake_system": "브레이크 패드 교체",
            "suspension": "쇼크업소버 점검",
            "battery": "배터리 교체",
            "tire": "타이어 교체"
        }

        estimated_costs = {
            "engine": 150000,
            "transmission": 200000,
            "brake_system": 120000,
            "suspension": 180000,
            "battery": 100000,
            "tire": 250000
        }

        # 권장 정비 일자 (예상 고장 일자보다 2주 전)
        recommended_date = predicted_failure_date - timedelta(days=14)

        return {
            "component": component,
            "component_name": component_names.get(component, component),
            "failure_probability": round(failure_probability, 3),
            "predicted_failure_date": predicted_failure_date,
            "confidence_score": round(confidence_score, 3),
            "recommended_action": recommended_actions.get(component, "점검 필요"),
            "recommended_date": recommended_date,
            "estimated_cost": estimated_costs.get(component, 100000),
            "sensor_anomaly_rate": round(anomaly_rate, 3),
            "days_since_last_maintenance": days_since_last_maintenance
        }

    def _save_prediction(self, vehicle_id: int, prediction_data: Dict[str, Any]):
        """예측 결과 저장"""
        # 기존 예측 비활성화
        self.db.query(MaintenancePrediction).filter(
            and_(
                MaintenancePrediction.vehicle_id == vehicle_id,
                MaintenancePrediction.component == prediction_data["component"],
                MaintenancePrediction.is_active == True
            )
        ).update({"is_active": False})

        # 새 예측 저장
        prediction = MaintenancePrediction(
            vehicle_id=vehicle_id,
            component=prediction_data["component"],
            failure_probability=prediction_data["failure_probability"],
            predicted_failure_date=prediction_data["predicted_failure_date"],
            confidence_score=prediction_data["confidence_score"],
            recommended_action=prediction_data["recommended_action"],
            recommended_date=prediction_data["recommended_date"],
            estimated_cost=prediction_data["estimated_cost"],
            sensor_data_summary={
                "anomaly_rate": prediction_data["sensor_anomaly_rate"],
                "days_since_maintenance": prediction_data["days_since_last_maintenance"]
            },
            model_version=self.model_version,
            is_active=True
        )
        
        self.db.add(prediction)
        self.db.commit()

    async def get_vehicle_predictions(
        self,
        vehicle_id: int,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """차량의 예측 결과 조회"""
        query = self.db.query(MaintenancePrediction).filter(
            MaintenancePrediction.vehicle_id == vehicle_id
        )

        if active_only:
            query = query.filter(MaintenancePrediction.is_active == True)

        predictions = query.order_by(
            desc(MaintenancePrediction.failure_probability)
        ).all()

        return [
            {
                "id": p.id,
                "vehicle_id": p.vehicle_id,
                "component": p.component,
                "failure_probability": p.failure_probability,
                "predicted_failure_date": p.predicted_failure_date.isoformat(),
                "confidence_score": p.confidence_score,
                "recommended_action": p.recommended_action,
                "recommended_date": p.recommended_date.isoformat() if p.recommended_date else None,
                "estimated_cost": p.estimated_cost,
                "is_scheduled": p.is_scheduled,
                "prediction_date": p.prediction_date.isoformat()
            }
            for p in predictions
        ]

    async def calculate_vehicle_health(
        self,
        vehicle_id: int
    ) -> Dict[str, Any]:
        """차량 건강 점수 계산"""
        # 활성 예측 조회
        predictions = await self.get_vehicle_predictions(vehicle_id, active_only=True)

        # 부품별 점수 계산 (0-100)
        component_scores = {
            "engine": 100,
            "transmission": 100,
            "brake": 100,
            "suspension": 100,
            "electrical": 100
        }

        for pred in predictions:
            component = pred["component"]
            failure_prob = pred["failure_probability"]
            
            # 고장 확률에 따른 점수 감소
            score_reduction = failure_prob * 100
            
            if component == "engine":
                component_scores["engine"] -= score_reduction
            elif component == "transmission":
                component_scores["transmission"] -= score_reduction
            elif component == "brake_system":
                component_scores["brake"] -= score_reduction
            elif component == "suspension":
                component_scores["suspension"] -= score_reduction
            elif component in ["battery"]:
                component_scores["electrical"] -= score_reduction

        # 모든 점수를 0-100 범위로 제한
        for key in component_scores:
            component_scores[key] = max(0, min(100, component_scores[key]))

        # 전체 건강 점수 (가중 평균)
        overall_score = (
            component_scores["engine"] * 0.3 +
            component_scores["transmission"] * 0.25 +
            component_scores["brake"] * 0.2 +
            component_scores["suspension"] * 0.15 +
            component_scores["electrical"] * 0.1
        )

        # 건강 상태 분류
        if overall_score >= 90:
            health_status = "excellent"
        elif overall_score >= 75:
            health_status = "good"
        elif overall_score >= 60:
            health_status = "fair"
        elif overall_score >= 40:
            health_status = "poor"
        else:
            health_status = "critical"

        # 위험 요인
        risk_factors = [
            {
                "component": p["component"],
                "probability": p["failure_probability"],
                "predicted_date": p["predicted_failure_date"]
            }
            for p in predictions
            if p["failure_probability"] > 0.5
        ]

        # VehicleHealth 업데이트 또는 생성
        vehicle_health = self.db.query(VehicleHealth).filter(
            VehicleHealth.vehicle_id == vehicle_id
        ).first()

        if vehicle_health:
            vehicle_health.overall_score = overall_score
            vehicle_health.engine_score = component_scores["engine"]
            vehicle_health.transmission_score = component_scores["transmission"]
            vehicle_health.brake_score = component_scores["brake"]
            vehicle_health.suspension_score = component_scores["suspension"]
            vehicle_health.electrical_score = component_scores["electrical"]
            vehicle_health.health_status = health_status
            vehicle_health.risk_factors = risk_factors
            vehicle_health.last_assessment = datetime.utcnow()
        else:
            vehicle_health = VehicleHealth(
                vehicle_id=vehicle_id,
                overall_score=overall_score,
                engine_score=component_scores["engine"],
                transmission_score=component_scores["transmission"],
                brake_score=component_scores["brake"],
                suspension_score=component_scores["suspension"],
                electrical_score=component_scores["electrical"],
                health_status=health_status,
                risk_factors=risk_factors
            )
            self.db.add(vehicle_health)

        self.db.commit()
        self.db.refresh(vehicle_health)

        return {
            "vehicle_id": vehicle_id,
            "overall_score": overall_score,
            "health_status": health_status,
            "component_scores": component_scores,
            "risk_factors": risk_factors,
            "prediction_count": len(predictions),
            "last_assessment": vehicle_health.last_assessment.isoformat()
        }

    async def schedule_maintenance(
        self,
        prediction_id: int,
        scheduled_date: datetime,
        assigned_technician: Optional[str] = None
    ) -> Dict[str, Any]:
        """예측 기반 정비 스케줄 생성"""
        prediction = self.db.query(MaintenancePrediction).filter(
            MaintenancePrediction.id == prediction_id
        ).first()

        if not prediction:
            raise ValueError(f"Prediction {prediction_id} not found")

        # 필요한 부품 확인
        required_parts = await self._get_required_parts(prediction.component)

        # 스케줄 생성
        schedule = MaintenanceSchedule(
            vehicle_id=prediction.vehicle_id,
            schedule_type="predictive",
            priority="normal" if prediction.failure_probability < 0.7 else "high",
            title=f"{prediction.recommended_action}",
            description=f"예측 기반 정비: {prediction.component} (고장 확률: {prediction.failure_probability:.1%})",
            work_items=[
                {
                    "component": prediction.component,
                    "action": prediction.recommended_action,
                    "estimated_hours": 2.0
                }
            ],
            required_parts=required_parts,
            scheduled_date=scheduled_date,
            estimated_duration_hours=2.0,
            assigned_technician=assigned_technician,
            estimated_cost=prediction.estimated_cost,
            status=MaintenanceStatus.SCHEDULED
        )

        self.db.add(schedule)

        # 예측에 스케줄 연결
        prediction.is_scheduled = True
        prediction.scheduled_maintenance_id = schedule.id

        self.db.commit()
        self.db.refresh(schedule)

        return {
            "schedule_id": schedule.id,
            "vehicle_id": schedule.vehicle_id,
            "scheduled_date": schedule.scheduled_date.isoformat(),
            "estimated_cost": schedule.estimated_cost,
            "status": schedule.status,
            "prediction_id": prediction_id
        }

    async def _get_required_parts(self, component: str) -> List[Dict[str, Any]]:
        """부품별 필요 부품 조회"""
        component_parts = {
            "engine": ["engine_oil", "oil_filter", "air_filter"],
            "transmission": ["transmission_oil", "transmission_filter"],
            "brake_system": ["brake_pad", "brake_fluid"],
            "suspension": ["shock_absorber"],
            "battery": ["battery"],
            "tire": ["tire"]
        }

        parts = component_parts.get(component, [])
        
        return [
            {
                "part_name": part,
                "quantity": 1,
                "in_stock": random.choice([True, False])
            }
            for part in parts
        ]

    async def get_maintenance_statistics(self) -> Dict[str, Any]:
        """정비 통계"""
        # 활성 예측 수
        active_predictions = self.db.query(func.count(MaintenancePrediction.id)).filter(
            MaintenancePrediction.is_active == True
        ).scalar()

        # 스케줄된 정비 수
        scheduled_maintenance = self.db.query(func.count(MaintenanceSchedule.id)).filter(
            MaintenanceSchedule.status == MaintenanceStatus.SCHEDULED
        ).scalar()

        # 고위험 차량 수 (overall_score < 60)
        high_risk_vehicles = self.db.query(func.count(VehicleHealth.id)).filter(
            VehicleHealth.overall_score < 60
        ).scalar()

        # 최근 30일 정비 완료 수
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        completed_maintenance = self.db.query(func.count(MaintenanceRecord.id)).filter(
            and_(
                MaintenanceRecord.status == MaintenanceStatus.COMPLETED,
                MaintenanceRecord.completed_at >= cutoff_date
            )
        ).scalar()

        return {
            "active_predictions": active_predictions or 0,
            "scheduled_maintenance": scheduled_maintenance or 0,
            "high_risk_vehicles": high_risk_vehicles or 0,
            "completed_maintenance_30d": completed_maintenance or 0
        }

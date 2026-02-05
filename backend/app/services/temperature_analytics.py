"""
Temperature Analytics Service
온도 분석 및 고급 리포팅 서비스
Phase 3-A Part 5: 고급 분석 대시보드
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, case
import statistics
import logging

from app.models.uvis_gps import VehicleTemperatureLog
from app.models.vehicle_location import TemperatureAlert
from app.models.vehicle import Vehicle
from app.models.dispatch import Dispatch

logger = logging.getLogger(__name__)


class TemperatureAnalytics:
    """온도 분석 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        vehicle_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        온도 준수 보고서
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            vehicle_id: 차량 ID (optional)
            
        Returns:
            준수율, 위반 건수, 세부 내역
        """
        # 온도 로그 조회
        query = self.db.query(VehicleTemperatureLog).filter(
            and_(
                VehicleTemperatureLog.created_at >= start_date,
                VehicleTemperatureLog.created_at <= end_date
            )
        )
        
        if vehicle_id:
            query = query.filter(VehicleTemperatureLog.vehicle_id == vehicle_id)
        
        logs = query.all()
        
        if not logs:
            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "compliance_rate": 100.0,
                "total_records": 0,
                "compliant_records": 0,
                "violation_records": 0,
                "violations": []
            }
        
        # 준수/위반 분석
        total_records = len(logs)
        violations = []
        
        for log in logs:
            vehicle = log.vehicle
            if not vehicle:
                continue
            
            vehicle_type = vehicle.vehicle_type
            
            # Sensor A 체크
            if log.temperature_a is not None:
                violation = self._check_compliance(
                    temperature=log.temperature_a,
                    vehicle_type=vehicle_type,
                    sensor="A"
                )
                if violation:
                    violations.append({
                        "timestamp": log.created_at.isoformat(),
                        "vehicle_id": log.vehicle_id,
                        "vehicle_number": vehicle.plate_number,
                        "sensor": "A",
                        "temperature": log.temperature_a,
                        "violation_type": violation,
                        "latitude": log.latitude,
                        "longitude": log.longitude
                    })
            
            # Sensor B 체크
            if log.temperature_b is not None:
                violation = self._check_compliance(
                    temperature=log.temperature_b,
                    vehicle_type=vehicle_type,
                    sensor="B"
                )
                if violation:
                    violations.append({
                        "timestamp": log.created_at.isoformat(),
                        "vehicle_id": log.vehicle_id,
                        "vehicle_number": vehicle.plate_number,
                        "sensor": "B",
                        "temperature": log.temperature_b,
                        "violation_type": violation,
                        "latitude": log.latitude,
                        "longitude": log.longitude
                    })
        
        violation_records = len(violations)
        compliant_records = total_records - violation_records
        compliance_rate = (compliant_records / total_records * 100) if total_records > 0 else 100.0
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "compliance_rate": round(compliance_rate, 2),
            "total_records": total_records,
            "compliant_records": compliant_records,
            "violation_records": violation_records,
            "violations": violations[:100],  # Limit to 100 violations
            "violation_summary": self._summarize_violations(violations)
        }
    
    def _check_compliance(
        self,
        temperature: float,
        vehicle_type: str,
        sensor: str
    ) -> Optional[str]:
        """온도 준수 여부 체크"""
        if vehicle_type == "냉동":
            if temperature < -25.0:
                return "TOO_COLD"
            elif temperature > -15.0:
                return "TOO_HOT"
        elif vehicle_type == "냉장":
            if temperature < 0.0:
                return "TOO_COLD"
            elif temperature > 5.0:
                return "TOO_HOT"
        
        return None
    
    def _summarize_violations(self, violations: List[Dict]) -> Dict[str, Any]:
        """위반 요약"""
        if not violations:
            return {
                "by_type": {},
                "by_vehicle": {},
                "by_sensor": {}
            }
        
        by_type = {}
        by_vehicle = {}
        by_sensor = {}
        
        for v in violations:
            # By violation type
            v_type = v["violation_type"]
            by_type[v_type] = by_type.get(v_type, 0) + 1
            
            # By vehicle
            v_num = v["vehicle_number"]
            by_vehicle[v_num] = by_vehicle.get(v_num, 0) + 1
            
            # By sensor
            sensor = v["sensor"]
            by_sensor[sensor] = by_sensor.get(sensor, 0) + 1
        
        return {
            "by_type": by_type,
            "by_vehicle": by_vehicle,
            "by_sensor": by_sensor
        }
    
    def get_vehicle_performance_score(
        self,
        vehicle_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        차량 온도 성능 점수
        
        Args:
            vehicle_id: 차량 ID
            days: 분석 기간 (일)
            
        Returns:
            성능 점수, 등급, 세부 지표
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 온도 로그 조회
        logs = self.db.query(VehicleTemperatureLog).filter(
            and_(
                VehicleTemperatureLog.vehicle_id == vehicle_id,
                VehicleTemperatureLog.created_at >= start_date
            )
        ).all()
        
        if not logs:
            return {
                "vehicle_id": vehicle_id,
                "score": 0,
                "grade": "N/A",
                "metrics": {},
                "message": "No data available"
            }
        
        # 성능 지표 계산
        metrics = self._calculate_performance_metrics(logs)
        
        # 점수 계산 (100점 만점)
        score = self._calculate_performance_score(metrics)
        
        # 등급 결정
        grade = self._determine_grade(score)
        
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        
        return {
            "vehicle_id": vehicle_id,
            "vehicle_number": vehicle.plate_number if vehicle else None,
            "period_days": days,
            "score": round(score, 2),
            "grade": grade,
            "metrics": metrics,
            "recommendations": self._generate_recommendations(metrics, score)
        }
    
    def _calculate_performance_metrics(self, logs: List[VehicleTemperatureLog]) -> Dict[str, Any]:
        """성능 지표 계산"""
        temps_a = [log.temperature_a for log in logs if log.temperature_a is not None]
        temps_b = [log.temperature_b for log in logs if log.temperature_b is not None]
        
        # 온도 안정성 (표준편차가 낮을수록 좋음)
        stability_a = statistics.stdev(temps_a) if len(temps_a) > 1 else 0
        stability_b = statistics.stdev(temps_b) if len(temps_b) > 1 else 0
        
        # 온도 범위 준수율
        compliant_a = sum(1 for t in temps_a if -25 <= t <= -15)
        compliant_b = sum(1 for t in temps_b if -25 <= t <= -15)
        compliance_rate_a = (compliant_a / len(temps_a) * 100) if temps_a else 100
        compliance_rate_b = (compliant_b / len(temps_b) * 100) if temps_b else 100
        
        # 평균 온도
        avg_temp_a = statistics.mean(temps_a) if temps_a else None
        avg_temp_b = statistics.mean(temps_b) if temps_b else None
        
        # 데이터 수집률 (예상 288개/일 = 5분마다)
        expected_records = len(logs) / (288 * (len(logs) / 288))  # Simplified
        data_collection_rate = min(100, (len(logs) / expected_records * 100)) if expected_records > 0 else 0
        
        return {
            "total_records": len(logs),
            "sensor_a": {
                "avg_temperature": round(avg_temp_a, 2) if avg_temp_a else None,
                "stability": round(stability_a, 2),
                "compliance_rate": round(compliance_rate_a, 2),
                "sample_count": len(temps_a)
            },
            "sensor_b": {
                "avg_temperature": round(avg_temp_b, 2) if avg_temp_b else None,
                "stability": round(stability_b, 2),
                "compliance_rate": round(compliance_rate_b, 2),
                "sample_count": len(temps_b)
            },
            "data_collection_rate": round(data_collection_rate, 2)
        }
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """성능 점수 계산 (100점 만점)"""
        score = 0.0
        
        # 1. 준수율 (40점)
        compliance_a = metrics["sensor_a"]["compliance_rate"]
        compliance_b = metrics["sensor_b"]["compliance_rate"]
        avg_compliance = (compliance_a + compliance_b) / 2
        score += (avg_compliance / 100) * 40
        
        # 2. 안정성 (30점) - 표준편차가 1.0 이하면 만점
        stability_a = metrics["sensor_a"]["stability"]
        stability_b = metrics["sensor_b"]["stability"]
        avg_stability = (stability_a + stability_b) / 2
        stability_score = max(0, 30 - (avg_stability * 10))
        score += stability_score
        
        # 3. 데이터 수집률 (20점)
        data_rate = metrics["data_collection_rate"]
        score += (data_rate / 100) * 20
        
        # 4. 온도 최적성 (10점) - 이상적인 온도에 가까울수록 높음
        if metrics["sensor_a"]["avg_temperature"]:
            temp_a = metrics["sensor_a"]["avg_temperature"]
            # 이상적인 온도: -20°C
            deviation_a = abs(temp_a - (-20.0))
            temp_score_a = max(0, 5 - deviation_a)
            score += temp_score_a
        
        if metrics["sensor_b"]["avg_temperature"]:
            temp_b = metrics["sensor_b"]["avg_temperature"]
            deviation_b = abs(temp_b - (-20.0))
            temp_score_b = max(0, 5 - deviation_b)
            score += temp_score_b
        
        return min(100, score)
    
    def _determine_grade(self, score: float) -> str:
        """등급 결정"""
        if score >= 90:
            return "A+ (탁월)"
        elif score >= 80:
            return "A (우수)"
        elif score >= 70:
            return "B+ (양호)"
        elif score >= 60:
            return "B (보통)"
        elif score >= 50:
            return "C (미흡)"
        else:
            return "D (불량)"
    
    def _generate_recommendations(self, metrics: Dict[str, Any], score: float) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        # 준수율 체크
        compliance_a = metrics["sensor_a"]["compliance_rate"]
        compliance_b = metrics["sensor_b"]["compliance_rate"]
        
        if compliance_a < 95:
            recommendations.append(f"Sensor A 온도 준수율이 {compliance_a}%입니다. 냉동기 점검이 필요합니다.")
        if compliance_b < 95:
            recommendations.append(f"Sensor B 온도 준수율이 {compliance_b}%입니다. 냉동기 점검이 필요합니다.")
        
        # 안정성 체크
        stability_a = metrics["sensor_a"]["stability"]
        stability_b = metrics["sensor_b"]["stability"]
        
        if stability_a > 2.0:
            recommendations.append(f"Sensor A 온도 변동이 큽니다 (σ={stability_a}). 냉동기 성능 점검이 필요합니다.")
        if stability_b > 2.0:
            recommendations.append(f"Sensor B 온도 변동이 큽니다 (σ={stability_b}). 냉동기 성능 점검이 필요합니다.")
        
        # 데이터 수집률 체크
        data_rate = metrics["data_collection_rate"]
        if data_rate < 80:
            recommendations.append(f"데이터 수집률이 {data_rate}%로 낮습니다. GPS 장치 점검이 필요합니다.")
        
        # 전체 점수 기반 권장사항
        if score < 60:
            recommendations.append("⚠️ 전반적인 온도 관리 성능이 낮습니다. 종합 점검이 필요합니다.")
        elif score >= 90:
            recommendations.append("✅ 온도 관리가 매우 우수합니다. 현재 수준을 유지하세요.")
        
        return recommendations if recommendations else ["✅ 온도 관리가 양호합니다."]
    
    def detect_temperature_anomalies(
        self,
        vehicle_id: int,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        온도 이상 패턴 감지
        
        Args:
            vehicle_id: 차량 ID
            hours: 분석 기간 (시간)
            
        Returns:
            이상 패턴 리스트
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        logs = self.db.query(VehicleTemperatureLog).filter(
            and_(
                VehicleTemperatureLog.vehicle_id == vehicle_id,
                VehicleTemperatureLog.created_at >= start_time
            )
        ).order_by(VehicleTemperatureLog.created_at).all()
        
        if len(logs) < 10:
            return []
        
        anomalies = []
        
        # 1. 급격한 온도 변화 감지 (5°C 이상 변화)
        for i in range(1, len(logs)):
            prev_log = logs[i-1]
            curr_log = logs[i]
            
            if prev_log.temperature_a and curr_log.temperature_a:
                temp_diff = abs(curr_log.temperature_a - prev_log.temperature_a)
                if temp_diff > 5.0:
                    anomalies.append({
                        "type": "RAPID_CHANGE",
                        "sensor": "A",
                        "timestamp": curr_log.created_at.isoformat(),
                        "temperature_before": prev_log.temperature_a,
                        "temperature_after": curr_log.temperature_a,
                        "change": temp_diff,
                        "severity": "HIGH" if temp_diff > 10 else "MEDIUM"
                    })
            
            if prev_log.temperature_b and curr_log.temperature_b:
                temp_diff = abs(curr_log.temperature_b - prev_log.temperature_b)
                if temp_diff > 5.0:
                    anomalies.append({
                        "type": "RAPID_CHANGE",
                        "sensor": "B",
                        "timestamp": curr_log.created_at.isoformat(),
                        "temperature_before": prev_log.temperature_b,
                        "temperature_after": curr_log.temperature_b,
                        "change": temp_diff,
                        "severity": "HIGH" if temp_diff > 10 else "MEDIUM"
                    })
        
        # 2. 장시간 이상 온도 유지 감지
        temps_a = [log.temperature_a for log in logs if log.temperature_a is not None]
        if temps_a:
            avg_temp_a = statistics.mean(temps_a)
            # 평균에서 3°C 이상 벗어난 경우가 30분 이상 지속
            consecutive_count = 0
            for log in logs:
                if log.temperature_a and abs(log.temperature_a - avg_temp_a) > 3.0:
                    consecutive_count += 1
                else:
                    consecutive_count = 0
                
                if consecutive_count >= 6:  # 30분 (5분 * 6)
                    anomalies.append({
                        "type": "PROLONGED_DEVIATION",
                        "sensor": "A",
                        "timestamp": log.created_at.isoformat(),
                        "temperature": log.temperature_a,
                        "expected": avg_temp_a,
                        "deviation": abs(log.temperature_a - avg_temp_a),
                        "severity": "MEDIUM"
                    })
                    consecutive_count = 0  # Reset after detection
        
        return anomalies
    
    def get_fleet_temperature_overview(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        전체 차량 온도 현황 요약
        
        Args:
            hours: 분석 기간 (시간)
            
        Returns:
            전체 차량 요약 통계
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # 차량별 최신 온도
        vehicles = self.db.query(Vehicle).all()
        
        vehicle_status = []
        for vehicle in vehicles:
            latest_log = self.db.query(VehicleTemperatureLog).filter(
                VehicleTemperatureLog.vehicle_id == vehicle.id
            ).order_by(desc(VehicleTemperatureLog.created_at)).first()
            
            if latest_log:
                status = "NORMAL"
                if vehicle.vehicle_type == "냉동":
                    if latest_log.temperature_a and (latest_log.temperature_a < -25 or latest_log.temperature_a > -15):
                        status = "VIOLATION"
                
                vehicle_status.append({
                    "vehicle_id": vehicle.id,
                    "vehicle_number": vehicle.plate_number,
                    "vehicle_type": vehicle.vehicle_type,
                    "temperature_a": latest_log.temperature_a,
                    "temperature_b": latest_log.temperature_b,
                    "status": status,
                    "last_updated": latest_log.created_at.isoformat()
                })
        
        # 알림 통계
        total_alerts = self.db.query(func.count(TemperatureAlert.id)).filter(
            TemperatureAlert.detected_at >= start_time
        ).scalar()
        
        critical_alerts = self.db.query(func.count(TemperatureAlert.id)).filter(
            and_(
                TemperatureAlert.detected_at >= start_time,
                TemperatureAlert.severity == "CRITICAL"
            )
        ).scalar()
        
        # 상태별 차량 수
        normal_count = sum(1 for v in vehicle_status if v["status"] == "NORMAL")
        violation_count = sum(1 for v in vehicle_status if v["status"] == "VIOLATION")
        
        return {
            "period_hours": hours,
            "total_vehicles": len(vehicles),
            "normal_vehicles": normal_count,
            "violation_vehicles": violation_count,
            "total_alerts": total_alerts,
            "critical_alerts": critical_alerts,
            "vehicle_status": vehicle_status,
            "summary": {
                "compliance_rate": round((normal_count / len(vehicles) * 100) if vehicles else 100, 2),
                "alert_rate": round((total_alerts / len(vehicles)) if vehicles else 0, 2)
            }
        }
    
    def get_temperature_trends(
        self,
        vehicle_id: Optional[int] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        온도 트렌드 분석
        
        Args:
            vehicle_id: 차량 ID (optional)
            days: 분석 기간 (일)
            
        Returns:
            일별 온도 트렌드
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(
            func.date(VehicleTemperatureLog.created_at).label("date"),
            func.avg(VehicleTemperatureLog.temperature_a).label("avg_temp_a"),
            func.min(VehicleTemperatureLog.temperature_a).label("min_temp_a"),
            func.max(VehicleTemperatureLog.temperature_a).label("max_temp_a"),
            func.count(VehicleTemperatureLog.id).label("record_count")
        ).filter(
            VehicleTemperatureLog.created_at >= start_date
        )
        
        if vehicle_id:
            query = query.filter(VehicleTemperatureLog.vehicle_id == vehicle_id)
        
        results = query.group_by(func.date(VehicleTemperatureLog.created_at)).order_by("date").all()
        
        trends = []
        for result in results:
            trends.append({
                "date": str(result.date),
                "avg_temperature": round(float(result.avg_temp_a), 2) if result.avg_temp_a else None,
                "min_temperature": round(float(result.min_temp_a), 2) if result.min_temp_a else None,
                "max_temperature": round(float(result.max_temp_a), 2) if result.max_temp_a else None,
                "record_count": result.record_count
            })
        
        return {
            "period_days": days,
            "vehicle_id": vehicle_id,
            "trends": trends
        }

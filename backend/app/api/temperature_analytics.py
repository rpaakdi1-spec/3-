"""
Temperature Analytics API
온도 분석 및 고급 리포팅 API
Phase 3-A Part 5: 고급 분석 대시보드
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.temperature_analytics import TemperatureAnalytics
from app.services.temperature_report_export import TemperatureReportExporter


router = APIRouter(prefix="/temperature-analytics", tags=["Temperature Analytics"])


# ============= Schemas =============

class ComplianceReportResponse(BaseModel):
    """준수 보고서 응답"""
    period: dict
    compliance_rate: float
    total_records: int
    compliant_records: int
    violation_records: int
    violations: list
    violation_summary: dict


class VehiclePerformanceResponse(BaseModel):
    """차량 성능 응답"""
    vehicle_id: int
    vehicle_number: Optional[str]
    period_days: int
    score: float
    grade: str
    metrics: dict
    recommendations: list


class FleetOverviewResponse(BaseModel):
    """전체 차량 현황 응답"""
    period_hours: int
    total_vehicles: int
    normal_vehicles: int
    violation_vehicles: int
    total_alerts: int
    critical_alerts: int
    vehicle_status: list
    summary: dict


# ============= Endpoints =============

@router.get("/compliance-report", response_model=ComplianceReportResponse)
async def get_compliance_report(
    days: int = Query(7, ge=1, le=90, description="보고 기간 (일, 최대 90일)"),
    vehicle_id: Optional[int] = Query(None, description="차량 ID (optional)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    온도 준수 보고서
    
    - 기간별 온도 준수율 분석
    - 위반 건수 및 세부 내역
    - 차량별/센서별 위반 요약
    
    **사용 시나리오:**
    - 주간/월간 온도 관리 보고서
    - 식품안전법 감사 대응
    - 온도 관리 개선 계획 수립
    """
    analytics = TemperatureAnalytics(db)
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    report = analytics.get_compliance_report(start_date, end_date, vehicle_id)
    return report


@router.get("/vehicles/{vehicle_id}/performance", response_model=VehiclePerformanceResponse)
async def get_vehicle_performance(
    vehicle_id: int,
    days: int = Query(30, ge=7, le=90, description="분석 기간 (일, 최대 90일)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    차량 온도 성능 점수
    
    - 온도 준수율, 안정성, 데이터 수집률 종합 평가
    - 100점 만점 점수 및 등급 (A+, A, B+, B, C, D)
    - 개선 권장사항 제공
    
    **평가 기준:**
    - 준수율 (40점): 온도 범위 준수 비율
    - 안정성 (30점): 온도 변동 안정성 (표준편차)
    - 데이터 수집률 (20점): 예상 대비 실제 수집률
    - 온도 최적성 (10점): 이상적인 온도 유지
    """
    analytics = TemperatureAnalytics(db)
    performance = analytics.get_vehicle_performance_score(vehicle_id, days)
    return performance


@router.get("/vehicles/{vehicle_id}/anomalies")
async def detect_vehicle_anomalies(
    vehicle_id: int,
    hours: int = Query(24, ge=1, le=168, description="분석 기간 (시간, 최대 7일)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    온도 이상 패턴 감지
    
    - 급격한 온도 변화 감지 (5°C 이상)
    - 장시간 이상 온도 유지 감지
    - 이상 패턴 분류 및 심각도 평가
    
    **감지 패턴:**
    - RAPID_CHANGE: 급격한 온도 변화
    - PROLONGED_DEVIATION: 장시간 정상 범위 이탈
    """
    analytics = TemperatureAnalytics(db)
    anomalies = analytics.detect_temperature_anomalies(vehicle_id, hours)
    
    return {
        "vehicle_id": vehicle_id,
        "period_hours": hours,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies
    }


@router.get("/fleet-overview", response_model=FleetOverviewResponse)
async def get_fleet_overview(
    hours: int = Query(24, ge=1, le=168, description="분석 기간 (시간)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    전체 차량 온도 현황 요약
    
    - 전체 차량 온도 상태
    - 정상/위반 차량 수
    - 알림 발생 통계
    - 준수율 및 알림율
    
    **사용 시나리오:**
    - 실시간 차량 온도 모니터링
    - 관리자 대시보드
    - 일일 운영 보고
    """
    analytics = TemperatureAnalytics(db)
    overview = analytics.get_fleet_temperature_overview(hours)
    return overview


@router.get("/temperature-trends")
async def get_temperature_trends(
    vehicle_id: Optional[int] = Query(None, description="차량 ID (optional)"),
    days: int = Query(7, ge=1, le=90, description="분석 기간 (일)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    온도 트렌드 분석
    
    - 일별 평균/최소/최대 온도
    - 온도 변화 추이 파악
    - 전체 차량 또는 특정 차량 분석
    
    **사용 시나리오:**
    - 온도 관리 트렌드 파악
    - 계절별 온도 패턴 분석
    - 냉동기 성능 모니터링
    """
    analytics = TemperatureAnalytics(db)
    trends = analytics.get_temperature_trends(vehicle_id, days)
    return trends


@router.get("/top-performers")
async def get_top_performers(
    days: int = Query(30, ge=7, le=90, description="분석 기간 (일)"),
    limit: int = Query(10, ge=1, le=50, description="결과 수 제한"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    온도 관리 우수 차량 순위
    
    - 성능 점수 기준 상위 차량
    - 각 차량의 점수 및 등급
    - 우수 사례 공유
    """
    from app.models.vehicle import Vehicle
    
    analytics = TemperatureAnalytics(db)
    vehicles = db.query(Vehicle).all()
    
    performances = []
    for vehicle in vehicles:
        try:
            perf = analytics.get_vehicle_performance_score(vehicle.id, days)
            performances.append(perf)
        except Exception as e:
            continue
    
    # 점수 기준 정렬
    performances.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "period_days": days,
        "total_vehicles": len(vehicles),
        "top_performers": performances[:limit]
    }


@router.get("/worst-performers")
async def get_worst_performers(
    days: int = Query(30, ge=7, le=90, description="분석 기간 (일)"),
    limit: int = Query(10, ge=1, le=50, description="결과 수 제한"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    온도 관리 개선 필요 차량 순위
    
    - 성능 점수 기준 하위 차량
    - 각 차량의 문제점 및 권장사항
    - 우선 조치 대상 식별
    """
    from app.models.vehicle import Vehicle
    
    analytics = TemperatureAnalytics(db)
    vehicles = db.query(Vehicle).all()
    
    performances = []
    for vehicle in vehicles:
        try:
            perf = analytics.get_vehicle_performance_score(vehicle.id, days)
            performances.append(perf)
        except Exception as e:
            continue
    
    # 점수 기준 정렬 (낮은 순)
    performances.sort(key=lambda x: x["score"])
    
    return {
        "period_days": days,
        "total_vehicles": len(vehicles),
        "worst_performers": performances[:limit]
    }


@router.get("/analytics-summary")
async def get_analytics_summary(
    days: int = Query(7, ge=1, le=90, description="분석 기간 (일)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    종합 분석 요약
    
    - 전체 준수율
    - 평균 차량 성능 점수
    - 주요 통계 지표
    - 전반적인 온도 관리 상태
    """
    from app.models.vehicle import Vehicle
    
    analytics = TemperatureAnalytics(db)
    
    # 준수 보고서
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    compliance = analytics.get_compliance_report(start_date, end_date)
    
    # 차량 성능 점수
    vehicles = db.query(Vehicle).all()
    scores = []
    for vehicle in vehicles:
        try:
            perf = analytics.get_vehicle_performance_score(vehicle.id, days)
            scores.append(perf["score"])
        except:
            continue
    
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Fleet overview
    fleet = analytics.get_fleet_temperature_overview(24)
    
    return {
        "period_days": days,
        "compliance": {
            "rate": compliance["compliance_rate"],
            "total_records": compliance["total_records"],
            "violations": compliance["violation_records"]
        },
        "performance": {
            "avg_score": round(avg_score, 2),
            "total_vehicles": len(vehicles),
            "scored_vehicles": len(scores)
        },
        "fleet_status": {
            "normal_vehicles": fleet["normal_vehicles"],
            "violation_vehicles": fleet["violation_vehicles"],
            "total_alerts": fleet["total_alerts"],
            "critical_alerts": fleet["critical_alerts"]
        },
        "overall_grade": _calculate_overall_grade(compliance["compliance_rate"], avg_score),
        "key_insights": _generate_key_insights(compliance, avg_score, fleet)
    }


def _calculate_overall_grade(compliance_rate: float, avg_score: float) -> str:
    """전반적인 등급 계산"""
    combined_score = (compliance_rate + avg_score) / 2
    
    if combined_score >= 90:
        return "A+ (탁월)"
    elif combined_score >= 80:
        return "A (우수)"
    elif combined_score >= 70:
        return "B+ (양호)"
    elif combined_score >= 60:
        return "B (보통)"
    elif combined_score >= 50:
        return "C (미흡)"
    else:
        return "D (불량)"


def _generate_key_insights(compliance: dict, avg_score: float, fleet: dict) -> list:
    """주요 인사이트 생성"""
    insights = []
    
    # 준수율 인사이트
    compliance_rate = compliance["compliance_rate"]
    if compliance_rate >= 95:
        insights.append(f"✅ 온도 준수율이 {compliance_rate}%로 매우 우수합니다.")
    elif compliance_rate >= 90:
        insights.append(f"✅ 온도 준수율이 {compliance_rate}%로 양호합니다.")
    else:
        insights.append(f"⚠️ 온도 준수율이 {compliance_rate}%로 개선이 필요합니다.")
    
    # 성능 점수 인사이트
    if avg_score >= 80:
        insights.append(f"✅ 차량 평균 성능 점수가 {avg_score:.1f}점으로 우수합니다.")
    elif avg_score >= 60:
        insights.append(f"📊 차량 평균 성능 점수가 {avg_score:.1f}점입니다.")
    else:
        insights.append(f"⚠️ 차량 평균 성능 점수가 {avg_score:.1f}점으로 낮습니다. 점검이 필요합니다.")
    
    # 알림 인사이트
    critical_alerts = fleet["critical_alerts"]
    if critical_alerts > 0:
        insights.append(f"🚨 최근 24시간 내 Critical 알림이 {critical_alerts}건 발생했습니다.")
    else:
        insights.append(f"✅ 최근 24시간 내 Critical 알림이 없습니다.")
    
    # 위반 차량 인사이트
    violation_vehicles = fleet["violation_vehicles"]
    if violation_vehicles > 0:
        insights.append(f"⚠️ 현재 {violation_vehicles}대의 차량이 온도 기준을 벗어났습니다.")
    
    return insights


@router.get("/export/compliance-report")
async def export_compliance_report(
    days: int = Query(7, ge=1, le=90, description="보고 기간 (일)"),
    vehicle_id: Optional[int] = Query(None, description="차량 ID (optional)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    준수 보고서 엑셀 다운로드
    
    - 요약, 위반 내역, 차량별 통계 포함
    - 엑셀 파일 형식 (.xlsx)
    """
    exporter = TemperatureReportExporter(db)
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    excel_file = exporter.generate_compliance_report(start_date, end_date, vehicle_id)
    
    filename = f"compliance_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/export/performance-report")
async def export_performance_report(
    days: int = Query(30, ge=7, le=90, description="분석 기간 (일)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    차량 성능 보고서 엑셀 다운로드
    
    - 차량별 성능 점수 및 순위
    - 성능 지표 및 권장사항 포함
    - 엑셀 파일 형식 (.xlsx)
    """
    exporter = TemperatureReportExporter(db)
    excel_file = exporter.generate_performance_report(days)
    
    filename = f"performance_report_{days}days_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

from __future__ import annotations
"""
Analytics schemas for dispatch statistics and dashboard
"""
from pydantic import BaseModel, Field
from datetime import date as date_type, datetime
from typing import List, Optional
from decimal import Decimal


# ===== 배차 통계 =====

class DispatchStatistics(BaseModel):
    """배차 통계"""
    date: date_type = Field(..., description="날짜")
    total_dispatches: int = Field(..., description="총 배차 건수")
    total_orders: int = Field(..., description="총 주문 건수")
    total_pallets: int = Field(..., description="총 팔레트 수")
    total_weight_kg: float = Field(..., description="총 중량 (kg)")
    total_distance_km: Optional[float] = Field(None, description="총 주행 거리 (km)")
    unique_vehicles: int = Field(..., description="투입 차량 수")
    unique_clients: int = Field(..., description="배송 거래처 수")
    avg_pallets_per_dispatch: float = Field(..., description="배차당 평균 팔레트 수")
    


class PeriodStatistics(BaseModel):
    """기간별 통계"""
    period: str = Field(..., description="기간 (daily/weekly/monthly)")
    start_date: date_type = Field(..., description="시작 날짜")
    end_date: date_type = Field(..., description="종료 날짜")
    statistics: List[DispatchStatistics] = Field(..., description="통계 데이터")
    summary: dict = Field(..., description="요약 통계")
    


# ===== 차량별 운행 분석 =====

class VehiclePerformance(BaseModel):
    """차량별 운행 성과"""
    vehicle_id: int = Field(..., description="차량 ID")
    vehicle_code: str = Field(..., description="차량 번호")
    vehicle_type: str = Field(..., description="차량 종류")
    total_dispatches: int = Field(..., description="총 배차 횟수")
    total_distance_km: float = Field(..., description="총 주행 거리 (km)")
    total_orders: int = Field(..., description="총 주문 건수")
    total_pallets: int = Field(..., description="총 팔레트 수")
    total_weight_kg: float = Field(..., description="총 중량 (kg)")
    avg_pallets_per_dispatch: float = Field(..., description="배차당 평균 팔레트")
    avg_distance_per_dispatch: float = Field(..., description="배차당 평균 거리 (km)")
    capacity_utilization: float = Field(..., description="평균 적재율 (%)")
    


class VehicleAnalytics(BaseModel):
    """차량 분석 응답"""
    period: str = Field(..., description="분석 기간")
    start_date: date_type = Field(..., description="시작 날짜")
    end_date: date_type = Field(..., description="종료 날짜")
    vehicles: List[VehiclePerformance] = Field(..., description="차량별 성과")
    summary: dict = Field(..., description="전체 요약")


# ===== 거래처별 배송 통계 =====

class ClientDeliveryStats(BaseModel):
    """거래처별 배송 통계"""
    client_id: int = Field(..., description="거래처 ID")
    client_code: str = Field(..., description="거래처 코드")
    client_name: str = Field(..., description="거래처명")
    client_type: str = Field(..., description="거래처 유형")
    total_orders: int = Field(..., description="총 주문 건수")
    total_pallets: int = Field(..., description="총 팔레트 수")
    total_weight_kg: float = Field(..., description="총 중량 (kg)")
    delivery_frequency: float = Field(..., description="배송 빈도 (회/월)")
    avg_pallets_per_order: float = Field(..., description="주문당 평균 팔레트")
    region: Optional[str] = Field(None, description="지역")
    


class ClientAnalytics(BaseModel):
    """거래처 분석 응답"""
    period: str = Field(..., description="분석 기간")
    start_date: date_type = Field(..., description="시작 날짜")
    end_date: date_type = Field(..., description="종료 날짜")
    clients: List[ClientDeliveryStats] = Field(..., description="거래처별 통계")
    summary: dict = Field(..., description="전체 요약")


# ===== 지역별 배송 분포 =====

class RegionDistribution(BaseModel):
    """지역별 배송 분포"""
    region: str = Field(..., description="지역명")
    total_orders: int = Field(..., description="총 주문 건수")
    total_pallets: int = Field(..., description="총 팔레트 수")
    total_weight_kg: float = Field(..., description="총 중량 (kg)")
    unique_clients: int = Field(..., description="거래처 수")
    percentage: float = Field(..., description="비율 (%)")


# ===== 대시보드 요약 =====

class DashboardSummary(BaseModel):
    """대시보드 요약 통계"""
    today: date_type = Field(..., description="기준 날짜")
    
    # 오늘 통계
    today_dispatches: int = Field(..., description="오늘 배차 건수")
    today_orders: int = Field(..., description="오늘 주문 건수")
    today_pallets: int = Field(..., description="오늘 팔레트 수")
    
    # 이번 주 통계
    week_dispatches: int = Field(..., description="이번 주 배차 건수")
    week_orders: int = Field(..., description="이번 주 주문 건수")
    week_distance_km: float = Field(..., description="이번 주 총 주행 거리")
    
    # 이번 달 통계
    month_dispatches: int = Field(..., description="이번 달 배차 건수")
    month_orders: int = Field(..., description="이번 달 주문 건수")
    month_pallets: int = Field(..., description="이번 달 팔레트 수")
    
    # 차량 통계
    active_vehicles: int = Field(..., description="활성 차량 수")
    total_vehicles: int = Field(..., description="전체 차량 수")
    
    # 거래처 통계
    active_clients: int = Field(..., description="활성 거래처 수")
    total_clients: int = Field(..., description="전체 거래처 수")
    
    # 전월 대비 증감율
    dispatch_growth_rate: float = Field(..., description="배차 증감율 (%)")
    order_growth_rate: float = Field(..., description="주문 증감율 (%)")


# ===== Excel Export =====

class ExcelExportRequest(BaseModel):
    """Excel 내보내기 요청"""
    start_date: date_type = Field(..., description="시작 날짜")
    end_date: date_type = Field(..., description="종료 날짜")
    include_routes: bool = Field(True, description="경로 정보 포함 여부")
    include_statistics: bool = Field(True, description="통계 포함 여부")


class ExcelExportResponse(BaseModel):
    """Excel 내보내기 응답"""
    filename: str = Field(..., description="파일명")
    download_url: str = Field(..., description="다운로드 URL")
    file_size_bytes: int = Field(..., description="파일 크기 (bytes)")
    created_at: datetime = Field(..., description="생성 시각")

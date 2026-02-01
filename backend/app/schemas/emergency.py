"""긴급정비 관련 스키마"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class EmergencyReportCreate(BaseModel):
    """긴급정비 신고"""
    emergency_type: str = Field(..., description="긴급 유형: breakdown, malfunction, accident, other")
    severity: str = Field(..., description="긴급도: critical, warning, minor")
    description: str = Field(..., description="상황 설명")
    location: Optional[str] = Field(None, description="발생 위치")
    estimated_repair_time: Optional[int] = Field(None, description="예상 수리 시간(분)")


class AffectedDispatch(BaseModel):
    """영향받는 배차"""
    dispatch_id: str
    order_number: str
    pickup_time: str
    delay_estimate: int  # 분
    customer_name: str


class RecommendedVehicle(BaseModel):
    """추천 대체 차량"""
    vehicle_id: int
    code: str
    plate_number: str
    vehicle_type: str
    distance_km: float
    availability: bool
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None


class EmergencyResponse(BaseModel):
    """긴급정비 신고 응답"""
    success: bool
    vehicle_id: int
    emergency_id: str
    affected_dispatches: List[AffectedDispatch]
    recommended_vehicles: List[RecommendedVehicle]
    message: str


class DispatchReassignRequest(BaseModel):
    """배차 재조정 요청"""
    broken_vehicle_id: int
    replacement_vehicle_id: int
    dispatch_ids: List[str]
    notify_customers: bool = True


class ReassignedDispatch(BaseModel):
    """재조정된 배차"""
    dispatch_id: str
    order_number: str
    original_vehicle: str
    new_vehicle: str
    customer_notified: bool


class DispatchReassignResponse(BaseModel):
    """배차 재조정 응답"""
    success: bool
    reassigned_count: int
    dispatches: List[ReassignedDispatch]
    message: str


class EmergencyListItem(BaseModel):
    """긴급 상황 목록 항목"""
    vehicle_id: int
    plate_number: str
    emergency_type: str
    severity: str
    reported_at: datetime
    affected_dispatches_count: int
    status: str  # active, resolved, cancelled
    description: str


class EmergencyListResponse(BaseModel):
    """긴급 상황 목록 응답"""
    total: int
    items: List[EmergencyListItem]

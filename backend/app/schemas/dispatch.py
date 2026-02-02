from __future__ import annotations
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.dispatch import DispatchStatus, RouteType


class DispatchRouteResponse(BaseModel):
    """Schema for dispatch route response"""
    id: int
    sequence: int
    route_type: RouteType
    order_id: Optional[int] = None
    location_name: str
    address: str
    latitude: float
    longitude: float
    distance_from_previous_km: Optional[float] = None
    duration_from_previous_minutes: Optional[int] = None
    estimated_arrival_time: Optional[str] = None
    estimated_work_duration_minutes: Optional[int] = None
    estimated_departure_time: Optional[str] = None
    current_pallets: int
    current_weight_kg: float
    notes: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class DispatchBase(BaseModel):
    """Base schema for Dispatch"""
    dispatch_date: date = Field(..., description="배차 일자")
    vehicle_id: int = Field(..., description="차량 ID")
    driver_id: Optional[int] = Field(None, description="기사 ID")
    notes: Optional[str] = Field(None, description="특이사항")


class DispatchCreate(BaseModel):
    """Schema for creating dispatch (via optimization)"""
    order_ids: List[int] = Field(..., description="배차할 주문 ID 목록")
    vehicle_ids: Optional[List[int]] = Field(None, description="사용할 차량 ID 목록 (None=전체)")
    dispatch_date: Optional[str] = Field(None, description="배차 일자 (YYYY-MM-DD)")


class DispatchUpdate(BaseModel):
    """Schema for updating dispatch"""
    dispatch_date: Optional[date] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    status: Optional[DispatchStatus] = None
    notes: Optional[str] = None


class DispatchResponse(BaseModel):
    """Schema for dispatch response"""
    id: int
    dispatch_number: str
    dispatch_date: date
    vehicle_id: int
    driver_id: Optional[int] = None
    total_orders: int
    total_pallets: int
    total_weight_kg: float
    total_distance_km: Optional[float] = None
    empty_distance_km: Optional[float] = None
    estimated_duration_minutes: Optional[int] = None
    estimated_cost: Optional[float] = None
    status: DispatchStatus
    optimization_score: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Vehicle info
    vehicle_code: Optional[str] = None
    vehicle_plate: Optional[str] = None
    
    # Driver info
    driver_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class DispatchDetailResponse(DispatchResponse):
    """Schema for dispatch detail with routes"""
    routes: List[DispatchRouteResponse] = []


class DispatchListResponse(BaseModel):
    """Schema for dispatch list response"""
    total: int
    items: List[DispatchResponse]


class OptimizationRequest(BaseModel):
    """Schema for dispatch optimization request"""
    order_ids: List[int] = Field(..., min_length=1, description="배차할 주문 ID 목록")
    vehicle_ids: Optional[List[int]] = Field(None, description="사용할 차량 ID 목록 (None=전체 사용 가능)")
    dispatch_date: Optional[str] = Field(None, description="배차 일자 (YYYY-MM-DD, None=오늘)")
    


class OptimizationResponse(BaseModel):
    """Schema for optimization response"""
    success: bool
    total_orders: Optional[int] = None
    total_dispatches: Optional[int] = None
    dispatches: Optional[List[dict]] = None
    error: Optional[str] = None


class DispatchConfirmRequest(BaseModel):
    """Schema for confirming dispatch"""
    dispatch_ids: List[int] = Field(..., description="확정할 배차 ID 목록")


class DispatchCompleteRequest(BaseModel):
    """Schema for completing dispatch"""
    dispatch_ids: List[int] = Field(..., description="완료할 배차 ID 목록")


class DispatchCancelRequest(BaseModel):
    """Schema for cancelling dispatch"""
    dispatch_ids: List[int] = Field(..., description="취소할 배차 ID 목록")
    reason: Optional[str] = Field(None, description="취소 사유")


class DispatchStatsResponse(BaseModel):
    """Schema for dispatch statistics"""
    total_dispatches: int
    by_status: dict
    by_date: dict
    total_orders: int
    total_vehicles_used: int
    avg_orders_per_dispatch: float
    avg_pallets_per_dispatch: float

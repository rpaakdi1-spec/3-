"""
ML 모델 API 엔드포인트
- 배송 시간 예측
- 수요 예측
- 모델 훈련 및 관리
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
from loguru import logger

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.delivery_time_prediction_service import get_delivery_time_prediction_service
from app.services.demand_forecasting_service import get_demand_forecasting_service


router = APIRouter()


# Request/Response Models
class DeliveryTimePredictionRequest(BaseModel):
    distance_km: float
    order_quantity_pallets: int
    vehicle_capacity_pallets: int
    dispatch_time: str  # ISO format
    temperature_zone: str  # '냉동', '냉장', '상온'
    order_count: int = 1


class DemandForecastRequest(BaseModel):
    forecast_date: str  # ISO format
    prev_week_orders: Optional[int] = None
    prev_month_orders: Optional[int] = None


# 배송 시간 예측 API
@router.post("/predict/delivery-time")
async def predict_delivery_time(
    request: DeliveryTimePredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배송 시간 예측
    
    Args:
        request: 예측 요청 데이터
        
    Returns:
        예측 결과
    """
    try:
        prediction_service = get_delivery_time_prediction_service(db)
        
        # ISO 시간 파싱
        dispatch_time = datetime.fromisoformat(request.dispatch_time.replace('Z', '+00:00'))
        
        result = prediction_service.predict_delivery_time(
            distance_km=request.distance_km,
            order_quantity_pallets=request.order_quantity_pallets,
            vehicle_capacity_pallets=request.vehicle_capacity_pallets,
            dispatch_time=dispatch_time,
            temperature_zone=request.temperature_zone,
            order_count=request.order_count
        )
        
        return {
            "status": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Error predicting delivery time: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train/delivery-time-model")
async def train_delivery_time_model(
    force_retrain: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    배송 시간 예측 모델 훈련
    
    Args:
        force_retrain: 기존 모델이 있어도 재훈련
        
    Returns:
        훈련 결과
    """
    # 관리자만 실행 가능
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        prediction_service = get_delivery_time_prediction_service(db)
        result = prediction_service.train_model(force_retrain=force_retrain)
        
        return {
            "status": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Error training delivery time model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info/delivery-time")
async def get_delivery_time_model_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """배송 시간 예측 모델 정보 조회"""
    try:
        prediction_service = get_delivery_time_prediction_service(db)
        info = prediction_service.get_model_info()
        
        return {
            "status": "success",
            "data": info
        }
    
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 수요 예측 API
@router.post("/forecast/demand")
async def forecast_demand(
    request: DemandForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 날짜의 수요 예측
    
    Args:
        request: 예측 요청 데이터
        
    Returns:
        예측 결과
    """
    try:
        forecasting_service = get_demand_forecasting_service(db)
        
        # ISO 날짜 파싱
        forecast_date = datetime.fromisoformat(request.forecast_date.replace('Z', '+00:00'))
        
        result = forecasting_service.forecast_demand(
            forecast_date=forecast_date,
            prev_week_orders=request.prev_week_orders,
            prev_month_orders=request.prev_month_orders
        )
        
        return {
            "status": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Error forecasting demand: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/demand/next-days")
async def forecast_next_n_days(
    n_days: int = Query(7, ge=1, le=30, description="예측할 일 수 (1-30)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    향후 N일 수요 예측
    
    Args:
        n_days: 예측할 일 수 (1-30)
        
    Returns:
        일별 예측 결과 리스트
    """
    try:
        forecasting_service = get_demand_forecasting_service(db)
        results = forecasting_service.forecast_next_n_days(n_days=n_days)
        
        return {
            "status": "success",
            "data": results,
            "summary": {
                "total_days": len(results),
                "avg_predicted_orders": sum(r['predicted_order_count'] for r in results) / len(results) if results else 0,
                "peak_day": max(results, key=lambda x: x['predicted_order_count']) if results else None,
                "low_day": min(results, key=lambda x: x['predicted_order_count']) if results else None
            }
        }
    
    except Exception as e:
        logger.error(f"Error forecasting next N days: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train/demand-forecast-model")
async def train_demand_forecast_model(
    force_retrain: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    수요 예측 모델 훈련
    
    Args:
        force_retrain: 기존 모델이 있어도 재훈련
        
    Returns:
        훈련 결과
    """
    # 관리자만 실행 가능
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        forecasting_service = get_demand_forecasting_service(db)
        result = forecasting_service.train_model(force_retrain=force_retrain)
        
        return {
            "status": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Error training demand forecast model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info/demand-forecast")
async def get_demand_forecast_model_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """수요 예측 모델 정보 조회"""
    try:
        forecasting_service = get_demand_forecasting_service(db)
        info = forecasting_service.get_model_info()
        
        return {
            "status": "success",
            "data": info
        }
    
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

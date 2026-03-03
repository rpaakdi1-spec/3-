"""
차량 주행거리 관리 API

GPS 기반 일별 주행거리 조회 및 통계 제공
"""
from datetime import date, datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.core.database import get_db
from app.models.vehicle import Vehicle
from app.models.vehicle_daily_mileage import VehicleDailyMileage
from app.services.vehicle_mileage_service import VehicleMileageService

router = APIRouter()


@router.get("/daily")
async def get_daily_mileages(
    target_date: Optional[date] = Query(None, description="조회 날짜 (기본: 어제)"),
    vehicle_id: Optional[int] = Query(None, description="특정 차량 ID"),
    db: Session = Depends(get_db)
):
    """일별 주행거리 조회"""
    if not target_date:
        target_date = date.today() - timedelta(days=1)
    
    query = db.query(VehicleDailyMileage, Vehicle).join(
        Vehicle, VehicleDailyMileage.vehicle_id == Vehicle.id
    ).filter(VehicleDailyMileage.date == target_date)
    
    if vehicle_id:
        query = query.filter(VehicleDailyMileage.vehicle_id == vehicle_id)
    
    results = query.order_by(desc(VehicleDailyMileage.total_distance_km)).all()
    
    return {
        "success": True,
        "date": target_date.isoformat(),
        "count": len(results),
        "mileages": [
            {
                "vehicle_id": mileage.vehicle_id,
                "vehicle_code": vehicle.code,
                "plate_number": vehicle.plate_number,
                "date": mileage.date.isoformat(),
                "total_distance_km": mileage.total_distance_km,
                "total_driving_minutes": mileage.total_driving_minutes,
                "engine_on_minutes": mileage.engine_on_minutes,
                "idle_minutes": mileage.idle_minutes,
                "max_speed_kmh": mileage.max_speed_kmh,
                "avg_speed_kmh": mileage.avg_speed_kmh,
                "gps_point_count": mileage.gps_point_count,
                "start_time": mileage.start_time.isoformat() if mileage.start_time else None,
                "end_time": mileage.end_time.isoformat() if mileage.end_time else None,
                "calculation_method": mileage.calculation_method
            }
            for mileage, vehicle in results
        ]
    }


@router.get("/weekly")
async def get_weekly_mileages(
    start_date: Optional[date] = Query(None, description="시작 날짜 (기본: 지난 월요일)"),
    vehicle_id: Optional[int] = Query(None, description="특정 차량 ID"),
    db: Session = Depends(get_db)
):
    """주간 주행거리 조회 (최근 7일)"""
    if not start_date:
        today = date.today()
        # 지난 월요일 계산
        start_date = today - timedelta(days=today.weekday() + 7)
    
    end_date = start_date + timedelta(days=6)
    
    query = db.query(
        VehicleDailyMileage.vehicle_id,
        Vehicle.code.label('vehicle_code'),
        Vehicle.plate_number,
        func.sum(VehicleDailyMileage.total_distance_km).label('total_distance'),
        func.sum(VehicleDailyMileage.total_driving_minutes).label('total_minutes'),
        func.avg(VehicleDailyMileage.avg_speed_kmh).label('avg_speed'),
        func.max(VehicleDailyMileage.max_speed_kmh).label('max_speed'),
        func.count(VehicleDailyMileage.id).label('driving_days')
    ).join(
        Vehicle, VehicleDailyMileage.vehicle_id == Vehicle.id
    ).filter(
        and_(
            VehicleDailyMileage.date >= start_date,
            VehicleDailyMileage.date <= end_date
        )
    )
    
    if vehicle_id:
        query = query.filter(VehicleDailyMileage.vehicle_id == vehicle_id)
    
    results = query.group_by(
        VehicleDailyMileage.vehicle_id,
        Vehicle.code,
        Vehicle.plate_number
    ).order_by(desc('total_distance')).all()
    
    return {
        "success": True,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "count": len(results),
        "summary": [
            {
                "vehicle_id": row.vehicle_id,
                "vehicle_code": row.vehicle_code,
                "plate_number": row.plate_number,
                "total_distance_km": round(float(row.total_distance), 2),
                "total_driving_minutes": int(row.total_minutes),
                "avg_speed_kmh": round(float(row.avg_speed), 2),
                "max_speed_kmh": int(row.max_speed),
                "driving_days": int(row.driving_days),
                "avg_distance_per_day": round(float(row.total_distance) / int(row.driving_days), 2) if row.driving_days > 0 else 0
            }
            for row in results
        ]
    }


@router.get("/monthly")
async def get_monthly_mileages(
    year: int = Query(..., description="년도 (예: 2026)"),
    month: int = Query(..., ge=1, le=12, description="월 (1-12)"),
    vehicle_id: Optional[int] = Query(None, description="특정 차량 ID"),
    db: Session = Depends(get_db)
):
    """월별 주행거리 조회"""
    start_date = date(year, month, 1)
    
    # 다음 달 1일을 구한 뒤 1일 빼기
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    query = db.query(
        VehicleDailyMileage.vehicle_id,
        Vehicle.code.label('vehicle_code'),
        Vehicle.plate_number,
        func.sum(VehicleDailyMileage.total_distance_km).label('total_distance'),
        func.sum(VehicleDailyMileage.total_driving_minutes).label('total_minutes'),
        func.sum(VehicleDailyMileage.idle_minutes).label('total_idle'),
        func.avg(VehicleDailyMileage.avg_speed_kmh).label('avg_speed'),
        func.max(VehicleDailyMileage.max_speed_kmh).label('max_speed'),
        func.count(VehicleDailyMileage.id).label('driving_days')
    ).join(
        Vehicle, VehicleDailyMileage.vehicle_id == Vehicle.id
    ).filter(
        and_(
            VehicleDailyMileage.date >= start_date,
            VehicleDailyMileage.date <= end_date
        )
    )
    
    if vehicle_id:
        query = query.filter(VehicleDailyMileage.vehicle_id == vehicle_id)
    
    results = query.group_by(
        VehicleDailyMileage.vehicle_id,
        Vehicle.code,
        Vehicle.plate_number
    ).order_by(desc('total_distance')).all()
    
    return {
        "success": True,
        "year": year,
        "month": month,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "count": len(results),
        "summary": [
            {
                "vehicle_id": row.vehicle_id,
                "vehicle_code": row.vehicle_code,
                "plate_number": row.plate_number,
                "total_distance_km": round(float(row.total_distance), 2),
                "total_driving_hours": round(float(row.total_minutes) / 60, 1),
                "total_idle_minutes": int(row.total_idle),
                "avg_speed_kmh": round(float(row.avg_speed), 2),
                "max_speed_kmh": int(row.max_speed),
                "driving_days": int(row.driving_days),
                "avg_distance_per_day": round(float(row.total_distance) / int(row.driving_days), 2) if row.driving_days > 0 else 0
            }
            for row in results
        ]
    }


@router.get("/vehicle/{vehicle_id}/history")
async def get_vehicle_mileage_history(
    vehicle_id: int,
    start_date: date = Query(..., description="시작 날짜"),
    end_date: date = Query(..., description="종료 날짜"),
    db: Session = Depends(get_db)
):
    """특정 차량의 주행거리 이력 조회"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    
    mileages = db.query(VehicleDailyMileage).filter(
        and_(
            VehicleDailyMileage.vehicle_id == vehicle_id,
            VehicleDailyMileage.date >= start_date,
            VehicleDailyMileage.date <= end_date
        )
    ).order_by(VehicleDailyMileage.date).all()
    
    # 통계 계산
    total_distance = sum(m.total_distance_km for m in mileages)
    total_minutes = sum(m.total_driving_minutes for m in mileages)
    driving_days = len(mileages)
    
    return {
        "success": True,
        "vehicle": {
            "id": vehicle.id,
            "code": vehicle.code,
            "plate_number": vehicle.plate_number
        },
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_distance_km": round(total_distance, 2),
            "total_driving_hours": round(total_minutes / 60, 1),
            "driving_days": driving_days,
            "avg_distance_per_day": round(total_distance / driving_days, 2) if driving_days > 0 else 0
        },
        "daily_records": [
            {
                "date": m.date.isoformat(),
                "distance_km": m.total_distance_km,
                "driving_minutes": m.total_driving_minutes,
                "avg_speed_kmh": m.avg_speed_kmh,
                "max_speed_kmh": m.max_speed_kmh,
                "idle_minutes": m.idle_minutes,
                "gps_point_count": m.gps_point_count
            }
            for m in mileages
        ]
    }


@router.post("/calculate")
async def calculate_mileage(
    vehicle_id: Optional[int] = Query(None, description="특정 차량 ID (없으면 전체)"),
    target_date: Optional[date] = Query(None, description="계산 날짜 (기본: 어제)"),
    db: Session = Depends(get_db)
):
    """주행거리 수동 계산 (관리자용)"""
    if not target_date:
        target_date = date.today() - timedelta(days=1)
    
    service = VehicleMileageService(db)
    
    if vehicle_id:
        # 특정 차량만 계산
        result = service.calculate_daily_mileage(vehicle_id, target_date)
        if not result:
            raise HTTPException(status_code=404, detail="GPS 데이터가 없거나 계산 실패")
        
        return {
            "success": True,
            "message": f"차량 ID {vehicle_id}의 {target_date} 주행거리 계산 완료",
            "result": {
                "vehicle_id": result.vehicle_id,
                "date": result.date.isoformat(),
                "total_distance_km": result.total_distance_km,
                "total_driving_minutes": result.total_driving_minutes
            }
        }
    else:
        # 전체 차량 계산
        results = service.calculate_all_vehicles_yesterday()
        
        return {
            "success": True,
            "message": f"{target_date} 전체 차량 주행거리 계산 완료",
            "count": len(results),
            "total_distance_km": round(sum(r.total_distance_km for r in results), 2)
        }


@router.get("/statistics")
async def get_mileage_statistics(
    start_date: date = Query(..., description="시작 날짜"),
    end_date: date = Query(..., description="종료 날짜"),
    db: Session = Depends(get_db)
):
    """전체 주행거리 통계 (대시보드용)"""
    # 전체 통계
    total_stats = db.query(
        func.count(func.distinct(VehicleDailyMileage.vehicle_id)).label('vehicle_count'),
        func.sum(VehicleDailyMileage.total_distance_km).label('total_distance'),
        func.sum(VehicleDailyMileage.total_driving_minutes).label('total_minutes'),
        func.avg(VehicleDailyMileage.avg_speed_kmh).label('avg_speed'),
        func.count(VehicleDailyMileage.id).label('record_count')
    ).filter(
        and_(
            VehicleDailyMileage.date >= start_date,
            VehicleDailyMileage.date <= end_date
        )
    ).first()
    
    # Top 10 차량
    top_vehicles = db.query(
        Vehicle.plate_number,
        func.sum(VehicleDailyMileage.total_distance_km).label('total_distance')
    ).join(
        VehicleDailyMileage, Vehicle.id == VehicleDailyMileage.vehicle_id
    ).filter(
        and_(
            VehicleDailyMileage.date >= start_date,
            VehicleDailyMileage.date <= end_date
        )
    ).group_by(Vehicle.plate_number).order_by(desc('total_distance')).limit(10).all()
    
    return {
        "success": True,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": (end_date - start_date).days + 1
        },
        "total_statistics": {
            "vehicle_count": int(total_stats.vehicle_count) if total_stats.vehicle_count else 0,
            "total_distance_km": round(float(total_stats.total_distance), 2) if total_stats.total_distance else 0,
            "total_driving_hours": round(float(total_stats.total_minutes) / 60, 1) if total_stats.total_minutes else 0,
            "avg_speed_kmh": round(float(total_stats.avg_speed), 2) if total_stats.avg_speed else 0,
            "record_count": int(total_stats.record_count) if total_stats.record_count else 0
        },
        "top_vehicles": [
            {
                "plate_number": row.plate_number,
                "total_distance_km": round(float(row.total_distance), 2)
            }
            for row in top_vehicles
        ]
    }

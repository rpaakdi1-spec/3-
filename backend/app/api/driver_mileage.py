"""
운전자 주행거리 관리 API

배차 기반 운전자별 일별 주행거리 조회 및 통계 제공
"""
from datetime import date, datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.core.database import get_db
from app.models.driver import Driver
from app.models.driver_daily_mileage import DriverDailyMileage
from app.services.driver_mileage_service import DriverMileageService

router = APIRouter()


@router.get("/daily")
async def get_driver_daily_mileages(
    target_date: Optional[date] = Query(None, description="조회 날짜 (기본: 어제)"),
    driver_id: Optional[int] = Query(None, description="특정 운전자 ID"),
    db: Session = Depends(get_db)
):
    """운전자 일별 주행거리 조회"""
    if not target_date:
        target_date = date.today() - timedelta(days=1)
    
    query = db.query(DriverDailyMileage, Driver).join(
        Driver, DriverDailyMileage.driver_id == Driver.id
    ).filter(DriverDailyMileage.date == target_date)
    
    if driver_id:
        query = query.filter(DriverDailyMileage.driver_id == driver_id)
    
    results = query.order_by(desc(DriverDailyMileage.total_distance_km)).all()
    
    return {
        "success": True,
        "date": target_date.isoformat(),
        "count": len(results),
        "mileages": [
            {
                "driver_id": mileage.driver_id,
                "driver_code": driver.code,
                "driver_name": driver.name,
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
                "vehicle_count": mileage.vehicle_count,
                "vehicle_ids": mileage.vehicle_ids,
                "calculation_method": mileage.calculation_method
            }
            for mileage, driver in results
        ]
    }


@router.get("/weekly")
async def get_driver_weekly_summary(
    driver_id: Optional[int] = Query(None, description="특정 운전자 ID"),
    db: Session = Depends(get_db)
):
    """운전자 주간 주행거리 요약 (최근 7일)"""
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    query = db.query(
        DriverDailyMileage.driver_id,
        Driver.code,
        Driver.name,
        func.sum(DriverDailyMileage.total_distance_km).label("total_distance_km"),
        func.sum(DriverDailyMileage.total_driving_minutes).label("total_driving_minutes"),
        func.avg(DriverDailyMileage.avg_speed_kmh).label("avg_speed_kmh"),
        func.max(DriverDailyMileage.max_speed_kmh).label("max_speed_kmh"),
        func.count(DriverDailyMileage.id).label("driving_days")
    ).join(
        Driver, DriverDailyMileage.driver_id == Driver.id
    ).filter(
        and_(
            DriverDailyMileage.date >= start_date,
            DriverDailyMileage.date < end_date
        )
    )
    
    if driver_id:
        query = query.filter(DriverDailyMileage.driver_id == driver_id)
    
    results = query.group_by(
        DriverDailyMileage.driver_id, Driver.code, Driver.name
    ).order_by(desc("total_distance_km")).all()
    
    return {
        "success": True,
        "period": f"{start_date.isoformat()} ~ {end_date.isoformat()}",
        "count": len(results),
        "summary": [
            {
                "driver_id": row.driver_id,
                "driver_code": row.code,
                "driver_name": row.name,
                "total_distance_km": float(row.total_distance_km or 0),
                "total_driving_hours": float(row.total_driving_minutes or 0) / 60,
                "avg_speed_kmh": float(row.avg_speed_kmh or 0),
                "max_speed_kmh": float(row.max_speed_kmh or 0),
                "driving_days": row.driving_days,
                "avg_distance_per_day": float(row.total_distance_km or 0) / row.driving_days if row.driving_days > 0 else 0
            }
            for row in results
        ]
    }


@router.get("/monthly")
async def get_driver_monthly_summary(
    year: int = Query(..., description="년도"),
    month: int = Query(..., ge=1, le=12, description="월"),
    driver_id: Optional[int] = Query(None, description="특정 운전자 ID"),
    db: Session = Depends(get_db)
):
    """운전자 월별 주행거리 요약"""
    from calendar import monthrange
    
    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)
    
    query = db.query(
        DriverDailyMileage.driver_id,
        Driver.code,
        Driver.name,
        func.sum(DriverDailyMileage.total_distance_km).label("total_distance_km"),
        func.sum(DriverDailyMileage.total_driving_minutes).label("total_driving_minutes"),
        func.sum(DriverDailyMileage.idle_minutes).label("total_idle_minutes"),
        func.avg(DriverDailyMileage.avg_speed_kmh).label("avg_speed_kmh"),
        func.max(DriverDailyMileage.max_speed_kmh).label("max_speed_kmh"),
        func.count(DriverDailyMileage.id).label("driving_days")
    ).join(
        Driver, DriverDailyMileage.driver_id == Driver.id
    ).filter(
        and_(
            DriverDailyMileage.date >= start_date,
            DriverDailyMileage.date <= end_date
        )
    )
    
    if driver_id:
        query = query.filter(DriverDailyMileage.driver_id == driver_id)
    
    results = query.group_by(
        DriverDailyMileage.driver_id, Driver.code, Driver.name
    ).order_by(desc("total_distance_km")).all()
    
    return {
        "success": True,
        "year": year,
        "month": month,
        "count": len(results),
        "summary": [
            {
                "driver_id": row.driver_id,
                "driver_code": row.code,
                "driver_name": row.name,
                "total_distance_km": float(row.total_distance_km or 0),
                "total_driving_hours": float(row.total_driving_minutes or 0) / 60,
                "total_idle_hours": float(row.total_idle_minutes or 0) / 60 if row.total_idle_minutes else 0,
                "avg_speed_kmh": float(row.avg_speed_kmh or 0),
                "max_speed_kmh": float(row.max_speed_kmh or 0),
                "driving_days": row.driving_days,
                "avg_distance_per_day": float(row.total_distance_km or 0) / row.driving_days if row.driving_days > 0 else 0
            }
            for row in results
        ]
    }


@router.get("/history/{driver_id}")
async def get_driver_mileage_history(
    driver_id: int,
    start_date: Optional[date] = Query(None, description="시작 날짜"),
    end_date: Optional[date] = Query(None, description="종료 날짜"),
    limit: int = Query(30, ge=1, le=365, description="조회 일수"),
    db: Session = Depends(get_db)
):
    """특정 운전자의 주행거리 이력"""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=limit)
    
    mileages = db.query(DriverDailyMileage).filter(
        and_(
            DriverDailyMileage.driver_id == driver_id,
            DriverDailyMileage.date >= start_date,
            DriverDailyMileage.date <= end_date
        )
    ).order_by(desc(DriverDailyMileage.date)).all()
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="운전자를 찾을 수 없습니다")
    
    return {
        "success": True,
        "driver_id": driver_id,
        "driver_code": driver.code,
        "driver_name": driver.name,
        "period": f"{start_date.isoformat()} ~ {end_date.isoformat()}",
        "count": len(mileages),
        "history": [
            {
                "date": m.date.isoformat(),
                "total_distance_km": m.total_distance_km,
                "total_driving_minutes": m.total_driving_minutes,
                "avg_speed_kmh": m.avg_speed_kmh,
                "max_speed_kmh": m.max_speed_kmh,
                "vehicle_count": m.vehicle_count,
                "vehicle_ids": m.vehicle_ids,
                "start_time": m.start_time.isoformat() if m.start_time else None,
                "end_time": m.end_time.isoformat() if m.end_time else None,
            }
            for m in mileages
        ]
    }


@router.post("/calculate")
async def calculate_driver_mileages(
    target_date: Optional[date] = Query(None, description="계산 대상 날짜 (기본: 어제)"),
    driver_id: Optional[int] = Query(None, description="특정 운전자 ID (없으면 전체)"),
    db: Session = Depends(get_db)
):
    """운전자 주행거리 재계산"""
    if not target_date:
        target_date = date.today() - timedelta(days=1)
    
    service = DriverMileageService(db)
    
    if driver_id:
        # 특정 운전자만 계산
        mileage = service.calculate_driver_daily_mileage(driver_id, target_date)
        if not mileage:
            raise HTTPException(status_code=404, detail="배차 기록을 찾을 수 없습니다")
        
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        return {
            "success": True,
            "message": f"{driver.name} 운전자의 {target_date} 주행거리 계산 완료",
            "driver_id": driver_id,
            "driver_name": driver.name,
            "total_distance_km": mileage.total_distance_km,
            "vehicle_count": mileage.vehicle_count
        }
    else:
        # 전체 운전자 계산
        results = service.calculate_all_drivers_yesterday()
        return {
            "success": True,
            "message": f"{len(results)}명 운전자의 {target_date} 주행거리 계산 완료",
            "count": len(results),
            "total_distance_km": sum(m.total_distance_km for m in results)
        }


@router.get("/statistics")
async def get_driver_statistics(
    start_date: date = Query(..., description="시작 날짜"),
    end_date: date = Query(..., description="종료 날짜"),
    db: Session = Depends(get_db)
):
    """운전자 주행거리 통계"""
    result = db.query(
        func.count(func.distinct(DriverDailyMileage.driver_id)).label("driver_count"),
        func.sum(DriverDailyMileage.total_distance_km).label("total_distance"),
        func.sum(DriverDailyMileage.total_driving_minutes).label("total_driving_minutes"),
        func.avg(DriverDailyMileage.avg_speed_kmh).label("avg_speed"),
        func.count(DriverDailyMileage.id).label("record_count")
    ).filter(
        and_(
            DriverDailyMileage.date >= start_date,
            DriverDailyMileage.date <= end_date
        )
    ).first()
    
    return {
        "driver_count": result.driver_count or 0,
        "total_distance_km": float(result.total_distance or 0),
        "total_driving_hours": float(result.total_driving_minutes or 0) / 60,
        "avg_speed_kmh": float(result.avg_speed or 0),
        "record_count": result.record_count or 0
    }


@router.get("/top-drivers")
async def get_top_drivers(
    start_date: Optional[date] = Query(None, description="시작 날짜"),
    end_date: Optional[date] = Query(None, description="종료 날짜"),
    limit: int = Query(10, ge=1, le=50, description="조회 인원"),
    db: Session = Depends(get_db)
):
    """주행거리 TOP 운전자"""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    results = db.query(
        DriverDailyMileage.driver_id,
        Driver.code,
        Driver.name,
        func.sum(DriverDailyMileage.total_distance_km).label("total_distance_km"),
        func.count(DriverDailyMileage.id).label("driving_days"),
        func.avg(DriverDailyMileage.avg_speed_kmh).label("avg_speed_kmh")
    ).join(
        Driver, DriverDailyMileage.driver_id == Driver.id
    ).filter(
        and_(
            DriverDailyMileage.date >= start_date,
            DriverDailyMileage.date <= end_date
        )
    ).group_by(
        DriverDailyMileage.driver_id, Driver.code, Driver.name
    ).order_by(desc("total_distance_km")).limit(limit).all()
    
    return {
        "success": True,
        "period": f"{start_date.isoformat()} ~ {end_date.isoformat()}",
        "count": len(results),
        "top_drivers": [
            {
                "rank": idx + 1,
                "driver_id": row.driver_id,
                "driver_code": row.code,
                "driver_name": row.name,
                "total_distance_km": float(row.total_distance_km),
                "driving_days": row.driving_days,
                "avg_distance_per_day": float(row.total_distance_km) / row.driving_days if row.driving_days > 0 else 0,
                "avg_speed_kmh": float(row.avg_speed_kmh or 0)
            }
            for idx, row in enumerate(results)
        ]
    }

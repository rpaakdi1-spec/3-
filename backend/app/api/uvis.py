"""
UVIS API 엔드포인트
- 실시간 차량 위치 조회
- 차량 온도 모니터링
- 차량 상태 추적
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from loguru import logger

from app.db.session import get_db
from app.models.vehicle import Vehicle
from app.services.uvis_service import get_uvis_service, UVISService

router = APIRouter()


@router.get("/vehicles/{vehicle_id}/location")
async def get_vehicle_location(
    vehicle_id: int,
    db: Session = Depends(get_db),
    uvis_service: UVISService = Depends(get_uvis_service)
):
    """
    차량 실시간 위치 조회
    
    Args:
        vehicle_id: 차량 ID
        
    Returns:
        {
            'vehicle_id': int,
            'vehicle_code': str,
            'plate_number': str,
            'terminal_id': str,
            'latitude': float,
            'longitude': float,
            'speed': float,
            'heading': float,
            'timestamp': str,
            'accuracy': float
        }
    """
    # 차량 조회
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    
    # UVIS 연동 확인
    if not vehicle.uvis_enabled or not vehicle.uvis_device_id:
        raise HTTPException(
            status_code=400,
            detail="차량에 UVIS 단말기가 연결되어 있지 않습니다"
        )
    
    # UVIS API 호출
    location = await uvis_service.get_vehicle_location(vehicle.uvis_device_id)
    if not location:
        raise HTTPException(
            status_code=503,
            detail="차량 위치를 조회할 수 없습니다"
        )
    
    # 응답 구성
    return {
        'vehicle_id': vehicle.id,
        'vehicle_code': vehicle.code,
        'plate_number': vehicle.plate_number,
        'terminal_id': vehicle.uvis_device_id,
        **location
    }


@router.get("/vehicles/{vehicle_id}/temperature")
async def get_vehicle_temperature(
    vehicle_id: int,
    db: Session = Depends(get_db),
    uvis_service: UVISService = Depends(get_uvis_service)
):
    """
    차량 온도 조회
    
    Args:
        vehicle_id: 차량 ID
        
    Returns:
        {
            'vehicle_id': int,
            'vehicle_code': str,
            'plate_number': str,
            'terminal_id': str,
            'temperature': float,
            'unit': str,
            'timestamp': str,
            'zone': str,
            'status': str
        }
    """
    # 차량 조회
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    
    # UVIS 연동 확인
    if not vehicle.uvis_enabled or not vehicle.uvis_device_id:
        raise HTTPException(
            status_code=400,
            detail="차량에 UVIS 단말기가 연결되어 있지 않습니다"
        )
    
    # UVIS API 호출
    temperature = await uvis_service.get_vehicle_temperature(vehicle.uvis_device_id)
    if not temperature:
        raise HTTPException(
            status_code=503,
            detail="차량 온도를 조회할 수 없습니다"
        )
    
    # 응답 구성
    return {
        'vehicle_id': vehicle.id,
        'vehicle_code': vehicle.code,
        'plate_number': vehicle.plate_number,
        'terminal_id': vehicle.uvis_device_id,
        **temperature
    }


@router.get("/vehicles/{vehicle_id}/status")
async def get_vehicle_status(
    vehicle_id: int,
    db: Session = Depends(get_db),
    uvis_service: UVISService = Depends(get_uvis_service)
):
    """
    차량 상태 조회
    
    Args:
        vehicle_id: 차량 ID
        
    Returns:
        {
            'vehicle_id': int,
            'vehicle_code': str,
            'plate_number': str,
            'terminal_id': str,
            'engine_status': str,
            'door_status': str,
            'refrigeration_status': str,
            'battery_level': float,
            'timestamp': str
        }
    """
    # 차량 조회
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    
    # UVIS 연동 확인
    if not vehicle.uvis_enabled or not vehicle.uvis_device_id:
        raise HTTPException(
            status_code=400,
            detail="차량에 UVIS 단말기가 연결되어 있지 않습니다"
        )
    
    # UVIS API 호출
    status = await uvis_service.get_vehicle_status(vehicle.uvis_device_id)
    if not status:
        raise HTTPException(
            status_code=503,
            detail="차량 상태를 조회할 수 없습니다"
        )
    
    # 응답 구성
    return {
        'vehicle_id': vehicle.id,
        'vehicle_code': vehicle.code,
        'plate_number': vehicle.plate_number,
        'terminal_id': vehicle.uvis_device_id,
        **status
    }


@router.get("/vehicles/{vehicle_id}/monitor")
async def monitor_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    uvis_service: UVISService = Depends(get_uvis_service)
):
    """
    차량 종합 모니터링 (위치 + 온도 + 상태)
    
    Args:
        vehicle_id: 차량 ID
        
    Returns:
        {
            'vehicle_id': int,
            'vehicle_code': str,
            'plate_number': str,
            'terminal_id': str,
            'timestamp': str,
            'location': {...},
            'temperature': {...},
            'status': {...},
            'alerts': [...]
        }
    """
    # 차량 조회
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="차량을 찾을 수 없습니다")
    
    # UVIS 연동 확인
    if not vehicle.uvis_enabled or not vehicle.uvis_device_id:
        raise HTTPException(
            status_code=400,
            detail="차량에 UVIS 단말기가 연결되어 있지 않습니다"
        )
    
    # UVIS API 호출
    monitoring = await uvis_service.monitor_vehicle(vehicle.uvis_device_id)
    
    # 응답 구성
    return {
        'vehicle_id': vehicle.id,
        'vehicle_code': vehicle.code,
        'plate_number': vehicle.plate_number,
        **monitoring
    }


@router.get("/vehicles/bulk/locations")
async def get_bulk_vehicle_locations(
    vehicle_ids: Optional[List[int]] = Query(None),
    db: Session = Depends(get_db),
    uvis_service: UVISService = Depends(get_uvis_service)
):
    """
    여러 차량의 위치 일괄 조회
    
    Args:
        vehicle_ids: 차량 ID 리스트 (지정하지 않으면 UVIS 연동된 모든 차량)
        
    Returns:
        {
            'total': int,
            'locations': [...]
        }
    """
    # 차량 조회
    query = db.query(Vehicle).filter(
        Vehicle.uvis_enabled == True,
        Vehicle.uvis_device_id.isnot(None)
    )
    
    if vehicle_ids:
        query = query.filter(Vehicle.id.in_(vehicle_ids))
    
    vehicles = query.all()
    
    if not vehicles:
        return {
            'total': 0,
            'locations': []
        }
    
    # UVIS API 일괄 호출
    terminal_ids = [v.uvis_device_id for v in vehicles]
    locations = await uvis_service.get_bulk_vehicle_locations(terminal_ids)
    
    # 차량 정보와 매핑
    vehicle_map = {v.uvis_device_id: v for v in vehicles}
    
    results = []
    for location in locations:
        terminal_id = location['terminal_id']
        vehicle = vehicle_map.get(terminal_id)
        if vehicle:
            results.append({
                'vehicle_id': vehicle.id,
                'vehicle_code': vehicle.code,
                'plate_number': vehicle.plate_number,
                **location
            })
    
    return {
        'total': len(results),
        'locations': results
    }


@router.get("/vehicles/bulk/temperatures")
async def get_bulk_vehicle_temperatures(
    vehicle_ids: Optional[List[int]] = Query(None),
    db: Session = Depends(get_db),
    uvis_service: UVISService = Depends(get_uvis_service)
):
    """
    여러 차량의 온도 일괄 조회
    
    Args:
        vehicle_ids: 차량 ID 리스트 (지정하지 않으면 UVIS 연동된 모든 차량)
        
    Returns:
        {
            'total': int,
            'warning_count': int,
            'temperatures': [...]
        }
    """
    # 차량 조회
    query = db.query(Vehicle).filter(
        Vehicle.uvis_enabled == True,
        Vehicle.uvis_device_id.isnot(None)
    )
    
    if vehicle_ids:
        query = query.filter(Vehicle.id.in_(vehicle_ids))
    
    vehicles = query.all()
    
    if not vehicles:
        return {
            'total': 0,
            'warning_count': 0,
            'temperatures': []
        }
    
    # UVIS API 일괄 호출
    terminal_ids = [v.uvis_device_id for v in vehicles]
    temperatures = await uvis_service.get_bulk_vehicle_temperatures(terminal_ids)
    
    # 차량 정보와 매핑
    vehicle_map = {v.uvis_device_id: v for v in vehicles}
    
    results = []
    warning_count = 0
    
    for temperature in temperatures:
        terminal_id = temperature['terminal_id']
        vehicle = vehicle_map.get(terminal_id)
        if vehicle:
            result = {
                'vehicle_id': vehicle.id,
                'vehicle_code': vehicle.code,
                'plate_number': vehicle.plate_number,
                **temperature
            }
            results.append(result)
            
            if temperature['status'] == 'warning':
                warning_count += 1
    
    return {
        'total': len(results),
        'warning_count': warning_count,
        'temperatures': results
    }


@router.get("/dashboard")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    uvis_service: UVISService = Depends(get_uvis_service)
):
    """
    실시간 대시보드 통합 데이터
    
    Returns:
        {
            'total_vehicles': int,
            'active_vehicles': int,
            'locations': [...],
            'temperatures': [...],
            'alerts': [...]
        }
    """
    # UVIS 연동된 모든 차량 조회
    vehicles = db.query(Vehicle).filter(
        Vehicle.uvis_enabled == True,
        Vehicle.uvis_device_id.isnot(None)
    ).all()
    
    if not vehicles:
        return {
            'total_vehicles': 0,
            'active_vehicles': 0,
            'locations': [],
            'temperatures': [],
            'alerts': []
        }
    
    # 일괄 조회
    terminal_ids = [v.uvis_device_id for v in vehicles]
    locations = await uvis_service.get_bulk_vehicle_locations(terminal_ids)
    temperatures = await uvis_service.get_bulk_vehicle_temperatures(terminal_ids)
    
    # 차량 정보와 매핑
    vehicle_map = {v.uvis_device_id: v for v in vehicles}
    
    # 위치 정보 구성
    location_results = []
    for location in locations:
        terminal_id = location['terminal_id']
        vehicle = vehicle_map.get(terminal_id)
        if vehicle:
            location_results.append({
                'vehicle_id': vehicle.id,
                'vehicle_code': vehicle.code,
                'plate_number': vehicle.plate_number,
                **location
            })
    
    # 온도 정보 구성
    temperature_results = []
    alerts = []
    
    for temperature in temperatures:
        terminal_id = temperature['terminal_id']
        vehicle = vehicle_map.get(terminal_id)
        if vehicle:
            result = {
                'vehicle_id': vehicle.id,
                'vehicle_code': vehicle.code,
                'plate_number': vehicle.plate_number,
                **temperature
            }
            temperature_results.append(result)
            
            # 경고 알림
            if temperature['status'] == 'warning':
                alerts.append({
                    'vehicle_id': vehicle.id,
                    'vehicle_code': vehicle.code,
                    'plate_number': vehicle.plate_number,
                    'type': 'temperature',
                    'severity': 'warning',
                    'message': f"{vehicle.plate_number}: 온도 이상 {temperature['temperature']:.1f}°C",
                    'timestamp': temperature['timestamp']
                })
    
    return {
        'total_vehicles': len(vehicles),
        'active_vehicles': len(locations),
        'locations': location_results,
        'temperatures': temperature_results,
        'alerts': alerts
    }

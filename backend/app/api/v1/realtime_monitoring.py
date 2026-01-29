"""
실시간 모니터링 API 엔드포인트
- 실시간 차량 모니터링
- WebSocket 실시간 업데이트
- 온도 알림 관리
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from loguru import logger

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.realtime_monitoring_service import get_monitoring_service


router = APIRouter()


@router.get("/monitor")
async def monitor_all_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    모든 차량 실시간 모니터링
    
    Returns:
        {
            'total_vehicles': int,
            'monitored': int,
            'alerts': List[Dict],
            'summary': Dict
        }
    """
    monitoring_service = get_monitoring_service(db)
    result = await monitoring_service.monitor_all_vehicles()
    
    return {
        "status": "success",
        "data": result
    }


@router.get("/dashboard")
async def get_monitoring_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    실시간 모니터링 대시보드 데이터 조회
    
    Returns:
        대시보드 데이터
    """
    monitoring_service = get_monitoring_service(db)
    dashboard_data = await monitoring_service.get_monitoring_dashboard_data()
    
    return {
        "status": "success",
        "data": dashboard_data
    }


@router.websocket("/ws")
async def websocket_monitoring(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket 실시간 모니터링 연결
    
    클라이언트는 실시간 모니터링 업데이트를 받습니다:
    - 차량 위치 업데이트
    - 온도 알림
    - 상태 변경
    """
    await websocket.accept()
    
    monitoring_service = get_monitoring_service(db)
    monitoring_service.add_websocket_connection(websocket)
    
    try:
        # 초기 데이터 전송
        initial_data = await monitoring_service.get_monitoring_dashboard_data()
        await websocket.send_json({
            'type': 'initial_data',
            'data': initial_data
        })
        
        # 연결 유지 (클라이언트로부터 메시지 대기)
        while True:
            data = await websocket.receive_text()
            
            # 클라이언트 요청 처리
            if data == "ping":
                await websocket.send_json({'type': 'pong'})
            elif data == "refresh":
                dashboard_data = await monitoring_service.get_monitoring_dashboard_data()
                await websocket.send_json({
                    'type': 'refresh_data',
                    'data': dashboard_data
                })
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        monitoring_service.remove_websocket_connection(websocket)


@router.post("/start-background-monitoring")
async def start_background_monitoring(
    interval_seconds: int = 60,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    백그라운드 모니터링 시작
    
    Args:
        interval_seconds: 모니터링 주기 (초)
    
    Returns:
        시작 확인 메시지
    """
    # 관리자만 실행 가능
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    monitoring_service = get_monitoring_service(db)
    
    # 비동기 백그라운드 태스크로 실행
    import asyncio
    asyncio.create_task(monitoring_service.start_background_monitoring(interval_seconds))
    
    return {
        "status": "success",
        "message": f"백그라운드 모니터링이 시작되었습니다 (주기: {interval_seconds}초)"
    }

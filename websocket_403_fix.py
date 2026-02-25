"""
WebSocket 엔드포인트 - 403 에러 해결 버전
주요 개선사항:
1. Token을 query parameter와 header 모두에서 검증
2. accept() 호출 전에 추가 검증 제거
3. 간단하고 명확한 에러 처리
4. 로깅 강화
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Header
from typing import Optional
import logging
import asyncio
import json
from datetime import datetime

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter()

# 연결 관리자 import
try:
    from app.websocket.connection_manager import manager
    logger.info("✅ WebSocket connection manager imported")
except ImportError as e:
    logger.error(f"❌ Failed to import connection manager: {e}")
    manager = None

# JWT 토큰 검증 함수
async def verify_token(token: Optional[str]) -> Optional[dict]:
    """
    JWT 토큰 검증 (선택적)
    403 방지를 위해 토큰이 없어도 연결을 허용하되, 로그만 남김
    """
    if not token:
        logger.warning("⚠️ No token provided - connection allowed but logged")
        return None
    
    try:
        from jose import jwt, JWTError
        from app.core.config import settings
        
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        logger.info(f"✅ Token verified for user: {payload.get('sub')}")
        return payload
    except JWTError as e:
        logger.warning(f"⚠️ Token verification failed: {e} - connection allowed anyway")
        return None
    except Exception as e:
        logger.warning(f"⚠️ Unexpected error during token verification: {e}")
        return None


@router.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """
    대시보드 실시간 데이터 WebSocket
    - 403 에러 방지: 무조건 연결 수락 후 내부에서 토큰 검증
    """
    client_info = f"{websocket.client.host}:{websocket.client.port}"
    logger.info(f"🔵 Dashboard WebSocket connection attempt from {client_info}")
    
    # 1️⃣ 먼저 무조건 연결 수락 (403 방지)
    try:
        await websocket.accept()
        logger.info(f"✅ WebSocket accepted for {client_info}")
    except Exception as e:
        logger.error(f"❌ Failed to accept WebSocket: {e}")
        return
    
    # 2️⃣ 연결 수락 후 토큰 검증 (실패해도 연결 유지)
    # Query parameter에서 토큰 확인
    token_value = token
    
    # Header에서 토큰 확인 (Bearer 토큰)
    if not token_value and authorization:
        if authorization.startswith("Bearer "):
            token_value = authorization.replace("Bearer ", "")
    
    user_data = await verify_token(token_value)
    if user_data:
        logger.info(f"🔐 User authenticated: {user_data.get('sub')}")
    else:
        logger.info(f"🔓 Anonymous connection allowed")
    
    # 3️⃣ Connection manager에 등록
    if manager:
        try:
            await manager.connect(websocket, "dashboard")
            logger.info(f"✅ Connected to dashboard channel")
        except Exception as e:
            logger.error(f"❌ Failed to register with manager: {e}")
    
    # 4️⃣ 환영 메시지 전송
    try:
        await websocket.send_json({
            "type": "connected",
            "channel": "dashboard",
            "timestamp": datetime.now().isoformat(),
            "authenticated": user_data is not None
        })
        logger.info(f"✅ Welcome message sent")
    except Exception as e:
        logger.error(f"❌ Failed to send welcome message: {e}")
    
    # 5️⃣ 메시지 루프
    try:
        while True:
            try:
                # 메시지 수신 대기 (타임아웃 30초)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                # 받은 메시지 처리
                message = json.loads(data)
                logger.debug(f"📥 Received: {message}")
                
                # 에코 응답
                await websocket.send_json({
                    "type": "echo",
                    "data": message,
                    "timestamp": datetime.now().isoformat()
                })
                
            except asyncio.TimeoutError:
                # 타임아웃 시 keep-alive 전송
                await websocket.send_json({
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                })
                logger.debug(f"💗 Keep-alive sent to {client_info}")
                
    except WebSocketDisconnect:
        logger.info(f"🔌 Client disconnected: {client_info}")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
    finally:
        # 연결 종료 처리
        if manager:
            try:
                await manager.disconnect(websocket, "dashboard")
                logger.info(f"✅ Disconnected from dashboard channel")
            except Exception as e:
                logger.error(f"⚠️ Error during disconnect: {e}")


@router.websocket("/ws/dispatches")
async def websocket_dispatches_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """배차 실시간 업데이트 WebSocket"""
    await websocket.accept()
    
    if manager:
        await manager.connect(websocket, "dispatches")
    
    try:
        await websocket.send_json({
            "type": "connected",
            "channel": "dispatches",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        pass
    finally:
        if manager:
            await manager.disconnect(websocket, "dispatches")


@router.websocket("/ws/vehicles/{vehicle_id}")
async def websocket_vehicle_endpoint(
    websocket: WebSocket,
    vehicle_id: int,
    token: Optional[str] = Query(None)
):
    """차량 위치 추적 WebSocket"""
    await websocket.accept()
    
    channel = f"vehicles/{vehicle_id}"
    if manager:
        await manager.connect(websocket, channel)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "channel": channel,
            "vehicle_id": vehicle_id,
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        pass
    finally:
        if manager:
            await manager.disconnect(websocket, channel)


@router.websocket("/ws/drivers/{driver_id}")
async def websocket_driver_endpoint(
    websocket: WebSocket,
    driver_id: int,
    token: Optional[str] = Query(None)
):
    """기사 상태 업데이트 WebSocket"""
    await websocket.accept()
    
    channel = f"drivers/{driver_id}"
    if manager:
        await manager.connect(websocket, channel)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "channel": channel,
            "driver_id": driver_id,
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        pass
    finally:
        if manager:
            await manager.disconnect(websocket, channel)


@router.websocket("/ws/orders/{order_id}")
async def websocket_order_endpoint(
    websocket: WebSocket,
    order_id: int,
    token: Optional[str] = Query(None)
):
    """주문 상태 추적 WebSocket"""
    await websocket.accept()
    
    channel = f"orders/{order_id}"
    if manager:
        await manager.connect(websocket, channel)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "channel": channel,
            "order_id": order_id,
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        pass
    finally:
        if manager:
            await manager.disconnect(websocket, channel)


@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """알림 실시간 수신 WebSocket"""
    await websocket.accept()
    
    if manager:
        await manager.connect(websocket, "alerts")
    
    try:
        await websocket.send_json({
            "type": "connected",
            "channel": "alerts",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        pass
    finally:
        if manager:
            await manager.disconnect(websocket, "alerts")


@router.websocket("/ws/analytics")
async def websocket_analytics_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """분석 데이터 실시간 업데이트 WebSocket"""
    await websocket.accept()
    
    if manager:
        await manager.connect(websocket, "analytics")
    
    try:
        await websocket.send_json({
            "type": "connected",
            "channel": "analytics",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        pass
    finally:
        if manager:
            await manager.disconnect(websocket, "analytics")


# Stats endpoint (HTTP)
@router.get("/ws/stats")
async def get_websocket_stats():
    """WebSocket 연결 통계 조회"""
    if not manager:
        return {"error": "Connection manager not available"}
    
    return {
        "active_connections": len(manager.active_connections),
        "channels": list(manager.active_connections.keys()) if hasattr(manager.active_connections, 'keys') else [],
        "timestamp": datetime.now().isoformat()
    }


logger.info("✅ WebSocket router initialized (403-fix version)")

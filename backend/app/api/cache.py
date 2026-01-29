"""
캐시 관리 API
캐시 통계, 무효화, 모니터링
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.auth import get_current_active_user
from app.models.user import User
from app.services.cache_service import cache_service
from loguru import logger


router = APIRouter(prefix="/cache", tags=["cache"])


@router.get("/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_active_user)
):
    """
    캐시 통계 조회
    
    - **사용 메모리**
    - **총 키 개수**
    - **캐시 히트율**
    - **히트/미스 횟수**
    """
    try:
        stats = cache_service.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"캐시 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def cache_health_check():
    """
    캐시 헬스 체크 (인증 불필요)
    
    Redis 연결 상태 확인
    """
    stats = cache_service.get_stats()
    
    if not stats.get("enabled"):
        return {
            "status": "disabled",
            "message": "캐싱이 비활성화되어 있습니다"
        }
    
    if stats.get("connected"):
        return {
            "status": "healthy",
            "enabled": True,
            "connected": True
        }
    else:
        return {
            "status": "unhealthy",
            "enabled": True,
            "connected": False,
            "error": stats.get("error")
        }


@router.post("/invalidate/{entity_type}/{entity_id}")
async def invalidate_cache(
    entity_type: str,
    entity_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    특정 엔티티 관련 캐시 무효화
    
    - **entity_type**: order, dispatch, vehicle, client 등
    - **entity_id**: 엔티티 ID
    """
    try:
        cache_service.invalidate_related(entity_type, entity_id)
        return {
            "success": True,
            "message": f"{entity_type}:{entity_id} 관련 캐시가 무효화되었습니다"
        }
    except Exception as e:
        logger.error(f"캐시 무효화 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/pattern/{pattern}")
async def delete_cache_pattern(
    pattern: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    패턴 매칭으로 캐시 삭제
    
    - **pattern**: 캐시 키 패턴 (예: "orders:*")
    """
    try:
        deleted_count = cache_service.delete_pattern(pattern)
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"{deleted_count}개의 캐시가 삭제되었습니다"
        }
    except Exception as e:
        logger.error(f"캐시 패턴 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_all_cache(
    current_user: User = Depends(get_current_active_user)
):
    """
    모든 캐시 삭제
    
    ⚠️ 주의: 모든 캐시가 삭제됩니다!
    """
    # 관리자만 허용
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="관리자만 모든 캐시를 삭제할 수 있습니다"
        )
    
    try:
        cache_service.clear_all()
        return {
            "success": True,
            "message": "모든 캐시가 삭제되었습니다"
        }
    except Exception as e:
        logger.error(f"캐시 전체 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/key/{key}")
async def get_cache_key(
    key: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    특정 캐시 키 조회
    
    - **key**: 캐시 키
    """
    try:
        value = cache_service.get(key)
        ttl = cache_service.get_ttl(key)
        
        if value is None:
            return {
                "success": False,
                "message": "캐시가 존재하지 않습니다"
            }
        
        return {
            "success": True,
            "key": key,
            "value": value,
            "ttl": ttl,
            "exists": True
        }
    except Exception as e:
        logger.error(f"캐시 키 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/warmup")
async def warmup_cache(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    캐시 웜업 (자주 사용되는 데이터 미리 캐싱)
    
    - 활성 주문 목록
    - 가용 차량 목록
    - 가용 기사 목록
    - 대시보드 통계
    """
    try:
        from app.models.order import Order, OrderStatus
        from app.models.vehicle import Vehicle
        from app.models.driver import Driver
        
        # 1. 활성 주문 캐싱
        active_orders = db.query(Order).filter(
            Order.status.in_([OrderStatus.PENDING, OrderStatus.ASSIGNED, OrderStatus.IN_TRANSIT])
        ).all()
        cache_service.set("orders:active:list", active_orders, ttl=300)
        logger.info(f"✅ 활성 주문 {len(active_orders)}개 캐싱")
        
        # 2. 가용 차량 캐싱
        available_vehicles = db.query(Vehicle).filter(
            Vehicle.status == "available"
        ).all()
        cache_service.set("vehicles:available:list", available_vehicles, ttl=300)
        logger.info(f"✅ 가용 차량 {len(available_vehicles)}개 캐싱")
        
        # 3. 가용 기사 캐싱
        available_drivers = db.query(Driver).filter(
            Driver.status == "available"
        ).all()
        cache_service.set("drivers:available:list", available_drivers, ttl=300)
        logger.info(f"✅ 가용 기사 {len(available_drivers)}개 캐싱")
        
        return {
            "success": True,
            "message": "캐시 웜업이 완료되었습니다",
            "cached_items": {
                "active_orders": len(active_orders),
                "available_vehicles": len(available_vehicles),
                "available_drivers": len(available_drivers)
            }
        }
    except Exception as e:
        logger.error(f"캐시 웜업 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_cache(
    current_user: User = Depends(get_current_active_user)
):
    """
    캐시 동작 테스트
    
    캐시 쓰기/읽기/삭제 테스트
    """
    try:
        test_key = "cache:test:key"
        test_value = {"message": "Hello, Cache!", "timestamp": "2026-01-27"}
        
        # 1. 캐시 쓰기
        write_success = cache_service.set(test_key, test_value, ttl=60)
        
        # 2. 캐시 읽기
        read_value = cache_service.get(test_key)
        
        # 3. TTL 확인
        ttl = cache_service.get_ttl(test_key)
        
        # 4. 캐시 삭제
        delete_success = cache_service.delete(test_key)
        
        return {
            "success": True,
            "test_results": {
                "write": write_success,
                "read": read_value == test_value,
                "ttl": ttl,
                "delete": delete_success
            },
            "read_value": read_value
        }
    except Exception as e:
        logger.error(f"캐시 테스트 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

"""
Performance Monitoring API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from loguru import logger

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.cache_service import cache_service
from app.middleware.performance import query_tracker
import psutil


router = APIRouter()


@router.get("/performance/cache-stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get cache performance statistics
    
    Returns cache hit rate, memory usage, etc.
    """
    # Only admins can view performance stats
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        stats = cache_service.get_cache_stats()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/query-stats")
async def get_query_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get database query performance statistics
    
    Returns slow queries, average query time, etc.
    """
    # Only admins can view performance stats
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        stats = query_tracker.get_stats()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting query stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/performance/query-stats/reset")
async def reset_query_stats(
    current_user: User = Depends(get_current_user)
):
    """Reset query performance statistics"""
    # Only admins can reset stats
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        query_tracker.reset()
        
        return {
            "status": "success",
            "message": "Query statistics reset"
        }
    except Exception as e:
        logger.error(f"Error resetting query stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/system")
async def get_system_performance(
    current_user: User = Depends(get_current_user)
):
    """
    Get system performance metrics
    
    Returns CPU, memory, disk usage
    """
    # Only admins can view system stats
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_total_gb = memory.total / (1024 ** 3)
        memory_used_gb = memory.used / (1024 ** 3)
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_total_gb = disk.total / (1024 ** 3)
        disk_used_gb = disk.used / (1024 ** 3)
        disk_percent = disk.percent
        
        return {
            "status": "success",
            "data": {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "cores": cpu_count
                },
                "memory": {
                    "total_gb": round(memory_total_gb, 2),
                    "used_gb": round(memory_used_gb, 2),
                    "usage_percent": memory_percent
                },
                "disk": {
                    "total_gb": round(disk_total_gb, 2),
                    "used_gb": round(disk_used_gb, 2),
                    "usage_percent": disk_percent
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting system performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/performance/cache/flush")
async def flush_cache(
    current_user: User = Depends(get_current_user)
):
    """
    Flush all cache (use with caution)
    
    Only admins can flush cache
    """
    # Only admins can flush cache
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        cache_service.flush_all()
        
        return {
            "status": "success",
            "message": "Cache flushed successfully"
        }
    except Exception as e:
        logger.error(f"Error flushing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/performance/cache/{pattern}")
async def invalidate_cache_pattern(
    pattern: str,
    current_user: User = Depends(get_current_user)
):
    """
    Invalidate cache by pattern
    
    Example: /performance/cache/users:*
    """
    # Only admins can invalidate cache
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        deleted = cache_service.delete_pattern(pattern)
        
        return {
            "status": "success",
            "message": f"Invalidated {deleted} cache keys",
            "deleted_count": deleted
        }
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

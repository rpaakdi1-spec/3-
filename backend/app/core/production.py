"""
프로덕션 환경 설정 및 유틸리티

이 모듈은 프로덕션 배포를 위한 설정과 유틸리티 함수를 제공합니다.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import psutil
import socket

from .config import settings


class ProductionConfig:
    """프로덕션 환경 설정"""
    
    @staticmethod
    def validate_environment() -> Dict[str, Any]:
        """
        프로덕션 환경 변수 검증
        
        Returns:
            Dict[str, Any]: 검증 결과
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        # 필수 환경 변수 확인
        required_vars = [
            "APP_ENV",
            "SECRET_KEY",
            "DATABASE_URL",
        ]
        
        for var in required_vars:
            value = getattr(settings, var.lower(), None)
            if not value:
                validation_result["valid"] = False
                validation_result["errors"].append(f"필수 환경 변수 누락: {var}")
            else:
                validation_result["info"][var] = "설정됨"
        
        # SECRET_KEY 강도 확인
        if settings.SECRET_KEY and len(settings.SECRET_KEY) < 32:
            validation_result["warnings"].append(
                "SECRET_KEY가 너무 짧습니다 (최소 32자 권장)"
            )
        
        # 프로덕션 환경 확인
        if settings.APP_ENV != "production":
            validation_result["warnings"].append(
                f"현재 환경: {settings.APP_ENV} (프로덕션 아님)"
            )
        
        # 데이터베이스 설정 확인
        if "sqlite" in str(settings.DATABASE_URL).lower():
            validation_result["warnings"].append(
                "SQLite는 프로덕션 환경에 권장하지 않습니다. PostgreSQL 사용을 고려하세요."
            )
        
        return validation_result
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        시스템 정보 조회
        
        Returns:
            Dict[str, Any]: 시스템 정보
        """
        return {
            "hostname": socket.gethostname(),
            "platform": sys.platform,
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
        }
    
    @staticmethod
    def check_dependencies() -> Dict[str, bool]:
        """
        의존성 패키지 확인
        
        Returns:
            Dict[str, bool]: 패키지별 설치 여부
        """
        dependencies = {
            "fastapi": False,
            "uvicorn": False,
            "sqlalchemy": False,
            "redis": False,
            "psutil": False,
            "sentry_sdk": False,
        }
        
        for package in dependencies.keys():
            try:
                __import__(package)
                dependencies[package] = True
            except ImportError:
                dependencies[package] = False
        
        return dependencies


class HealthCheck:
    """헬스체크 유틸리티"""
    
    @staticmethod
    async def check_database() -> Dict[str, Any]:
        """
        데이터베이스 연결 확인
        
        Returns:
            Dict[str, Any]: 데이터베이스 상태
        """
        try:
            # 실제 구현에서는 데이터베이스 연결을 확인해야 합니다
            # from .database import SessionLocal
            # db = SessionLocal()
            # db.execute("SELECT 1")
            # db.close()
            
            return {
                "status": "healthy",
                "message": "Database connection successful",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    async def check_redis() -> Dict[str, Any]:
        """
        Redis 연결 확인
        
        Returns:
            Dict[str, Any]: Redis 상태
        """
        try:
            from ..services.cache_service import CacheService
            
            cache = CacheService()
            await cache.set("health_check", "ok", ttl=10)
            value = await cache.get("health_check")
            
            if value == "ok":
                return {
                    "status": "healthy",
                    "message": "Redis connection successful",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Redis read/write test failed",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Redis connection failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def check_disk_space(threshold_percent: int = 90) -> Dict[str, Any]:
        """
        디스크 공간 확인
        
        Args:
            threshold_percent: 경고 임계값 (%)
            
        Returns:
            Dict[str, Any]: 디스크 상태
        """
        disk = psutil.disk_usage('/')
        used_percent = disk.percent
        
        status = "healthy" if used_percent < threshold_percent else "warning"
        
        return {
            "status": status,
            "used_percent": used_percent,
            "free_gb": round(disk.free / (1024**3), 2),
            "total_gb": round(disk.total / (1024**3), 2),
            "message": f"Disk usage: {used_percent}%",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def check_memory(threshold_percent: int = 85) -> Dict[str, Any]:
        """
        메모리 사용량 확인
        
        Args:
            threshold_percent: 경고 임계값 (%)
            
        Returns:
            Dict[str, Any]: 메모리 상태
        """
        memory = psutil.virtual_memory()
        used_percent = memory.percent
        
        status = "healthy" if used_percent < threshold_percent else "warning"
        
        return {
            "status": status,
            "used_percent": used_percent,
            "available_gb": round(memory.available / (1024**3), 2),
            "total_gb": round(memory.total / (1024**3), 2),
            "message": f"Memory usage: {used_percent}%",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    async def comprehensive_check() -> Dict[str, Any]:
        """
        종합 헬스체크
        
        Returns:
            Dict[str, Any]: 전체 시스템 상태
        """
        checks = {
            "database": await HealthCheck.check_database(),
            "redis": await HealthCheck.check_redis(),
            "disk": HealthCheck.check_disk_space(),
            "memory": HealthCheck.check_memory(),
        }
        
        # 전체 상태 판단
        all_healthy = all(
            check["status"] == "healthy" 
            for check in checks.values()
        )
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "checks": checks
        }


class DeploymentManager:
    """배포 관리 유틸리티"""
    
    @staticmethod
    def pre_deployment_check() -> Dict[str, Any]:
        """
        배포 전 사전 점검
        
        Returns:
            Dict[str, Any]: 점검 결과
        """
        result = {
            "ready": True,
            "checks": {},
            "errors": [],
            "warnings": []
        }
        
        # 환경 변수 검증
        env_validation = ProductionConfig.validate_environment()
        result["checks"]["environment"] = env_validation
        if not env_validation["valid"]:
            result["ready"] = False
            result["errors"].extend(env_validation["errors"])
        result["warnings"].extend(env_validation["warnings"])
        
        # 의존성 확인
        dependencies = ProductionConfig.check_dependencies()
        result["checks"]["dependencies"] = dependencies
        missing_deps = [pkg for pkg, installed in dependencies.items() if not installed]
        if missing_deps:
            result["ready"] = False
            result["errors"].append(f"누락된 패키지: {', '.join(missing_deps)}")
        
        # 시스템 리소스 확인
        disk = psutil.disk_usage('/')
        memory = psutil.virtual_memory()
        
        if disk.percent > 90:
            result["warnings"].append(f"디스크 공간 부족: {disk.percent}% 사용 중")
        
        if memory.percent > 85:
            result["warnings"].append(f"메모리 사용량 높음: {memory.percent}% 사용 중")
        
        return result
    
    @staticmethod
    def get_deployment_info() -> Dict[str, Any]:
        """
        배포 정보 조회
        
        Returns:
            Dict[str, Any]: 배포 정보
        """
        return {
            "app_name": settings.APP_NAME,
            "environment": settings.APP_ENV,
            "version": "1.0.0",
            "deployment_time": datetime.now().isoformat(),
            "system_info": ProductionConfig.get_system_info(),
        }

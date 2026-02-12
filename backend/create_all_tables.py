#!/usr/bin/env python3
"""
모든 Phase 테이블 생성 스크립트
서버에서 실행: docker exec -it uvis-backend python3 /app/create_all_tables.py
"""

from app.core.database import Base, engine
from loguru import logger

# Phase 10: Smart Dispatch Rule Engine
try:
    from app.models.dispatch_rules import (
        DispatchRule,
        RuleCondition,
        RuleAction,
        RuleExecution
    )
    logger.info("✅ Phase 10 models imported")
except Exception as e:
    logger.warning(f"⚠️ Phase 10 models import failed: {e}")

# Phase 11-C: Rule Simulation
try:
    from app.models.simulations import (
        Simulation,
        SimulationResult
    )
    logger.info("✅ Phase 11-C models imported")
except Exception as e:
    logger.warning(f"⚠️ Phase 11-C models import failed: {e}")

# Phase 11-B: Traffic Information Integration
try:
    from app.models.traffic import (
        TrafficCondition,
        RouteOptimization,
        TrafficAlert,
        RouteHistory,
        TrafficRule
    )
    logger.info("✅ Phase 11-B models imported")
except Exception as e:
    logger.warning(f"⚠️ Phase 11-B models import failed: {e}")

# Phase 12: Integrated Dispatch
try:
    from app.models.integrated_dispatch import (
        VehicleGPSLocation,
        AutoDispatchLog,
        NaverMapCache
    )
    logger.info("✅ Phase 12 models imported")
except Exception as e:
    logger.warning(f"⚠️ Phase 12 models import failed: {e}")

# Phase 13-14: IoT & Predictive Maintenance
try:
    from app.models.iot_maintenance import (
        IoTSensor,
        SensorReading,
        MaintenanceSchedule,
        MaintenanceHistory,
        PredictiveAlert
    )
    logger.info("✅ Phase 13-14 models imported")
except Exception as e:
    logger.warning(f"⚠️ Phase 13-14 models import failed: {e}")

# Phase 15: ML Auto-Learning
try:
    from app.models.ml_autolearning import (
        DispatchTrainingData,
        MLExperiment,
        ModelVersion,
        DispatchFeature,
        RLRewardHistory
    )
    logger.info("✅ Phase 15 models imported")
except Exception as e:
    logger.warning(f"⚠️ Phase 15 models import failed: {e}")

# Phase 16: Driver App Enhancement
try:
    from app.models.driver_app import (
        DriverNotification,
        PushToken,
        DeliveryProof,
        ChatRoom,
        ChatMessage,
        DriverPerformance,
        NavigationSession,
        DriverLocation
    )
    logger.info("✅ Phase 16 models imported")
except Exception as e:
    logger.warning(f"⚠️ Phase 16 models import failed: {e}")

# 모든 테이블 생성
logger.info("🚀 Creating all Phase tables...")
try:
    Base.metadata.create_all(bind=engine)
    logger.success("✅ 모든 Phase 테이블 생성 완료!")
except Exception as e:
    logger.error(f"❌ 테이블 생성 실패: {e}")
    raise

# 생성된 테이블 목록 출력
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()

logger.info(f"\n📊 총 {len(tables)}개의 테이블이 생성되었습니다:")
for table in sorted(tables):
    logger.info(f"  - {table}")

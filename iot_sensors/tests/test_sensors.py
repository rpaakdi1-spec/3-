"""
IoT 센서 통합 - 테스트 스크립트
2026-02-05

센서 데이터 수집 및 처리 테스트
"""
import asyncio
import random
from datetime import datetime, timedelta
from loguru import logger

from models import (
    TemperatureSensorData, GPSSensorData, DoorSensorData,
    SensorType, AlertLevel
)
from processors.validator import validate_sensor_data
from alerts.rules_engine import AlertRulesEngine
from alerts.notifier import AlertNotifier


# ============================================================================
# 테스트 데이터 생성
# ============================================================================

def generate_temperature_data(
    sensor_id: str,
    vehicle_id: str,
    temp_min: float = -25.0,
    temp_max: float = -15.0,
    anomaly: bool = False
) -> TemperatureSensorData:
    """온도 센서 테스트 데이터 생성"""
    if anomaly:
        # 이상 온도 (정상 범위 벗어남)
        temperature = random.choice([
            random.uniform(-30, temp_min - 1),  # 너무 낮음
            random.uniform(temp_max + 1, 0)     # 너무 높음
        ])
    else:
        # 정상 온도
        temperature = random.uniform(temp_min, temp_max)
        
    return TemperatureSensorData(
        sensor_id=sensor_id,
        vehicle_id=vehicle_id,
        temperature=round(temperature, 1),
        humidity=random.uniform(40, 60),
        battery_level=random.uniform(80, 100),
        timestamp=datetime.utcnow()
    )


def generate_gps_data(
    sensor_id: str,
    vehicle_id: str,
    base_lat: float = 37.5665,
    base_lng: float = 126.9780
) -> GPSSensorData:
    """GPS 센서 테스트 데이터 생성"""
    return GPSSensorData(
        sensor_id=sensor_id,
        vehicle_id=vehicle_id,
        latitude=base_lat + random.uniform(-0.1, 0.1),
        longitude=base_lng + random.uniform(-0.1, 0.1),
        altitude=random.uniform(0, 100),
        speed=random.uniform(0, 80),
        heading=random.uniform(0, 360),
        accuracy=random.uniform(5, 15),
        timestamp=datetime.utcnow()
    )


def generate_door_data(
    sensor_id: str,
    vehicle_id: str,
    is_open: bool = False,
    long_open: bool = False
) -> DoorSensorData:
    """도어 센서 테스트 데이터 생성"""
    duration = None
    if is_open:
        if long_open:
            duration = random.randint(400, 800)  # 6~13분
        else:
            duration = random.randint(10, 200)   # 10초~3분
            
    return DoorSensorData(
        sensor_id=sensor_id,
        vehicle_id=vehicle_id,
        is_open=is_open,
        duration=duration,
        timestamp=datetime.utcnow()
    )


# ============================================================================
# 테스트 시나리오
# ============================================================================

async def test_temperature_validation():
    """온도 검증 테스트"""
    logger.info("\n" + "="*60)
    logger.info("테스트 1: 온도 센서 데이터 검증")
    logger.info("="*60)
    
    # 정상 온도
    data = generate_temperature_data("TEMP_001", "V001")
    result = validate_sensor_data(data, vehicle_type="frozen")
    logger.info(f"✅ 정상 온도: {data.temperature}°C | 검증: {result['valid']}")
    
    # 이상 온도 (경고)
    data = generate_temperature_data("TEMP_001", "V001", anomaly=True)
    result = validate_sensor_data(data, vehicle_type="frozen")
    logger.warning(f"⚠️ 이상 온도: {data.temperature}°C | 검증: {result['valid']} | 메시지: {result.get('messages')}")
    
    # 배터리 부족
    data.battery_level = 15.0
    result = validate_sensor_data(data, vehicle_type="frozen")
    logger.warning(f"🔋 배터리 부족: {data.battery_level}% | 메시지: {result.get('messages')}")


async def test_gps_validation():
    """GPS 검증 테스트"""
    logger.info("\n" + "="*60)
    logger.info("테스트 2: GPS 센서 데이터 검증")
    logger.info("="*60)
    
    # 정상 GPS
    data = generate_gps_data("GPS_001", "V001")
    result = validate_sensor_data(data)
    logger.info(
        f"✅ GPS 데이터: ({data.latitude:.4f}, {data.longitude:.4f}) | "
        f"속도: {data.speed:.1f}km/h | 검증: {result['valid']}"
    )


async def test_door_validation():
    """도어 검증 테스트"""
    logger.info("\n" + "="*60)
    logger.info("테스트 3: 도어 센서 데이터 검증")
    logger.info("="*60)
    
    # 정상 닫힘
    data = generate_door_data("DOOR_001", "V001", is_open=False)
    result = validate_sensor_data(data)
    logger.info(f"✅ 도어 닫힘 | 검증: {result['valid']}")
    
    # 짧은 열림
    data = generate_door_data("DOOR_001", "V001", is_open=True, long_open=False)
    result = validate_sensor_data(data)
    logger.info(f"✅ 도어 열림: {data.duration}초 | 검증: {result['valid']}")
    
    # 장시간 열림 (경고)
    data = generate_door_data("DOOR_001", "V001", is_open=True, long_open=True)
    result = validate_sensor_data(data)
    logger.warning(f"⚠️ 도어 장시간 열림: {data.duration}초 | 메시지: {result.get('messages')}")


async def test_alert_system():
    """알림 시스템 테스트"""
    logger.info("\n" + "="*60)
    logger.info("테스트 4: 알림 시스템")
    logger.info("="*60)
    
    engine = AlertRulesEngine()
    notifier = AlertNotifier()
    
    # 온도 이상 알림
    data = generate_temperature_data("TEMP_002", "V002", anomaly=True)
    alert = await engine.check_temperature_alert(data, vehicle_type="frozen", vehicle_id="V002")
    
    if alert:
        logger.warning(f"🚨 온도 알림: {alert.message}")
        # await notifier.send_alert(alert)  # 실제 전송은 주석 처리
    else:
        logger.info("알림 없음")
        
    # 도어 장시간 열림 알림
    data = generate_door_data("DOOR_002", "V002", is_open=True, long_open=True)
    alert = await engine.check_door_alert(data, vehicle_id="V002")
    
    if alert:
        logger.warning(f"🚨 도어 알림: {alert.message}")
        # await notifier.send_alert(alert)  # 실제 전송은 주석 처리
    else:
        logger.info("알림 없음")


async def test_continuous_monitoring():
    """연속 모니터링 시뮬레이션"""
    logger.info("\n" + "="*60)
    logger.info("테스트 5: 연속 모니터링 (10초)")
    logger.info("="*60)
    
    vehicles = ["V001", "V002", "V003"]
    
    for i in range(10):
        logger.info(f"\n--- {i+1}초 ---")
        
        for vehicle_id in vehicles:
            # 온도 데이터
            temp_data = generate_temperature_data(
                f"TEMP_{vehicle_id}",
                vehicle_id,
                anomaly=(random.random() < 0.2)  # 20% 확률로 이상
            )
            
            # GPS 데이터
            gps_data = generate_gps_data(f"GPS_{vehicle_id}", vehicle_id)
            
            logger.debug(
                f"{vehicle_id}: {temp_data.temperature}°C | "
                f"GPS: ({gps_data.latitude:.4f}, {gps_data.longitude:.4f})"
            )
            
        await asyncio.sleep(1)
        
    logger.info("\n✅ 연속 모니터링 완료")


# ============================================================================
# 메인 실행
# ============================================================================

async def main():
    """메인 테스트 함수"""
    logger.info("🧪 IoT 센서 통합 테스트 시작\n")
    
    try:
        # 개별 테스트
        await test_temperature_validation()
        await test_gps_validation()
        await test_door_validation()
        await test_alert_system()
        
        # 연속 모니터링 (선택)
        # await test_continuous_monitoring()
        
        logger.info("\n" + "="*60)
        logger.info("✅ 모든 테스트 완료!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ 테스트 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())

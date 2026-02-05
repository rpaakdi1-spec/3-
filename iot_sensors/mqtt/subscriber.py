"""
IoT 센서 통합 - MQTT 구독자
2026-02-05

실시간 센서 데이터를 MQTT 브로커에서 수신하여 처리합니다.
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Callable, Optional
from loguru import logger
import aiomqtt

from config import settings
from models import (
    TemperatureSensorData, GPSSensorData, 
    DoorSensorData, HumiditySensorData
)


class MQTTSubscriber:
    """MQTT 구독자 클래스"""
    
    def __init__(self):
        self.client: Optional[aiomqtt.Client] = None
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        
    def register_handler(self, topic: str, handler: Callable):
        """토픽별 핸들러 등록"""
        self.handlers[topic] = handler
        logger.info(f"핸들러 등록: {topic}")
        
    async def connect(self):
        """MQTT 브로커 연결"""
        try:
            self.client = aiomqtt.Client(
                hostname=settings.MQTT_BROKER_HOST,
                port=settings.MQTT_BROKER_PORT,
                username=settings.MQTT_USERNAME,
                password=settings.MQTT_PASSWORD,
                keepalive=settings.MQTT_KEEPALIVE,
            )
            await self.client.__aenter__()
            logger.info(f"MQTT 브로커 연결 성공: {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
            return True
        except Exception as e:
            logger.error(f"MQTT 브로커 연결 실패: {e}")
            return False
            
    async def subscribe_topics(self):
        """토픽 구독"""
        if not self.client:
            logger.error("MQTT 클라이언트가 초기화되지 않았습니다")
            return
            
        topics = [
            settings.MQTT_TOPIC_TEMPERATURE,
            settings.MQTT_TOPIC_GPS,
            settings.MQTT_TOPIC_DOOR,
            settings.MQTT_TOPIC_HUMIDITY,
        ]
        
        for topic in topics:
            await self.client.subscribe(topic, qos=settings.MQTT_QOS)
            logger.info(f"토픽 구독: {topic}")
            
    async def start(self):
        """구독 시작"""
        if not await self.connect():
            return
            
        await self.subscribe_topics()
        self.running = True
        
        logger.info("MQTT 구독 시작...")
        
        try:
            async for message in self.client.messages:
                await self._process_message(message)
        except asyncio.CancelledError:
            logger.info("MQTT 구독 중단됨")
        except Exception as e:
            logger.error(f"MQTT 구독 오류: {e}")
        finally:
            await self.stop()
            
    async def stop(self):
        """구독 중지"""
        self.running = False
        if self.client:
            await self.client.__aexit__(None, None, None)
            logger.info("MQTT 연결 종료")
            
    async def _process_message(self, message: aiomqtt.Message):
        """메시지 처리"""
        try:
            topic = str(message.topic)
            payload = json.loads(message.payload.decode())
            
            logger.debug(f"메시지 수신: {topic} | {payload}")
            
            # 센서 타입 판별
            sensor_data = await self._parse_sensor_data(topic, payload)
            
            if sensor_data:
                # 등록된 핸들러 호출
                for pattern, handler in self.handlers.items():
                    if self._topic_matches(topic, pattern):
                        await handler(sensor_data)
                        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e} | {message.payload}")
        except Exception as e:
            logger.error(f"메시지 처리 오류: {e}")
            
    async def _parse_sensor_data(self, topic: str, payload: Dict):
        """센서 데이터 파싱"""
        try:
            # 토픽에서 센서 타입 추출
            if "temperature" in topic:
                return TemperatureSensorData(**payload)
            elif "gps" in topic:
                return GPSSensorData(**payload)
            elif "door" in topic:
                return DoorSensorData(**payload)
            elif "humidity" in topic:
                return HumiditySensorData(**payload)
            else:
                logger.warning(f"알 수 없는 센서 타입: {topic}")
                return None
        except Exception as e:
            logger.error(f"센서 데이터 파싱 오류: {e}")
            return None
            
    def _topic_matches(self, topic: str, pattern: str) -> bool:
        """토픽 패턴 매칭"""
        # MQTT 와일드카드 지원
        pattern_parts = pattern.split("/")
        topic_parts = topic.split("/")
        
        if len(pattern_parts) != len(topic_parts):
            if pattern_parts[-1] != "#":
                return False
                
        for p, t in zip(pattern_parts, topic_parts):
            if p == "#":
                return True
            elif p == "+":
                continue
            elif p != t:
                return False
                
        return True


# ============================================================================
# 센서 데이터 핸들러 예제
# ============================================================================

async def handle_temperature_data(data: TemperatureSensorData):
    """온도 데이터 처리"""
    logger.info(f"온도 데이터: {data.sensor_id} | {data.temperature}°C")
    
    # 온도 임계값 체크
    from config import TEMPERATURE_THRESHOLDS
    
    # 예: 냉동 차량 온도 체크
    frozen_min = TEMPERATURE_THRESHOLDS["frozen"]["min"]
    frozen_max = TEMPERATURE_THRESHOLDS["frozen"]["max"]
    
    if data.temperature < frozen_min or data.temperature > frozen_max:
        logger.warning(
            f"⚠️ 온도 이상: {data.sensor_id} | "
            f"{data.temperature}°C (정상: {frozen_min}~{frozen_max}°C)"
        )


async def handle_gps_data(data: GPSSensorData):
    """GPS 데이터 처리"""
    logger.info(
        f"GPS 데이터: {data.sensor_id} | "
        f"위치: ({data.latitude}, {data.longitude}) | "
        f"속도: {data.speed}km/h"
    )


async def handle_door_data(data: DoorSensorData):
    """도어 데이터 처리"""
    status = "열림" if data.is_open else "닫힘"
    logger.info(f"도어 상태: {data.sensor_id} | {status}")
    
    if data.is_open and data.duration and data.duration > 300:  # 5분 이상
        logger.warning(f"⚠️ 도어 장시간 열림: {data.sensor_id} | {data.duration}초")


# ============================================================================
# 메인 실행
# ============================================================================

async def main():
    """메인 함수"""
    subscriber = MQTTSubscriber()
    
    # 핸들러 등록
    subscriber.register_handler("sensors/temperature/#", handle_temperature_data)
    subscriber.register_handler("sensors/gps/#", handle_gps_data)
    subscriber.register_handler("sensors/door/#", handle_door_data)
    
    # 구독 시작
    await subscriber.start()


if __name__ == "__main__":
    logger.info("MQTT 구독자 시작...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("MQTT 구독자 종료")

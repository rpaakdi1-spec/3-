"""
IoT 센서 시뮬레이터
2026-02-05

테스트용 센서 데이터를 생성하고 MQTT 또는 HTTP로 전송합니다.
"""
import asyncio
import argparse
import random
import json
from datetime import datetime
from loguru import logger
import aiohttp

# 시뮬레이터에서는 MQTT 라이브러리를 선택적으로 사용
try:
    import aiomqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logger.warning("aiomqtt 미설치: MQTT 기능 비활성화")


class SensorSimulator:
    """센서 시뮬레이터"""
    
    def __init__(
        self,
        vehicles: list,
        mode: str = "http",
        mqtt_host: str = "localhost",
        mqtt_port: int = 1883,
        http_url: str = "http://localhost:8001"
    ):
        self.vehicles = vehicles
        self.mode = mode
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.http_url = http_url
        self.running = False
        
    async def start(self, interval: int = 60):
        """시뮬레이터 시작"""
        logger.info(f"센서 시뮬레이터 시작 (모드: {self.mode}, 차량: {len(self.vehicles)}대)")
        self.running = True
        
        if self.mode == "mqtt" and MQTT_AVAILABLE:
            await self._run_mqtt_mode(interval)
        else:
            await self._run_http_mode(interval)
            
    async def _run_mqtt_mode(self, interval: int):
        """MQTT 모드 실행"""
        async with aiomqtt.Client(self.mqtt_host, self.mqtt_port) as client:
            logger.info(f"MQTT 브로커 연결: {self.mqtt_host}:{self.mqtt_port}")
            
            while self.running:
                for vehicle_id in self.vehicles:
                    # 온도 데이터
                    temp_data = self._generate_temperature_data(vehicle_id)
                    await client.publish(
                        f"sensors/temperature/{vehicle_id}",
                        json.dumps(temp_data)
                    )
                    
                    # GPS 데이터
                    gps_data = self._generate_gps_data(vehicle_id)
                    await client.publish(
                        f"sensors/gps/{vehicle_id}",
                        json.dumps(gps_data)
                    )
                    
                    # 도어 데이터
                    door_data = self._generate_door_data(vehicle_id)
                    await client.publish(
                        f"sensors/door/{vehicle_id}",
                        json.dumps(door_data)
                    )
                    
                    logger.debug(f"MQTT 전송: {vehicle_id}")
                    
                logger.info(f"✅ {len(self.vehicles)}대 차량 데이터 전송 완료")
                await asyncio.sleep(interval)
                
    async def _run_http_mode(self, interval: int):
        """HTTP 모드 실행"""
        logger.info(f"HTTP API: {self.http_url}")
        
        while self.running:
            async with aiohttp.ClientSession() as session:
                for vehicle_id in self.vehicles:
                    try:
                        # 온도 데이터 전송
                        temp_data = [self._generate_temperature_data(vehicle_id)]
                        await self._post_data(
                            session,
                            f"{self.http_url}/api/v1/sensors/temperature",
                            temp_data
                        )
                        
                        # GPS 데이터 전송
                        gps_data = [self._generate_gps_data(vehicle_id)]
                        await self._post_data(
                            session,
                            f"{self.http_url}/api/v1/sensors/gps",
                            gps_data
                        )
                        
                        # 도어 데이터 전송
                        door_data = [self._generate_door_data(vehicle_id)]
                        await self._post_data(
                            session,
                            f"{self.http_url}/api/v1/sensors/door",
                            door_data
                        )
                        
                        logger.debug(f"HTTP 전송: {vehicle_id}")
                        
                    except Exception as e:
                        logger.error(f"HTTP 전송 오류 ({vehicle_id}): {e}")
                        
            logger.info(f"✅ {len(self.vehicles)}대 차량 데이터 전송 완료")
            await asyncio.sleep(interval)
            
    async def _post_data(self, session: aiohttp.ClientSession, url: str, data: list):
        """HTTP POST 요청"""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": "test-api-key"
        }
        
        async with session.post(url, json=data, headers=headers) as response:
            if response.status != 200:
                logger.warning(f"HTTP 오류: {response.status}")
                
    def _generate_temperature_data(self, vehicle_id: str) -> dict:
        """온도 데이터 생성"""
        # 20% 확률로 이상 온도
        if random.random() < 0.2:
            temperature = random.choice([
                random.uniform(-30, -26),  # 너무 낮음
                random.uniform(-14, 0)     # 너무 높음
            ])
        else:
            temperature = random.uniform(-25, -15)  # 정상
            
        return {
            "sensor_id": f"TEMP_{vehicle_id}",
            "vehicle_id": vehicle_id,
            "sensor_type": "temperature",
            "temperature": round(temperature, 1),
            "humidity": round(random.uniform(40, 60), 1),
            "battery_level": round(random.uniform(80, 100), 1),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    def _generate_gps_data(self, vehicle_id: str) -> dict:
        """GPS 데이터 생성"""
        # 서울 중심 (37.5665, 126.9780)
        base_lat = 37.5665
        base_lng = 126.9780
        
        return {
            "sensor_id": f"GPS_{vehicle_id}",
            "vehicle_id": vehicle_id,
            "sensor_type": "gps",
            "latitude": round(base_lat + random.uniform(-0.1, 0.1), 6),
            "longitude": round(base_lng + random.uniform(-0.1, 0.1), 6),
            "altitude": round(random.uniform(0, 100), 1),
            "speed": round(random.uniform(0, 80), 1),
            "heading": round(random.uniform(0, 360), 1),
            "accuracy": round(random.uniform(5, 15), 1),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    def _generate_door_data(self, vehicle_id: str) -> dict:
        """도어 데이터 생성"""
        # 10% 확률로 열림
        is_open = random.random() < 0.1
        duration = None
        
        if is_open:
            # 5% 확률로 장시간 열림
            if random.random() < 0.5:
                duration = random.randint(400, 800)  # 6~13분
            else:
                duration = random.randint(10, 200)   # 10초~3분
                
        return {
            "sensor_id": f"DOOR_{vehicle_id}",
            "vehicle_id": vehicle_id,
            "sensor_type": "door",
            "is_open": is_open,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


# ============================================================================
# 메인 실행
# ============================================================================

async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="IoT 센서 시뮬레이터")
    parser.add_argument("--vehicles", type=int, default=5, help="시뮬레이션할 차량 수")
    parser.add_argument("--interval", type=int, default=60, help="데이터 전송 주기 (초)")
    parser.add_argument("--mode", choices=["http", "mqtt"], default="http", help="전송 모드")
    parser.add_argument("--mqtt-host", default="localhost", help="MQTT 브로커 호스트")
    parser.add_argument("--mqtt-port", type=int, default=1883, help="MQTT 브로커 포트")
    parser.add_argument("--http-url", default="http://localhost:8001", help="HTTP API URL")
    
    args = parser.parse_args()
    
    # 차량 ID 생성
    vehicles = [f"V{str(i+1).zfill(3)}" for i in range(args.vehicles)]
    
    # 시뮬레이터 초기화
    simulator = SensorSimulator(
        vehicles=vehicles,
        mode=args.mode,
        mqtt_host=args.mqtt_host,
        mqtt_port=args.mqtt_port,
        http_url=args.http_url
    )
    
    # 시작
    try:
        await simulator.start(interval=args.interval)
    except KeyboardInterrupt:
        logger.info("시뮬레이터 중단")
        simulator.running = False


if __name__ == "__main__":
    logger.info("🎬 IoT 센서 시뮬레이터")
    asyncio.run(main())

"""
IoT 센서 통합 - 설정 파일
2026-02-05
"""
from pydantic_settings import BaseSettings
from typing import Optional


class IoTSettings(BaseSettings):
    """IoT 센서 통합 설정"""
    
    # MQTT Broker 설정
    MQTT_BROKER_HOST: str = "mqtt.coldchain.local"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    MQTT_QOS: int = 1
    MQTT_KEEPALIVE: int = 60
    
    # MQTT Topics
    MQTT_TOPIC_TEMPERATURE: str = "sensors/temperature/#"
    MQTT_TOPIC_GPS: str = "sensors/gps/#"
    MQTT_TOPIC_DOOR: str = "sensors/door/#"
    MQTT_TOPIC_HUMIDITY: str = "sensors/humidity/#"
    
    # HTTP Collector 설정
    HTTP_COLLECTOR_HOST: str = "0.0.0.0"
    HTTP_COLLECTOR_PORT: int = 8001
    HTTP_API_KEY: Optional[str] = "your-api-key-here"
    
    # Database 설정
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "coldchain"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "coldchain_db"
    
    # Redis 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # InfluxDB 설정 (시계열 데이터 저장용, Optional)
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: Optional[str] = None
    INFLUXDB_ORG: str = "coldchain"
    INFLUXDB_BUCKET: str = "sensors"
    
    # 온도 임계값 설정
    TEMP_MIN_FROZEN: float = -25.0  # 냉동 최저 온도 (°C)
    TEMP_MAX_FROZEN: float = -18.0  # 냉동 최고 온도 (°C)
    TEMP_MIN_CHILLED: float = 0.0   # 냉장 최저 온도 (°C)
    TEMP_MAX_CHILLED: float = 5.0   # 냉장 최고 온도 (°C)
    TEMP_TOLERANCE: float = 2.0     # 허용 오차 (°C)
    
    # 알림 설정
    ALERT_COOLDOWN_SECONDS: int = 300  # 알림 재전송 대기 시간 (5분)
    ALERT_TELEGRAM_BOT_TOKEN: Optional[str] = None
    ALERT_TELEGRAM_CHAT_ID: Optional[str] = None
    ALERT_EMAIL_ENABLED: bool = False
    ALERT_SMS_ENABLED: bool = False
    
    # WebSocket 설정
    WS_HOST: str = "0.0.0.0"
    WS_PORT: int = 8002
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # 데이터 처리 설정
    BUFFER_SIZE: int = 100
    BATCH_INSERT_SIZE: int = 50
    DATA_RETENTION_DAYS: int = 90
    ANOMALY_DETECTION_ENABLED: bool = True
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/home/user/webapp/iot_sensors/logs/iot.log"
    
    class Config:
        env_file = "/home/user/webapp/.env"
        env_file_encoding = "utf-8"


# 전역 설정 인스턴스
settings = IoTSettings()


# 온도대별 임계값 매핑
TEMPERATURE_THRESHOLDS = {
    "frozen": {
        "min": settings.TEMP_MIN_FROZEN,
        "max": settings.TEMP_MAX_FROZEN,
        "name": "냉동",
    },
    "chilled": {
        "min": settings.TEMP_MIN_CHILLED,
        "max": settings.TEMP_MAX_CHILLED,
        "name": "냉장",
    },
    "ambient": {
        "min": 10.0,
        "max": 25.0,
        "name": "상온",
    },
}


# 센서 타입별 설정
SENSOR_TYPES = {
    "temperature": {
        "unit": "°C",
        "precision": 1,
        "sampling_interval": 60,  # seconds
    },
    "humidity": {
        "unit": "%",
        "precision": 0,
        "sampling_interval": 300,  # seconds
    },
    "gps": {
        "precision": 6,
        "sampling_interval": 30,  # seconds
    },
    "door": {
        "states": ["open", "closed"],
        "sampling_interval": 5,  # seconds
    },
}

"""
UVIS GPS 관제 시스템 API 서비스
"""
import httpx
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
import time

from app.models.uvis_gps import (
    UvisAccessKey,
    VehicleGPSLog,
    VehicleTemperatureLog,
    UvisApiLog
)
from app.models.vehicle import Vehicle


# UVIS API 설정
UVIS_BASE_URL = "https://s1.u-vis.com/uvisc"
UVIS_SERIAL_KEY = "S1910-3A84-4559--CC4"  # 업체 인증키
ACCESS_KEY_VALID_MINUTES = 5  # 인증키 유효 시간


class UvisGPSService:
    """UVIS GPS 관제 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = httpx.Client(timeout=30.0)
    
    def __del__(self):
        """클라이언트 정리"""
        if hasattr(self, 'client'):
            self.client.close()
    
    async def get_valid_access_key(self) -> Optional[str]:
        """
        유효한 실시간 인증키 조회 (없으면 새로 발급)
        
        Returns:
            실시간 인증키 또는 None
        """
        # 1. DB에서 유효한 키 조회
        now = datetime.utcnow()
        valid_key = self.db.query(UvisAccessKey).filter(
            UvisAccessKey.is_active == True,
            UvisAccessKey.expires_at > now
        ).order_by(desc(UvisAccessKey.issued_at)).first()
        
        if valid_key:
            return valid_key.access_key
        
        # 2. 유효한 키가 없으면 새로 발급
        return await self.issue_access_key()
    
    async def issue_access_key(self) -> Optional[str]:
        """
        UVIS-001: 실시간 인증키 발급
        
        Returns:
            실시간 인증키 또는 None
        """
        url = f"{UVIS_BASE_URL}/InterfaceAction.do"
        params = {
            "method": "GetAccessKeyWithValues",
            "SerialKey": UVIS_SERIAL_KEY
        }
        
        start_time = time.time()
        
        try:
            # API 호출
            response = self.client.get(url, params=params)
            execution_time = int((time.time() - start_time) * 1000)
            
            # 로그 저장
            self._save_api_log(
                api_type="auth",
                method="GET",
                url=str(response.url),
                request_params=json.dumps(params),
                response_status=response.status_code,
                response_data=response.text,
                execution_time_ms=execution_time
            )
            
            if response.status_code == 200:
                # 응답 파싱 (예상: JSON 형태, 배열일 수 있음)
                try:
                    data = response.json()
                    
                    # 응답이 배열인 경우 첫 번째 항목 사용
                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]
                    
                    access_key = data.get("AccessKey") or data.get("access_key")
                    
                    if access_key:
                        # DB에 저장
                        now = datetime.utcnow()
                        expires_at = now + timedelta(minutes=ACCESS_KEY_VALID_MINUTES)
                        
                        # 기존 키 비활성화
                        self.db.query(UvisAccessKey).filter(
                            UvisAccessKey.is_active == True
                        ).update({"is_active": False})
                        
                        # 새 키 저장
                        new_key = UvisAccessKey(
                            serial_key=UVIS_SERIAL_KEY,
                            access_key=access_key,
                            issued_at=now,
                            expires_at=expires_at,
                            is_active=True
                        )
                        self.db.add(new_key)
                        self.db.commit()
                        
                        return access_key
                except Exception as e:
                    print(f"⚠️ 인증키 파싱 실패: {e}")
                    return None
            
            return None
            
        except Exception as e:
            print(f"❌ UVIS 인증키 발급 실패: {e}")
            self._save_api_log(
                api_type="auth",
                method="GET",
                url=url,
                request_params=json.dumps(params),
                error_message=str(e)
            )
            return None
    
    async def get_vehicle_gps_data(self) -> List[Dict[str, Any]]:
        """
        UVIS-002: 실시간 운행정보 조회
        
        Returns:
            GPS 데이터 리스트
        """
        # 인증키 가져오기
        access_key = await self.get_valid_access_key()
        if not access_key:
            print("❌ 유효한 인증키가 없습니다.")
            return []
        
        url = f"{UVIS_BASE_URL}/SSOAction.do"
        params = {
            "method": "getDeviceAPI",
            "AccessKey": access_key,
            "GUBUN": "01"  # 운행정보
        }
        
        start_time = time.time()
        
        try:
            response = self.client.get(url, params=params)
            execution_time = int((time.time() - start_time) * 1000)
            
            # 로그 저장
            self._save_api_log(
                api_type="gps",
                method="GET",
                url=str(response.url),
                request_params=json.dumps(params),
                response_status=response.status_code,
                response_data=response.text[:1000],  # 최대 1000자
                execution_time_ms=execution_time
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 🔍 DEBUG: UVIS API 원본 응답 로그
                print(f"📥 UVIS GPS API 원본 응답 (첫 2개 항목):")
                items = data if isinstance(data, list) else [data]
                for idx, item in enumerate(items[:2]):
                    print(f"   [{idx}] BI_TURN_ONOFF='{item.get('BI_TURN_ONOFF')}', BI_GPS_SPEED={item.get('BI_GPS_SPEED')}, TID_ID={item.get('TID_ID')}, CM_NUMBER={item.get('CM_NUMBER')}")
                
                # 데이터 저장
                saved_count = await self._save_gps_data(data)
                print(f"✅ GPS 데이터 {saved_count}건 저장 완료")
                
                return data if isinstance(data, list) else [data]
            
            return []
            
        except Exception as e:
            print(f"❌ GPS 데이터 조회 실패: {e}")
            self._save_api_log(
                api_type="gps",
                method="GET",
                url=url,
                request_params=json.dumps(params),
                error_message=str(e)
            )
            return []
    
    async def get_vehicle_temperature_data(self) -> List[Dict[str, Any]]:
        """
        UVIS-003: 실시간 온도정보 조회
        
        Returns:
            온도 데이터 리스트
        """
        # 인증키 가져오기
        access_key = await self.get_valid_access_key()
        if not access_key:
            print("❌ 유효한 인증키가 없습니다.")
            return []
        
        url = f"{UVIS_BASE_URL}/SSOAction.do"
        params = {
            "method": "getDeviceAPI",
            "AccessKey": access_key,
            "GUBUN": "02"  # 온도정보
        }
        
        start_time = time.time()
        
        try:
            response = self.client.get(url, params=params)
            execution_time = int((time.time() - start_time) * 1000)
            
            # 로그 저장
            self._save_api_log(
                api_type="temperature",
                method="GET",
                url=str(response.url),
                request_params=json.dumps(params),
                response_status=response.status_code,
                response_data=response.text[:1000],
                execution_time_ms=execution_time
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 데이터 저장
                saved_count = await self._save_temperature_data(data)
                print(f"✅ 온도 데이터 {saved_count}건 저장 완료")
                
                return data if isinstance(data, list) else [data]
            
            return []
            
        except Exception as e:
            print(f"❌ 온도 데이터 조회 실패: {e}")
            self._save_api_log(
                api_type="temperature",
                method="GET",
                url=url,
                request_params=json.dumps(params),
                error_message=str(e)
            )
            return []
    
    async def _save_gps_data(self, data: List[Dict[str, Any]]) -> int:
        """GPS 데이터 DB 저장"""
        saved_count = 0
        
        try:
            items = data if isinstance(data, list) else [data]
            
            for item in items:
                try:
                    # 위도/경도 변환
                    latitude = float(item.get("BI_X_POSITION", 0)) if item.get("BI_X_POSITION") else None
                    longitude = float(item.get("BI_Y_POSITION", 0)) if item.get("BI_Y_POSITION") else None
                    
                    # 시동 상태 변환
                    # UVIS API: "On" = 시동 ON, "Off" = 시동 OFF (또는 "1"/"0")
                    turn_onoff = str(item.get("BI_TURN_ONOFF", "Off"))
                    is_engine_on = turn_onoff.lower() in ["on", "1", "true"]
                    
                    # 속도 필터링 (유효성 검증)
                    # 255는 GPS 오류 값으로 간주하여 0으로 처리
                    raw_speed = item.get("BI_GPS_SPEED", 0)
                    try:
                        speed_kmh = float(raw_speed) if raw_speed is not None else 0
                        # 비정상적인 속도 값 필터링
                        if speed_kmh >= 250 or speed_kmh < 0:
                            print(f"⚠️ 비정상 속도 감지: {speed_kmh} km/h → 0으로 수정")
                            speed_kmh = 0
                    except (ValueError, TypeError):
                        print(f"⚠️ 속도 파싱 실패: {raw_speed} → 0으로 설정")
                        speed_kmh = 0
                    
                    # 디버그 로그
                    tid_id = item.get("TID_ID")
                    cm_number = item.get("CM_NUMBER")
                    raw_turn_onoff = item.get("BI_TURN_ONOFF")
                    print(f"🚗 차량 {cm_number} (TID: {tid_id})")
                    print(f"   원본 BI_TURN_ONOFF: {repr(raw_turn_onoff)} (type: {type(raw_turn_onoff).__name__})")
                    print(f"   변환 후: '{turn_onoff}' → is_engine_on={is_engine_on}")
                    print(f"   속도: {speed_kmh} km/h (원본: {raw_speed})")
                    
                    # 차량 찾기
                    vehicle = self.db.query(Vehicle).filter(
                        Vehicle.uvis_device_id == tid_id
                    ).first()
                    
                    gps_log = VehicleGPSLog(
                        vehicle_id=vehicle.id if vehicle else None,
                        tid_id=tid_id,
                        bi_date=item.get("BI_DATE", ""),
                        bi_time=item.get("BI_TIME", ""),
                        cm_number=item.get("CM_NUMBER"),
                        bi_turn_onoff=turn_onoff,
                        bi_x_position=item.get("BI_X_POSITION", ""),
                        bi_y_position=item.get("BI_Y_POSITION", ""),
                        bi_gps_speed=item.get("BI_GPS_SPEED"),
                        latitude=latitude,
                        longitude=longitude,
                        is_engine_on=is_engine_on,
                        speed_kmh=speed_kmh  # 필터링된 속도 사용
                    )
                    
                    self.db.add(gps_log)
                    self.db.flush()  # id 채번 후 alert 처리
                    saved_count += 1
                    
                    # 알림 처리 (GPS 로그 저장 후)
                    if vehicle:
                        from app.services.uvis_alert_service import UVISAlertService
                        alerts = UVISAlertService.process_all_alerts(
                            db=self.db,
                            gps_log=gps_log,
                            vehicle=vehicle
                        )
                        # 알림이 발생하면 로그 출력
                        if alerts:
                            for alert in alerts:
                                print(f"🚨 [{alert['level'].upper()}] {alert['title']}")
                    
                except Exception as e:
                    print(f"⚠️ GPS 데이터 저장 실패 (항목): {e}")
                    continue
            
            self.db.commit()
            
        except Exception as e:
            print(f"❌ GPS 데이터 저장 실패: {e}")
            self.db.rollback()
        
        return saved_count
    
    async def _save_temperature_data(self, data: List[Dict[str, Any]]) -> int:
        """온도 데이터 DB 저장"""
        saved_count = 0
        
        try:
            items = data if isinstance(data, list) else [data]
            
            for item in items:
                try:
                    # 위도/경도 변환
                    latitude = float(item.get("TPL_X_POSITION", 0)) if item.get("TPL_X_POSITION") else None
                    longitude = float(item.get("TPL_Y_POSITION", 0)) if item.get("TPL_Y_POSITION") else None
                    
                    # 온도 변환 (부호 + 값)
                    temp_a = self._parse_temperature(
                        item.get("TPL_SIGNAL_A"),
                        item.get("TPL_DEGREE_A")
                    )
                    temp_b = self._parse_temperature(
                        item.get("TPL_SIGNAL_B"),
                        item.get("TPL_DEGREE_B")
                    )
                    
                    # 차량 찾기
                    tid_id = item.get("TID_ID")
                    vehicle = self.db.query(Vehicle).filter(
                        Vehicle.uvis_device_id == tid_id
                    ).first()
                    
                    temp_log = VehicleTemperatureLog(
                        vehicle_id=vehicle.id if vehicle else None,
                        off_key=item.get("OFF_KEY"),
                        tid_id=tid_id,
                        tpl_date=item.get("TPL_DATE", ""),
                        tpl_time=item.get("TPL_TIME", ""),
                        cm_number=item.get("CM_NUMBER"),
                        tpl_x_position=item.get("TPL_X_POSITION", ""),
                        tpl_y_position=item.get("TPL_Y_POSITION", ""),
                        tpl_signal_a=item.get("TPL_SIGNAL_A"),
                        tpl_degree_a=item.get("TPL_DEGREE_A"),
                        temperature_a=temp_a,
                        tpl_signal_b=item.get("TPL_SIGNAL_B"),
                        tpl_degree_b=item.get("TPL_DEGREE_B"),
                        temperature_b=temp_b,
                        latitude=latitude,
                        longitude=longitude
                    )
                    
                    self.db.add(temp_log)
                    saved_count += 1
                    
                    # 알림 처리 (온도 로그 저장 후)
                    if vehicle:
                        from app.services.uvis_alert_service import UVISAlertService
                        alerts = UVISAlertService.process_all_alerts(
                            db=self.db,
                            temp_log=temp_log,
                            vehicle=vehicle
                        )
                        # 알림이 발생하면 로그 출력
                        if alerts:
                            for alert in alerts:
                                print(f"🚨 [{alert['level'].upper()}] {alert['title']}")
                    
                except Exception as e:
                    print(f"⚠️ 온도 데이터 저장 실패 (항목): {e}")
                    continue
            
            self.db.commit()
            
        except Exception as e:
            print(f"❌ 온도 데이터 저장 실패: {e}")
            self.db.rollback()
        
        return saved_count
    
    def _parse_temperature(self, signal: Any, degree: Any) -> Optional[float]:
        """온도 파싱 (부호 + 값)"""
        try:
            if degree is None:
                return None
            
            temp_value = float(degree)
            
            # 부호 처리 (0='+', 1='-')
            if signal == 1 or signal == "1":
                temp_value = -temp_value
            
            return temp_value
            
        except:
            return None
    
    def _save_api_log(
        self,
        api_type: str,
        method: str,
        url: str,
        request_params: Optional[str] = None,
        response_status: Optional[int] = None,
        response_data: Optional[str] = None,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None
    ):
        """API 호출 로그 저장"""
        try:
            log = UvisApiLog(
                api_type=api_type,
                method=method,
                url=url,
                request_params=request_params,
                response_status=response_status,
                response_data=response_data,
                error_message=error_message,
                execution_time_ms=execution_time_ms
            )
            self.db.add(log)
            self.db.commit()
        except Exception as e:
            print(f"⚠️ API 로그 저장 실패: {e}")
            self.db.rollback()
    
    def get_latest_gps_by_vehicle(self, vehicle_id: int) -> Optional[VehicleGPSLog]:
        """차량의 최신 GPS 로그 조회"""
        return self.db.query(VehicleGPSLog).filter(
            VehicleGPSLog.vehicle_id == vehicle_id
        ).order_by(desc(VehicleGPSLog.created_at)).first()
    
    def get_latest_temperature_by_vehicle(self, vehicle_id: int) -> Optional[VehicleTemperatureLog]:
        """차량의 최신 온도 로그 조회"""
        return self.db.query(VehicleTemperatureLog).filter(
            VehicleTemperatureLog.vehicle_id == vehicle_id
        ).order_by(desc(VehicleTemperatureLog.created_at)).first()

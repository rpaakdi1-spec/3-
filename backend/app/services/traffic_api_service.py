"""
Phase 11-B: Traffic API Service
외부 교통 API 통합 서비스 (TMAP, Kakao, Google Maps)
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
import requests
import json

from app.models.traffic import (
    TrafficCondition,
    TrafficLevel,
    TrafficAlert,
    AlertType
)


class TrafficAPIService:
    """교통 API 통합 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        # API Keys (환경 변수에서 로드해야 함)
        self.tmap_key = None  # TMAP API Key
        self.kakao_key = None  # Kakao API Key
        self.google_key = None  # Google Maps API Key
    
    # ==================== TMAP API ====================
    
    def get_tmap_traffic(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float
    ) -> Dict[str, Any]:
        """
        TMAP 교통 정보 조회
        
        Args:
            start_lat: 출발지 위도
            start_lng: 출발지 경도
            end_lat: 목적지 위도
            end_lng: 목적지 경도
        
        Returns:
            교통 정보 딕셔너리
        """
        # TODO: 실제 TMAP API 호출
        # url = "https://apis.openapi.sk.com/tmap/routes"
        # headers = {"appKey": self.tmap_key}
        # response = requests.post(url, headers=headers, json=payload)
        
        # 임시 모의 데이터
        return {
            "provider": "TMAP",
            "distance": 15.5,  # km
            "duration": 25,  # 분
            "traffic_level": TrafficLevel.NORMAL,
            "route_geometry": [],
            "toll_fee": 3000
        }
    
    # ==================== Kakao API ====================
    
    def get_kakao_traffic(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float
    ) -> Dict[str, Any]:
        """
        Kakao 교통 정보 조회
        
        Args:
            start_lat: 출발지 위도
            start_lng: 출발지 경도
            end_lat: 목적지 위도
            end_lng: 목적지 경도
        
        Returns:
            교통 정보 딕셔너리
        """
        # TODO: 실제 Kakao API 호출
        # url = "https://apis-navi.kakaomobility.com/v1/directions"
        # headers = {"Authorization": f"KakaoAK {self.kakao_key}"}
        # response = requests.get(url, headers=headers, params=params)
        
        # 임시 모의 데이터
        return {
            "provider": "KAKAO",
            "distance": 15.8,
            "duration": 27,
            "traffic_level": TrafficLevel.SLOW,
            "route_geometry": [],
            "toll_fee": 3000
        }
    
    # ==================== Google Maps API ====================
    
    def get_google_traffic(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float
    ) -> Dict[str, Any]:
        """
        Google Maps 교통 정보 조회
        
        Args:
            start_lat: 출발지 위도
            start_lng: 출발지 경도
            end_lat: 목적지 위도
            end_lng: 목적지 경도
        
        Returns:
            교통 정보 딕셔너리
        """
        # TODO: 실제 Google Maps API 호출
        # url = "https://maps.googleapis.com/maps/api/directions/json"
        # params = {
        #     "origin": f"{start_lat},{start_lng}",
        #     "destination": f"{end_lat},{end_lng}",
        #     "departure_time": "now",
        #     "traffic_model": "best_guess",
        #     "key": self.google_key
        # }
        # response = requests.get(url, params=params)
        
        # 임시 모의 데이터
        return {
            "provider": "GOOGLE",
            "distance": 16.2,
            "duration": 28,
            "traffic_level": TrafficLevel.NORMAL,
            "route_geometry": [],
            "toll_fee": 3000
        }
    
    # ==================== 통합 교통 정보 ====================
    
    def get_best_route(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float
    ) -> Dict[str, Any]:
        """
        여러 API를 비교하여 최적 경로 선택
        
        Args:
            start_lat: 출발지 위도
            start_lng: 출발지 경도
            end_lat: 목적지 위도
            end_lng: 목적지 경도
        
        Returns:
            최적 경로 정보
        """
        routes = []
        
        # TMAP 경로
        try:
            tmap_route = self.get_tmap_traffic(start_lat, start_lng, end_lat, end_lng)
            routes.append(tmap_route)
        except Exception as e:
            print(f"TMAP API 에러: {e}")
        
        # Kakao 경로
        try:
            kakao_route = self.get_kakao_traffic(start_lat, start_lng, end_lat, end_lng)
            routes.append(kakao_route)
        except Exception as e:
            print(f"Kakao API 에러: {e}")
        
        # Google 경로
        try:
            google_route = self.get_google_traffic(start_lat, start_lng, end_lat, end_lng)
            routes.append(google_route)
        except Exception as e:
            print(f"Google API 에러: {e}")
        
        if not routes:
            return None
        
        # 소요시간 기준으로 최적 경로 선택
        best_route = min(routes, key=lambda r: r.get("duration", float('inf')))
        
        return best_route
    
    # ==================== 교통 상황 저장 ====================
    
    def save_traffic_condition(
        self,
        road_name: str,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float,
        traffic_level: TrafficLevel,
        speed: Optional[float] = None,
        api_provider: str = "SYSTEM"
    ) -> TrafficCondition:
        """
        교통 상황 저장
        
        Args:
            road_name: 도로명
            start_lat: 시작 위도
            start_lng: 시작 경도
            end_lat: 종료 위도
            end_lng: 종료 경도
            traffic_level: 혼잡도
            speed: 평균 속도
            api_provider: API 제공자
        
        Returns:
            생성된 교통 상황 객체
        """
        condition = TrafficCondition(
            road_name=road_name,
            start_lat=start_lat,
            start_lng=start_lng,
            end_lat=end_lat,
            end_lng=end_lng,
            traffic_level=traffic_level,
            speed=speed,
            api_provider=api_provider,
            collected_at=datetime.utcnow()
        )
        
        self.db.add(condition)
        self.db.commit()
        self.db.refresh(condition)
        
        return condition
    
    # ==================== 교통 알림 ====================
    
    def create_traffic_alert(
        self,
        alert_type: AlertType,
        title: str,
        description: Optional[str] = None,
        road_name: Optional[str] = None,
        location_lat: Optional[float] = None,
        location_lng: Optional[float] = None,
        severity: str = "MEDIUM"
    ) -> TrafficAlert:
        """
        교통 알림 생성
        
        Args:
            alert_type: 알림 타입
            title: 제목
            description: 설명
            road_name: 도로명
            location_lat: 위도
            location_lng: 경도
            severity: 심각도
        
        Returns:
            생성된 알림 객체
        """
        alert = TrafficAlert(
            alert_type=alert_type,
            title=title,
            description=description,
            road_name=road_name,
            location_lat=location_lat,
            location_lng=location_lng,
            severity=severity,
            is_active=True
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def get_active_alerts(
        self,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius: float = 10.0
    ) -> List[TrafficAlert]:
        """
        활성 교통 알림 조회
        
        Args:
            lat: 중심 위도
            lng: 중심 경도
            radius: 반경 (km)
        
        Returns:
            알림 목록
        """
        query = self.db.query(TrafficAlert).filter(
            TrafficAlert.is_active == True
        )
        
        # TODO: 위치 기반 필터링 (Haversine formula)
        
        alerts = query.order_by(TrafficAlert.created_at.desc()).limit(50).all()
        
        return alerts

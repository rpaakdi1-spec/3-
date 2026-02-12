/**
 * 실시간 교통 정보 서비스
 * 
 * 네이버/카카오 교통 API 연동
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';
const API_PREFIX = '/traffic';

export interface LocationPoint {
  latitude: number;
  longitude: number;
}

export interface RouteRequest {
  start: LocationPoint;
  end: LocationPoint;
  waypoints?: LocationPoint[];
  provider?: 'naver' | 'kakao';
  option?: 'trafast' | 'tracomfort' | 'traoptimal' | 'traavoidtoll' | 'traavoidcaronly';
}

export interface TrafficInfo {
  overall_level: string;
  smooth_ratio?: number;
  slow_ratio?: number;
  congested_ratio?: number;
  description?: string;
}

export interface RouteResponse {
  provider: string;
  distance_km: number;
  duration_minutes: number;
  duration_with_traffic_minutes: number;
  traffic_info?: TrafficInfo;
  path_coordinates?: Array<{
    latitude: number;
    longitude: number;
  }>;
  fuel_cost?: number;
  toll_cost?: number;
  taxi_fare?: number;
  retrieved_at: string;
}

export interface ArrivalEstimate {
  departure_time: string;
  estimated_arrival_time: string;
  early_arrival_time: string;
  late_arrival_time: string;
  duration_minutes: number;
  distance_km: number;
  traffic_info?: TrafficInfo;
  confidence: string;
  updated_at: string;
}

class TrafficInformationService {
  /**
   * 실시간 경로 탐색
   * @param request 경로 요청
   * @returns 경로 정보
   */
  async getRouteWithTraffic(request: RouteRequest): Promise<RouteResponse> {
    const response = await axios.post(`${API_BASE_URL}${API_PREFIX}/route`, request);
    return response.data;
  }

  /**
   * 간단 경로 탐색 (쿼리 파라미터)
   * @param startLat 출발지 위도
   * @param startLon 출발지 경도
   * @param endLat 도착지 위도
   * @param endLon 도착지 경도
   * @param provider 교통 정보 제공자
   * @param option 경로 옵션
   * @returns 경로 정보
   */
  async getSimpleRoute(
    startLat: number,
    startLon: number,
    endLat: number,
    endLon: number,
    provider: 'naver' | 'kakao' = 'naver',
    option: string = 'trafast'
  ): Promise<RouteResponse> {
    const response = await axios.get(`${API_BASE_URL}${API_PREFIX}/route/simple`, {
      params: {
        start_lat: startLat,
        start_lon: startLon,
        end_lat: endLat,
        end_lon: endLon,
        provider,
        option
      }
    });
    return response.data;
  }

  /**
   * 예상 도착 시간 계산
   * @param currentLat 현재 위도
   * @param currentLon 현재 경도
   * @param destLat 목적지 위도
   * @param destLon 목적지 경도
   * @returns 예상 도착 시간
   */
  async estimateArrivalTime(
    currentLat: number,
    currentLon: number,
    destLat: number,
    destLon: number
  ): Promise<ArrivalEstimate> {
    const response = await axios.get(`${API_BASE_URL}${API_PREFIX}/arrival-estimate/simple`, {
      params: {
        current_lat: currentLat,
        current_lon: currentLon,
        dest_lat: destLat,
        dest_lon: destLon
      }
    });
    return response.data;
  }

  /**
   * 교통 정보 API 테스트
   * @param provider 테스트할 제공자
   * @returns 테스트 결과
   */
  async testTrafficAPI(provider: 'naver' | 'kakao' = 'naver'): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}${API_PREFIX}/traffic/test`, {
      params: { provider }
    });
    return response.data;
  }

  /**
   * 경로 비교 (네이버 vs 카카오)
   * @param startLat 출발지 위도
   * @param startLon 출발지 경도
   * @param endLat 도착지 위도
   * @param endLon 도착지 경도
   * @returns 비교 결과
   */
  async compareRoutes(
    startLat: number,
    startLon: number,
    endLat: number,
    endLon: number
  ): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}${API_PREFIX}/traffic/compare`, {
      params: {
        start_lat: startLat,
        start_lon: startLon,
        end_lat: endLat,
        end_lon: endLon
      }
    });
    return response.data;
  }

  /**
   * 교통 혼잡도 색상 반환
   * @param level 교통 레벨
   * @returns 색상 코드
   */
  getTrafficColor(level: string): string {
    switch (level) {
      case '원활':
        return '#4caf50'; // 녹색
      case '보통':
        return '#2196f3'; // 파랑
      case '서행':
        return '#ff9800'; // 주황
      case '정체':
        return '#f44336'; // 빨강
      case '차단':
        return '#9e9e9e'; // 회색
      default:
        return '#2196f3'; // 기본 파랑
    }
  }

  /**
   * 소요 시간을 "X시간 Y분" 형식으로 변환
   * @param minutes 분
   * @returns 포맷된 문자열
   */
  formatDuration(minutes: number): string {
    if (minutes < 60) {
      return `${Math.round(minutes)}분`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return mins > 0 ? `${hours}시간 ${mins}분` : `${hours}시간`;
  }

  /**
   * 거리를 "X.Xkm" 형식으로 변환
   * @param km 거리 (km)
   * @returns 포맷된 문자열
   */
  formatDistance(km: number): string {
    return `${km.toFixed(1)}km`;
  }
}

export default new TrafficInformationService();

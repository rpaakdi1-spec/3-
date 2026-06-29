/**
 * 게스트 기사 실시간 차량 추적 모달
 * 
 * 1회용 링크로 접속한 기사의 실시간 GPS 위치를 관리자가 볼 수 있는 컴포넌트
 * - 30초마다 자동 갱신
 * - 네이버 지도로 현재 위치 및 이동 경로 표시
 * - 배송 경로 마커 표시
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  X, Navigation, MapPin, RefreshCw, Truck, Phone, User, Clock,
  CheckCircle, AlertCircle, Radio, Wifi, WifiOff
} from 'lucide-react';
import apiClient from '../../api/client';

interface LocationPoint {
  latitude: number;
  longitude: number;
  accuracy?: number;
  timestamp: string | null;
}

interface RoutePoint {
  sequence: number;
  type: string;
  location_name: string;
  address: string;
  latitude: number;
  longitude: number;
  estimated_arrival_time?: string;
  notes?: string;
}

interface TrackingData {
  token: string;
  dispatch_id: number;
  dispatch_number: string;
  dispatch_date: string;
  driver_name: string | null;
  driver_phone: string | null;
  vehicle_plate: string | null;
  current_location: LocationPoint | null;
  location_history: LocationPoint[];
  routes: RoutePoint[];
  last_updated: string | null;
  is_active: boolean;
  access_count: number;
  first_accessed_at: string | null;
  expires_at: string;
  message?: string;
}

interface GuestTrackingModalProps {
  token: string;
  onClose: () => void;
}

declare global {
  interface Window {
    naver: any;
  }
}

const GuestTrackingModal: React.FC<GuestTrackingModalProps> = ({ token, onClose }) => {
  const [trackingData, setTrackingData] = useState<TrackingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);

  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<any>(null);
  const currentMarker = useRef<any>(null);
  const routeMarkers = useRef<any[]>([]);
  const pathPolyline = useRef<any>(null);

  const NAVER_CLIENT_ID = (import.meta as any).env?.VITE_NAVER_MAP_KEY_ID || (import.meta as any).env?.VITE_NAVER_MAP_CLIENT_ID || 'oimsa0yj4k';

  // 추적 데이터 조회
  const fetchTrackingData = useCallback(async () => {
    try {
      const response = await apiClient.get(`/guest/delivery/${token}/track`);
      setTrackingData(response.data);
      setError(null);
      setLastRefresh(new Date());
    } catch (err: any) {
      setError(err.response?.data?.detail || '추적 정보를 불러올 수 없습니다');
    } finally {
      setLoading(false);
    }
  }, [token]);

  // 최초 로드 및 자동 갱신
  useEffect(() => {
    fetchTrackingData();
  }, [fetchTrackingData]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetchTrackingData, 30000); // 30초마다 갱신
    return () => clearInterval(interval);
  }, [autoRefresh, fetchTrackingData]);

  // 네이버 맵 초기화
  useEffect(() => {
    const loadAndInitMap = () => {
      if (!mapRef.current) return;

      const init = () => {
        if (!window.naver || !window.naver.maps || !mapRef.current) return;

        const mapOptions = {
          center: new window.naver.maps.LatLng(37.5665, 126.978),
          zoom: 13,
          mapTypeId: window.naver.maps.MapTypeId.NORMAL
        };

        mapInstance.current = new window.naver.maps.Map(mapRef.current, mapOptions);
      };

      if (window.naver && window.naver.maps) {
        init();
      } else {
        // 이미 스크립트가 로딩 중이면 onload 콜백 추가
        const existingScript = document.querySelector(
          'script[src*="oapi.map.naver.com"]'
        ) as HTMLScriptElement | null;

        if (existingScript) {
          const prevOnload = existingScript.onload;
          existingScript.onload = (e) => {
            if (prevOnload) (prevOnload as any)(e);
            setTimeout(init, 100);
          };
        } else {
          const script = document.createElement('script');
          script.src = `https://oapi.map.naver.com/openapi/v3/maps.js?ncpKeyId=${NAVER_CLIENT_ID}`;
          script.async = true;
          script.onload = () => setTimeout(init, 100);
          document.head.appendChild(script);
        }
      }
    };

    loadAndInitMap();
  }, [NAVER_CLIENT_ID]);

  // 지도 업데이트 (위치 데이터 변경 시)
  useEffect(() => {
    if (!mapInstance.current || !trackingData || !window.naver) return;

    const naver = window.naver.maps;

    // 기존 마커 제거
    if (currentMarker.current) {
      currentMarker.current.setMap(null);
    }
    routeMarkers.current.forEach(m => m.setMap(null));
    routeMarkers.current = [];
    if (pathPolyline.current) {
      pathPolyline.current.setMap(null);
    }

    // 경로 마커 추가
    trackingData.routes.forEach((route, idx) => {
      if (!route.latitude || !route.longitude) return;

      const isStart = route.type === 'departure' || route.sequence === 1;
      const isEnd = route.type === 'arrival';

      const markerHtml = `
        <div style="
          background: ${isStart ? '#16a34a' : isEnd ? '#dc2626' : '#2563eb'};
          color: white;
          border-radius: 50%;
          width: 28px;
          height: 28px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          font-weight: bold;
          border: 2px solid white;
          box-shadow: 0 2px 6px rgba(0,0,0,0.4);
          cursor: pointer;
        ">${route.sequence}</div>
      `;

      const marker = new naver.Marker({
        position: new naver.LatLng(route.latitude, route.longitude),
        map: mapInstance.current,
        icon: {
          content: markerHtml,
          anchor: new naver.Point(14, 14)
        }
      });

      const infoWindow = new naver.InfoWindow({
        content: `
          <div style="padding: 8px; min-width: 150px;">
            <p style="font-weight: bold; margin: 0 0 4px;">${route.sequence}. ${route.location_name}</p>
            <p style="font-size: 12px; color: #666; margin: 0;">${route.address}</p>
            ${route.estimated_arrival_time ? `<p style="font-size: 11px; color: #3b82f6; margin: 4px 0 0;">예상 도착: ${route.estimated_arrival_time}</p>` : ''}
          </div>
        `
      });

      naver.Event.addListener(marker, 'click', () => {
        infoWindow.open(mapInstance.current, marker);
      });

      routeMarkers.current.push(marker);
    });

    // 이동 경로 폴리라인
    if (trackingData.location_history.length > 1) {
      const pathCoords = trackingData.location_history.map(loc =>
        new naver.LatLng(loc.latitude, loc.longitude)
      );

      pathPolyline.current = new naver.Polyline({
        path: pathCoords,
        strokeColor: '#6366f1',
        strokeWeight: 3,
        strokeOpacity: 0.7,
        strokeStyle: 'solid',
        map: mapInstance.current
      });
    }

    // 현재 위치 마커
    if (trackingData.current_location) {
      const { latitude, longitude } = trackingData.current_location;

      const vehicleHtml = `
        <div style="
          background: #f97316;
          color: white;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          border: 3px solid white;
          box-shadow: 0 3px 10px rgba(249,115,22,0.6);
          animation: pulse 1.5s infinite;
        ">🚛</div>
        <style>
          @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(249,115,22,0.7); }
            70% { box-shadow: 0 0 0 10px rgba(249,115,22,0); }
            100% { box-shadow: 0 0 0 0 rgba(249,115,22,0); }
          }
        </style>
      `;

      currentMarker.current = new naver.Marker({
        position: new naver.LatLng(latitude, longitude),
        map: mapInstance.current,
        icon: {
          content: vehicleHtml,
          anchor: new naver.Point(20, 20)
        },
        zIndex: 100
      });

      // 현재 위치로 지도 이동
      mapInstance.current.setCenter(new naver.LatLng(latitude, longitude));
      mapInstance.current.setZoom(14);
    } else if (trackingData.routes.length > 0) {
      // 위치 없으면 첫 번째 경로로 이동
      const firstRoute = trackingData.routes[0];
      if (firstRoute.latitude && firstRoute.longitude) {
        mapInstance.current.setCenter(new naver.LatLng(firstRoute.latitude, firstRoute.longitude));
        mapInstance.current.setZoom(13);
      }
    }
  }, [trackingData]);

  const formatTime = (isoString: string | null) => {
    if (!isoString) return '-';
    try {
      return new Date(isoString).toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return '-';
    }
  };

  const formatDateTime = (isoString: string | null) => {
    if (!isoString) return '-';
    try {
      return new Date(isoString).toLocaleString('ko-KR', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '-';
    }
  };

  const timeSinceUpdate = () => {
    if (!trackingData?.last_updated) return null;
    const seconds = Math.floor((new Date().getTime() - new Date(trackingData.last_updated).getTime()) / 1000);
    if (seconds < 60) return `${seconds}초 전`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}분 전`;
    return `${Math.floor(seconds / 3600)}시간 전`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden">
        {/* 헤더 */}
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 rounded-full p-2">
              <Truck size={22} />
            </div>
            <div>
              <h2 className="text-lg font-bold">실시간 차량 추적</h2>
              <p className="text-sm opacity-80">
                {trackingData?.dispatch_number || '배차번호 로딩중...'} · 1회용 링크 기사
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* 자동갱신 토글 */}
            <button
              onClick={() => setAutoRefresh(prev => !prev)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                autoRefresh
                  ? 'bg-green-400/30 text-white border border-green-300/50'
                  : 'bg-white/20 text-white/70 border border-white/30'
              }`}
            >
              {autoRefresh ? <Wifi size={12} /> : <WifiOff size={12} />}
              {autoRefresh ? '자동갱신 ON' : '자동갱신 OFF'}
            </button>
            {/* 수동 새로고침 */}
            <button
              onClick={fetchTrackingData}
              className="bg-white/20 hover:bg-white/30 rounded-full p-2 transition-colors"
              title="지금 새로고침"
            >
              <RefreshCw size={16} />
            </button>
            <button
              onClick={onClose}
              className="bg-white/20 hover:bg-white/30 rounded-full p-2 transition-colors"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* 본문 */}
        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-3"></div>
              <p className="text-gray-500">추적 정보 불러오는 중...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-3" />
              <p className="text-gray-700 font-medium">{error}</p>
              <button
                onClick={fetchTrackingData}
                className="mt-4 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
              >
                다시 시도
              </button>
            </div>
          </div>
        ) : trackingData ? (
          <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
            {/* 좌측: 정보 패널 */}
            <div className="lg:w-72 xl:w-80 border-r border-gray-100 overflow-y-auto flex-shrink-0 p-4 space-y-4">
              {/* 기사 정보 */}
              <div className="bg-gray-50 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <User size={14} />
                  기사 정보
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">이름</span>
                    <span className="font-medium">{trackingData.driver_name || '미등록'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">연락처</span>
                    <span className="font-medium">{trackingData.driver_phone || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">차량번호</span>
                    <span className="font-medium">{trackingData.vehicle_plate || '-'}</span>
                  </div>
                </div>
              </div>

              {/* 위치 상태 */}
              <div className={`rounded-xl p-4 border-2 ${
                trackingData.current_location
                  ? 'bg-green-50 border-green-200'
                  : 'bg-yellow-50 border-yellow-200'
              }`}>
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  {trackingData.current_location ? (
                    <>
                      <Radio size={14} className="text-green-600 animate-pulse" />
                      <span className="text-green-700">위치 수신 중</span>
                    </>
                  ) : (
                    <>
                      <Navigation size={14} className="text-yellow-600" />
                      <span className="text-yellow-700">위치 대기 중</span>
                    </>
                  )}
                </h3>
                {trackingData.current_location ? (
                  <div className="space-y-1.5 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">위도</span>
                      <span className="font-mono text-xs">{trackingData.current_location.latitude.toFixed(6)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">경도</span>
                      <span className="font-mono text-xs">{trackingData.current_location.longitude.toFixed(6)}</span>
                    </div>
                    {trackingData.current_location.accuracy && (
                      <div className="flex justify-between">
                        <span className="text-gray-500">정확도</span>
                        <span className="text-xs">±{Math.round(trackingData.current_location.accuracy)}m</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-gray-500">마지막 수신</span>
                      <span className="text-xs text-green-600 font-medium">{timeSinceUpdate()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">수신 시각</span>
                      <span className="text-xs">{formatTime(trackingData.last_updated)}</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-yellow-700">
                    {trackingData.message || '기사님이 아직 GPS를 시작하지 않았습니다.'}
                  </p>
                )}
              </div>

              {/* 링크 상태 */}
              <div className="bg-gray-50 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <Clock size={14} />
                  링크 상태
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500">상태</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      trackingData.is_active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {trackingData.is_active ? '활성' : '만료/완료'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">접속 횟수</span>
                    <span className="font-medium">{trackingData.access_count}회</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">최초 접속</span>
                    <span className="text-xs">{formatDateTime(trackingData.first_accessed_at)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">만료 시각</span>
                    <span className="text-xs">{formatDateTime(trackingData.expires_at)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">위치 기록</span>
                    <span className="font-medium">{trackingData.location_history.length}건</span>
                  </div>
                </div>
              </div>

              {/* 배송 경로 */}
              {trackingData.routes.length > 0 && (
                <div className="bg-gray-50 rounded-xl p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <MapPin size={14} />
                    배송 경로
                  </h3>
                  <div className="space-y-2">
                    {trackingData.routes.map((route) => (
                      <div key={route.sequence} className="flex items-start gap-2 text-xs">
                        <span className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-white font-bold ${
                          route.type === 'departure' ? 'bg-green-600' :
                          route.type === 'arrival' ? 'bg-red-600' : 'bg-blue-600'
                        }`}>
                          {route.sequence}
                        </span>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-gray-800 truncate">{route.location_name}</p>
                          <p className="text-gray-500 truncate">{route.address}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 갱신 정보 */}
              <div className="text-center text-xs text-gray-400 pb-2">
                마지막 조회: {lastRefresh.toLocaleTimeString('ko-KR')}
                {autoRefresh && <span className="ml-1">(30초 자동갱신)</span>}
              </div>
            </div>

            {/* 우측: 지도 */}
            <div className="flex-1 relative min-h-[300px]">
              <div ref={mapRef} className="absolute inset-0" />

              {/* 지도 범례 */}
              <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-3 text-xs z-10">
                <div className="font-semibold text-gray-700 mb-2">범례</div>
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🚛</span>
                    <span className="text-gray-600">현재 위치</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-4 h-4 rounded-full bg-green-600 inline-block"></span>
                    <span className="text-gray-600">출발지</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-4 h-4 rounded-full bg-blue-600 inline-block"></span>
                    <span className="text-gray-600">경유지</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-4 h-4 rounded-full bg-red-600 inline-block"></span>
                    <span className="text-gray-600">도착지</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-0.5 bg-indigo-500" style={{borderTop: '2px dashed #6366f1'}}></div>
                    <span className="text-gray-600">이동경로</span>
                  </div>
                </div>
              </div>

              {/* 현재 위치 없음 오버레이 */}
              {!trackingData.current_location && (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-100/70 backdrop-blur-sm z-10">
                  <div className="text-center bg-white rounded-xl shadow-lg p-6 max-w-xs mx-4">
                    <Navigation className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                    <h3 className="font-semibold text-gray-700 mb-2">GPS 위치 없음</h3>
                    <p className="text-sm text-gray-500">
                      {trackingData.message || '기사님이 아직 GPS를 시작하지 않았습니다.\n기사님의 링크에서 GPS 시작 버튼을 눌러주세요.'}
                    </p>
                    <p className="text-xs text-gray-400 mt-3">
                      30초마다 자동으로 업데이트됩니다
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default GuestTrackingModal;

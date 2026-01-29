/**
 * 실시간 차량 모니터링 (UVIS GPS 연동)
 * - UVIS GPS API를 통해 실제 차량 위치 표시
 * - 차량 상태: 시동 ON/OFF, GPS 위치, 온도, 속도
 * - 지도 중심: 대한민국 중심 (36.5N, 127.5E)
 */
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Icon, LatLngExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';

const API_BASE = '/api/v1';

interface VehicleRealtimeStatus {
  vehicle_id: number | null;
  vehicle_plate_number: string | null;
  tid_id: string;
  gps_datetime: string | null;
  latitude: number | null;
  longitude: number | null;
  is_engine_on: boolean | null;
  speed_kmh: number | null;
  temperature_datetime: string | null;
  temperature_a: number | null;
  temperature_b: number | null;
  last_updated: string | null;
}

// 차량 마커 아이콘 생성
const createVehicleIcon = (isEngineOn: boolean, tempAvg: number | null) => {
  let color = '#9ca3af'; // 기본 회색 (시동 OFF)
  
  if (isEngineOn) {
    // 시동 ON인 경우 온도에 따라 색상 결정
    if (tempAvg === null) {
      color = '#10b981'; // 녹색 (온도 정보 없음)
    } else if (tempAvg < -15) {
      color = '#3b82f6'; // 파란색 (냉동)
    } else if (tempAvg < 5) {
      color = '#22d3ee'; // 하늘색 (냉장)
    } else if (tempAvg < 15) {
      color = '#10b981'; // 녹색 (정상)
    } else {
      color = '#f59e0b'; // 주황색 (경고)
    }
  }
  
  return new Icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${color}" width="36" height="36">
        <path d="M18 18.5C18 19.328 17.328 20 16.5 20H7.5C6.672 20 6 19.328 6 18.5V5.5C6 4.672 6.672 4 7.5 4H16.5C17.328 4 18 4.672 18 5.5V18.5ZM8 6V18H16V6H8Z"/>
        <circle cx="12" cy="12" r="3" fill="white"/>
      </svg>
    `)}`,
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -36]
  });
};

const RealtimeDashboard: React.FC = () => {
  const [vehicles, setVehicles] = useState<VehicleRealtimeStatus[]>([]);
  const [loading, setLoading] = useState(true); // 초기 로딩 상태를 true로 설정
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh] = useState(true);
  const [refreshInterval] = useState(30); // seconds

  // 대한민국 중심 좌표
  const koreaCenter: LatLngExpression = [36.5, 127.5];

  // UVIS GPS 데이터 조회
  const loadRealtimeData = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('[실시간 모니터링] 데이터 조회 시작...');
      
      const response = await fetch(`${API_BASE}/uvis-gps/realtime/vehicles`);
      
      if (!response.ok) {
        throw new Error(`API 오류: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('[실시간 모니터링] API 응답:', data);
      
      if (data.items && Array.isArray(data.items)) {
        setVehicles(data.items);
        console.log(`[실시간 모니터링] 차량 데이터 ${data.items.length}대 로드 완료`);
      } else {
        console.warn('[실시간 모니터링] 예상치 못한 API 응답 형식:', data);
        setVehicles([]);
      }
    } catch (err: any) {
      console.error('[실시간 모니터링] 데이터 조회 실패:', err);
      setError(err.message || '데이터 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  // 초기 로드
  useEffect(() => {
    loadRealtimeData();
  }, []);

  // 자동 새로고침
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      loadRealtimeData();
    }, refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  // 시간 포맷팅
  const formatDateTime = (dateStr: string | null) => {
    if (!dateStr) return '-';
    try {
      return new Date(dateStr).toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  // 온도 색상
  const getTempColor = (temp: number | null) => {
    if (temp === null) return 'text-gray-500';
    if (temp < -15) return 'text-blue-600';
    if (temp < 5) return 'text-cyan-600';
    if (temp < 15) return 'text-green-600';
    return 'text-orange-600';
  };

  // GPS 위치가 있는 차량만 필터링
  const vehiclesWithLocation = vehicles.filter(
    v => v.latitude !== null && v.longitude !== null && 
         v.latitude !== 0 && v.longitude !== 0
  );

  // 렌더링 로그
  console.log('[실시간 모니터링] 렌더링:', {
    총차량: vehicles.length,
    GPS차량: vehiclesWithLocation.length,
    로딩중: loading,
    에러: error
  });

  return (
    <div className="h-screen flex flex-col">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded m-4">
          ⚠️ {error}
        </div>
      )}

      {/* 로딩 중 */}
      {loading ? (
        <div className="flex justify-center items-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">차량 데이터 로딩 중...</p>
          </div>
        </div>
      ) : vehicles.length === 0 ? (
        <div className="flex justify-center items-center h-full text-gray-500">
          <div className="text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <p className="mt-4 text-lg">차량 데이터가 없습니다</p>
            <p className="mt-2 text-sm">UVIS 데이터 동기화를 실행해주세요</p>
          </div>
        </div>
      ) : vehiclesWithLocation.length === 0 ? (
        <div className="flex justify-center items-center h-full text-gray-500">
          <div className="text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <p className="mt-4 text-lg">GPS 위치 정보가 있는 차량이 없습니다</p>
            <p className="mt-2 text-sm">UVIS 데이터 동기화를 실행해주세요</p>
          </div>
        </div>
      ) : (
        <div className="h-full flex-1">
          <MapContainer
            center={koreaCenter}
            zoom={7}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {vehiclesWithLocation.map((vehicle) => {
                  const tempAvg = 
                    vehicle.temperature_a !== null && vehicle.temperature_b !== null
                      ? (vehicle.temperature_a + vehicle.temperature_b) / 2
                      : vehicle.temperature_a !== null
                      ? vehicle.temperature_a
                      : vehicle.temperature_b;
                  
                  return (
                    <Marker
                      key={vehicle.tid_id}
                      position={[vehicle.latitude!, vehicle.longitude!]}
                      icon={createVehicleIcon(vehicle.is_engine_on || false, tempAvg)}
                    >
                      <Popup>
                        <div className="p-2 min-w-[250px]">
                          <h3 className="font-bold text-lg mb-2">
                            {vehicle.vehicle_plate_number || vehicle.tid_id}
                          </h3>
                          
                          {/* 시동 상태 */}
                          <div className="mb-2">
                            <span className={`inline-block px-2 py-1 rounded text-sm font-semibold ${
                              vehicle.is_engine_on 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-gray-100 text-gray-800'
                            }`}>
                              {vehicle.is_engine_on ? '🟢 시동 ON' : '⚫ 시동 OFF'}
                            </span>
                          </div>
                          
                          {/* GPS 정보 */}
                          <div className="text-sm text-gray-600 space-y-1">
                            <p>📍 위치: {vehicle.latitude?.toFixed(6)}, {vehicle.longitude?.toFixed(6)}</p>
                            <p className={vehicle.speed_kmh && vehicle.speed_kmh > 0 ? 'text-green-600 font-semibold' : ''}>
                              🚗 속도: {vehicle.speed_kmh?.toFixed(1) || 0} km/h
                            </p>
                            {vehicle.gps_datetime && (
                              <p className="text-xs">⏰ GPS: {formatDateTime(vehicle.gps_datetime)}</p>
                            )}
                          </div>
                          
                          {/* 온도 정보 */}
                          {(vehicle.temperature_a !== null || vehicle.temperature_b !== null) && (
                            <div className="mt-2 pt-2 border-t border-gray-200">
                              <p className="text-sm font-semibold text-gray-700 mb-1">🌡️ 온도</p>
                              <div className="text-sm space-y-1">
                                {vehicle.temperature_a !== null && (
                                  <p className={getTempColor(vehicle.temperature_a)}>
                                    냉동실 A: <span className="font-bold">{vehicle.temperature_a.toFixed(1)}°C</span>
                                  </p>
                                )}
                                {vehicle.temperature_b !== null && (
                                  <p className={getTempColor(vehicle.temperature_b)}>
                                    냉동실 B: <span className="font-bold">{vehicle.temperature_b.toFixed(1)}°C</span>
                                  </p>
                                )}
                                {vehicle.temperature_datetime && (
                                  <p className="text-xs text-gray-500">
                                    ⏰ 온도: {formatDateTime(vehicle.temperature_datetime)}
                                  </p>
                                )}
                              </div>
                            </div>
                          )}
                          
                          {/* 마지막 업데이트 */}
                          {vehicle.last_updated && (
                            <p className="text-xs text-gray-400 mt-2 pt-2 border-t border-gray-200">
                              🔄 업데이트: {formatDateTime(vehicle.last_updated)}
                            </p>
                          )}
                        </div>
                      </Popup>
                    </Marker>
                  );
                })}
              </MapContainer>
            </div>
          )}
    </div>
  );
};

export default RealtimeDashboard;

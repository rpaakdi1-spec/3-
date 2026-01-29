/**
 * UVIS GPS 실시간 모니터링 컴포넌트 (개선버전 v2)
 * - 주소 변환 기능 (Nominatim API - 무료)
 * - 시동 상태 정확한 판단 (속도 기반)
 * - 정확한 시간 표시
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';

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

interface SyncResponse {
  success: boolean;
  message: string;
  gps_count?: number;
  temperature_count?: number;
}

const UvisGPSMonitoring: React.FC = () => {
  const [vehicles, setVehicles] = useState<VehicleRealtimeStatus[]>([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30); // 30초
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  const [currentTime, setCurrentTime] = useState<Date>(new Date());
  const [addressCache, setAddressCache] = useState<{ [key: string]: string }>({});
  const [loadingAddresses, setLoadingAddresses] = useState<Set<string>>(new Set());

  // 실시간 시계 업데이트
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000); // 1초마다 업데이트

    return () => clearInterval(timer);
  }, []);

  // 시동 상태 정확하게 판단
  const getEngineStatus = (vehicle: VehicleRealtimeStatus): boolean => {
    // 1. 속도가 0이 아니면 무조건 시동 ON
    if (vehicle.speed_kmh !== null && vehicle.speed_kmh > 0) {
      return true;
    }
    
    // 2. UVIS API의 is_engine_on 값 사용
    return vehicle.is_engine_on || false;
  };

  // 좌표를 주소로 변환 (Nominatim API - 무료, 인증 불필요)
  const getAddressFromCoords = async (lat: number, lon: number): Promise<string> => {
    const cacheKey = `${lat.toFixed(4)},${lon.toFixed(4)}`;
    
    // 캐시에 있으면 반환
    if (addressCache[cacheKey]) {
      return addressCache[cacheKey];
    }
    
    // 이미 로딩 중이면 대기
    if (loadingAddresses.has(cacheKey)) {
      return '주소 조회 중...';
    }

    try {
      setLoadingAddresses(prev => new Set([...prev, cacheKey]));
      
      // Nominatim API 사용 (OpenStreetMap - 무료)
      const response = await axios.get(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1`,
        {
          headers: {
            'User-Agent': 'UVIS-GPS-Monitoring/1.0'
          }
        }
      );

      let address = '';
      if (response.data && response.data.address) {
        const addr = response.data.address;
        
        // 한국어 주소 구성
        const parts = [];
        
        if (addr.province || addr.state) {
          parts.push(addr.province || addr.state);
        }
        if (addr.city || addr.county) {
          parts.push(addr.city || addr.county);
        }
        if (addr.suburb || addr.district) {
          parts.push(addr.suburb || addr.district);
        }
        if (addr.road || addr.street) {
          parts.push(addr.road || addr.street);
        }
        if (addr.house_number) {
          parts.push(addr.house_number);
        }
        
        address = parts.join(' ') || response.data.display_name;
      }

      if (!address) {
        address = `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
      }

      // 캐시에 저장
      setAddressCache(prev => ({ ...prev, [cacheKey]: address }));
      setLoadingAddresses(prev => {
        const newSet = new Set(prev);
        newSet.delete(cacheKey);
        return newSet;
      });

      return address;
    } catch (error) {
      console.warn('주소 변환 실패:', error);
      setLoadingAddresses(prev => {
        const newSet = new Set(prev);
        newSet.delete(cacheKey);
        return newSet;
      });
      
      // 실패 시 간단한 주소 표시
      const simpleAddr = `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
      setAddressCache(prev => ({ ...prev, [cacheKey]: simpleAddr }));
      return simpleAddr;
    }
  };

  // 실시간 데이터 조회
  const loadRealtimeData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/uvis-gps/realtime/vehicles`);
      const items = response.data.items || [];
      setVehicles(items);
      
      // 주소 조회 (백그라운드)
      items.forEach((vehicle: VehicleRealtimeStatus) => {
        if (vehicle.latitude && vehicle.longitude) {
          getAddressFromCoords(vehicle.latitude, vehicle.longitude);
        }
      });
    } catch (error) {
      console.error('❌ 실시간 데이터 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // UVIS 데이터 동기화
  const syncAllData = async () => {
    setSyncing(true);
    try {
      const response = await axios.post(`${API_BASE}/uvis-gps/sync/all`, {
        force_new_key: false
      });
      const data: SyncResponse = response.data;
      
      alert(`✅ 동기화 완료!\nGPS: ${data.gps_count || 0}건\n온도: ${data.temperature_count || 0}건`);
      setLastSyncTime(new Date());
      
      // 동기화 후 데이터 새로고침
      await loadRealtimeData();
    } catch (error) {
      console.error('❌ 동기화 실패:', error);
      alert('❌ 동기화 실패. 다시 시도해주세요.');
    } finally {
      setSyncing(false);
    }
  };

  // 시동 ON/OFF 버튼 클릭 (표시만, 실제 제어 불가)
  const handleEngineToggle = (vehicle: VehicleRealtimeStatus) => {
    const actualStatus = getEngineStatus(vehicle);
    alert(`⚠️ 시동 제어 기능은 현재 표시만 가능합니다.\n\n차량: ${vehicle.vehicle_plate_number}\n현재 상태: ${actualStatus ? '시동 ON' : '시동 OFF'}\n속도: ${vehicle.speed_kmh || 0} km/h\n\n실제 시동 제어는 UVIS 시스템에서 직접 수행해야 합니다.`);
  };

  // 자동 새로고침
  useEffect(() => {
    if (autoRefresh) {
      const timer = setInterval(() => {
        loadRealtimeData();
      }, refreshInterval * 1000);
      
      return () => clearInterval(timer);
    }
  }, [autoRefresh, refreshInterval]);

  // 초기 로드
  useEffect(() => {
    loadRealtimeData();
  }, []);

  // 시간 포맷팅 (정확한 로컬 시간)
  const formatDateTime = (dateStr: string | null): string => {
    if (!dateStr) return '-';
    try {
      const date = new Date(dateStr);
      return date.toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    } catch {
      return dateStr;
    }
  };

  // 현재 시간 포맷팅
  const formatCurrentTime = (): string => {
    return currentTime.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  // 온도 색상
  const getTempColor = (temp: number | null): string => {
    if (temp === null) return 'gray';
    if (temp < -15) return 'blue';
    if (temp < 5) return 'lightblue';
    if (temp < 15) return 'green';
    return 'orange';
  };

  // 주소 표시
  const getDisplayAddress = (lat: number | null, lon: number | null): string => {
    if (!lat || !lon) return '-';
    const cacheKey = `${lat.toFixed(4)},${lon.toFixed(4)}`;
    return addressCache[cacheKey] || '주소 조회 중...';
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <h2 style={{ margin: 0 }}>🛰️ UVIS GPS 실시간 모니터링</h2>
        <div style={{ 
          fontSize: '18px', 
          fontWeight: 'bold', 
          color: '#2196F3',
          backgroundColor: '#f0f8ff',
          padding: '8px 16px',
          borderRadius: '8px',
          border: '2px solid #2196F3'
        }}>
          🕐 {formatCurrentTime()}
        </div>
      </div>

      {/* 컨트롤 패널 */}
      <div style={{
        display: 'flex',
        gap: '15px',
        marginBottom: '20px',
        padding: '15px',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <button
          onClick={syncAllData}
          disabled={syncing}
          style={{
            padding: '10px 20px',
            backgroundColor: syncing ? '#ccc' : '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: syncing ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {syncing ? '🔄 동기화 중...' : '🔄 UVIS 데이터 동기화'}
        </button>

        <button
          onClick={loadRealtimeData}
          disabled={loading}
          style={{
            padding: '10px 20px',
            backgroundColor: loading ? '#ccc' : '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? '⏳ 로딩 중...' : '🔄 새로고침'}
        </button>

        <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
          />
          자동 새로고침
        </label>

        {autoRefresh && (
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
          >
            <option value={10}>10초</option>
            <option value={30}>30초</option>
            <option value={60}>1분</option>
            <option value={300}>5분</option>
          </select>
        )}

        {lastSyncTime && (
          <span style={{ marginLeft: 'auto', color: '#666', fontSize: '14px' }}>
            마지막 동기화: {formatDateTime(lastSyncTime.toISOString())}
          </span>
        )}
      </div>

      {/* 차량 목록 */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(450px, 1fr))',
        gap: '20px'
      }}>
        {vehicles.length === 0 ? (
          <div style={{
            gridColumn: '1 / -1',
            textAlign: 'center',
            padding: '40px',
            backgroundColor: '#f9f9f9',
            borderRadius: '8px',
            color: '#666'
          }}>
            {loading ? '⏳ 데이터를 불러오는 중...' : '📭 실시간 데이터가 없습니다. "UVIS 데이터 동기화" 버튼을 클릭하세요.'}
          </div>
        ) : (
          vehicles.map((vehicle) => {
            const actualEngineStatus = getEngineStatus(vehicle);
            return (
              <div
                key={vehicle.tid_id}
                style={{
                  backgroundColor: 'white',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  padding: '15px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '15px',
                  paddingBottom: '10px',
                  borderBottom: '2px solid #eee'
                }}>
                  <h3 style={{ margin: 0, fontSize: '18px' }}>
                    🚛 {vehicle.vehicle_plate_number || vehicle.tid_id}
                  </h3>
                  <button
                    onClick={() => handleEngineToggle(vehicle)}
                    style={{
                      padding: '6px 12px',
                      backgroundColor: actualEngineStatus ? '#4CAF50' : '#999',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      cursor: 'pointer',
                      transition: 'all 0.3s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.opacity = '0.8';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.opacity = '1';
                    }}
                  >
                    {actualEngineStatus ? '🔑 시동 ON' : '⭕ 시동 OFF'}
                  </button>
                </div>

                {/* GPS 정보 + 주소 */}
                <div style={{ marginBottom: '12px' }}>
                  <div style={{ fontWeight: 'bold', color: '#333', marginBottom: '6px', fontSize: '14px' }}>
                    📍 GPS 정보
                  </div>
                  <div style={{ fontSize: '13px', color: '#666', lineHeight: '1.8' }}>
                    <div style={{ 
                      backgroundColor: '#f8f9fa', 
                      padding: '8px', 
                      borderRadius: '4px', 
                      marginBottom: '6px',
                      fontWeight: '500',
                      minHeight: '24px'
                    }}>
                      🏠 {getDisplayAddress(vehicle.latitude, vehicle.longitude)}
                    </div>
                    <div>• 위도: {vehicle.latitude?.toFixed(6) || '-'}</div>
                    <div>• 경도: {vehicle.longitude?.toFixed(6) || '-'}</div>
                    <div>• 속도: <strong style={{ color: vehicle.speed_kmh && vehicle.speed_kmh > 0 ? '#4CAF50' : '#666' }}>{vehicle.speed_kmh !== null ? `${vehicle.speed_kmh} km/h` : '-'}</strong></div>
                    <div>• GPS 시간: {vehicle.gps_datetime || '-'}</div>
                  </div>
                </div>

                {/* 온도 정보 */}
                <div style={{ marginBottom: '12px' }}>
                  <div style={{ fontWeight: 'bold', color: '#333', marginBottom: '6px', fontSize: '14px' }}>
                    🌡️ 온도 정보
                  </div>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '8px'
                  }}>
                    <div style={{
                      padding: '8px',
                      backgroundColor: '#f0f8ff',
                      borderRadius: '4px',
                      textAlign: 'center'
                    }}>
                      <div style={{ fontSize: '11px', color: '#666' }}>냉동실 A</div>
                      <div style={{
                        fontSize: '18px',
                        fontWeight: 'bold',
                        color: getTempColor(vehicle.temperature_a)
                      }}>
                        {vehicle.temperature_a !== null ? `${vehicle.temperature_a.toFixed(1)}°C` : '-'}
                      </div>
                    </div>
                    <div style={{
                      padding: '8px',
                      backgroundColor: '#fff0f0',
                      borderRadius: '4px',
                      textAlign: 'center'
                    }}>
                      <div style={{ fontSize: '11px', color: '#666' }}>냉장실 B</div>
                      <div style={{
                        fontSize: '18px',
                        fontWeight: 'bold',
                        color: getTempColor(vehicle.temperature_b)
                      }}>
                        {vehicle.temperature_b !== null ? `${vehicle.temperature_b.toFixed(1)}°C` : '-'}
                      </div>
                    </div>
                  </div>
                  <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
                    온도 업데이트: {vehicle.temperature_datetime || '-'}
                  </div>
                </div>

                {/* 최종 업데이트 */}
                <div style={{
                  marginTop: '12px',
                  paddingTop: '8px',
                  borderTop: '1px solid #eee',
                  fontSize: '11px',
                  color: '#999',
                  textAlign: 'right'
                }}>
                  ⏱️ 데이터 업데이트: {formatDateTime(vehicle.last_updated)}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* 통계 */}
      {vehicles.length > 0 && (
        <div style={{
          marginTop: '20px',
          padding: '15px',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          display: 'flex',
          justifyContent: 'space-around',
          flexWrap: 'wrap',
          gap: '15px'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2196F3' }}>
              {vehicles.length}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>전체 차량</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4CAF50' }}>
              {vehicles.filter(v => getEngineStatus(v)).length}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>시동 ON</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#FF9800' }}>
              {vehicles.filter(v => v.latitude && v.longitude).length}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>GPS 활성</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#9C27B0' }}>
              {vehicles.filter(v => v.temperature_a !== null || v.temperature_b !== null).length}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>온도 센서 활성</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UvisGPSMonitoring;

/**
 * Real-time Dashboard Page with WebSocket Integration
 * Phase 13: Real-time WebSocket Dashboard
 * 
 * Features:
 * - Real-time metrics updates via WebSocket
 * - Live dispatch status monitoring
 * - Active vehicle tracking
 * - Temperature alerts
 * - Order status updates
 * - Auto-reconnect support
 * - UVIS GPS real-time vehicle tracking
 */
import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { Icon, LatLngExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useRealtimeDashboard, useRealtimeAlerts, Alert, DashboardMetrics } from '../hooks/useRealtimeData';
import { uvisAPI } from '../services/api';
import { toast } from 'react-hot-toast';

interface RealtimeVehicle {
  vehicle_id: number;
  vehicle_plate_number: string;
  tid_id: string;
  latitude: number | null;
  longitude: number | null;
  is_engine_on: boolean;
  speed_kmh: number;
  temperature_a: number | null;
  temperature_b: number | null;
  gps_datetime: string;
  temperature_datetime: string;
  last_updated: string;
  driver_name?: string | null;
  driver_phone?: string | null;
}

// Vehicle icon creator with plate number label
const createVehicleIcon = (plateNumber: string, status: string, temperature?: number) => {
  let color = '#6b7280'; // gray for offline (GPS 없음)
  
  if (status === 'active') {
    if (temperature === undefined) {
      color = '#10b981'; // green (정상)
    } else if (temperature < -18) {
      color = '#3b82f6'; // blue (냉동)
    } else if (temperature < 5) {
      color = '#22d3ee'; // cyan (냉장)
    } else if (temperature < 15) {
      color = '#10b981'; // green (정상)
    } else {
      color = '#f59e0b'; // orange (주의)
    }
  } else if (status === 'idle') {
    color = '#fbbf24'; // yellow (시동꺼짐)
  }
  
  // Escape plate number for SVG (replace special characters)
  const escapedPlateNumber = plateNumber
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
  
  // Use encodeURIComponent instead of btoa for UTF-8 support
  const svgString = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60" width="120" height="60">
      <!-- Vehicle marker -->
      <g transform="translate(60, 36)">
        <path d="M0,-30 L-18,-10 L-18,10 L18,10 L18,-10 Z" fill="${color}" stroke="white" stroke-width="2"/>
        <circle cx="0" cy="0" r="8" fill="white"/>
      </g>
      <!-- Plate number label -->
      <rect x="10" y="2" width="100" height="20" rx="3" fill="white" stroke="${color}" stroke-width="1.5"/>
      <text x="60" y="16" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="${color}" text-anchor="middle">${escapedPlateNumber}</text>
    </svg>
  `;
  
  return new Icon({
    iconUrl: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svgString)}`,
    iconSize: [120, 60],
    iconAnchor: [60, 36],
    popupAnchor: [0, -40]
  });
};

// Map center updater component
const MapCenterUpdater: React.FC<{ center: LatLngExpression; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  
  return null;
};

const RealtimeDashboardPage: React.FC = () => {
  const { data: dashboardData, isConnected: dashboardConnected } = useRealtimeDashboard();
  const [alerts, setAlerts] = React.useState<Alert[]>([]);
  const [vehicles, setVehicles] = useState<RealtimeVehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [mapCenter, setMapCenter] = useState<LatLngExpression>([37.5665, 126.9780]); // Seoul default
  const [mapZoom, setMapZoom] = useState(7);
  const [selectedMetric, setSelectedMetric] = useState<'today' | 'hour' | 'active'>('today');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedVehicleId, setSelectedVehicleId] = useState<string>('');
  
  // Use real-time alerts hook
  useRealtimeAlerts(undefined, (alert) => {
    setAlerts(prev => [alert, ...prev].slice(0, 10)); // Keep last 10 alerts
  });

  // Sync UVIS GPS data manually
  const handleSyncGPS = async () => {
    setSyncing(true);
    try {
      // Call backend to sync GPS data from UVIS
      const response = await uvisAPI.syncGPS({ force_new_key: false });
      toast.success(`GPS 데이터 동기화 완료: ${response.data.gps_count}건`);
      
      // Refresh vehicle data after sync
      await fetchRealtimeVehicles();
    } catch (error) {
      console.error('Failed to sync GPS:', error);
      toast.error('GPS 데이터 동기화에 실패했습니다');
    } finally {
      setSyncing(false);
    }
  };

  // Handle vehicle selection from dropdown
  const handleVehicleSelect = (vehicleId: string) => {
    setSelectedVehicleId(vehicleId);
    
    if (!vehicleId) return;
    
    const vehicle = vehicles.find(v => v.vehicle_id.toString() === vehicleId);
    if (vehicle && vehicle.latitude && vehicle.longitude) {
      setMapCenter([vehicle.latitude, vehicle.longitude]);
      setMapZoom(15); // Zoom in to selected vehicle
      toast.success(`${vehicle.vehicle_plate_number} 위치로 이동`);
    }
  };

  // Fetch real-time vehicle data from UVIS GPS
  const fetchRealtimeVehicles = async () => {
    try {
      const response = await uvisAPI.getRealtimeVehicles();
      const vehicleData = response.data.items || [];
      
      // Debug: Log raw data
      console.log('🚗 Fetched vehicles:', vehicleData.length);
      vehicleData.forEach((v: RealtimeVehicle) => {
        console.log(`   ${v.vehicle_plate_number}: engine=${v.is_engine_on}, speed=${v.speed_kmh}km/h, temp_a=${v.temperature_a}°C`);
      });
      
      // Filter vehicles with valid GPS coordinates and validate speed
      const validVehicles = vehicleData
        .filter((v: RealtimeVehicle) => v.latitude !== null && v.longitude !== null)
        .map((v: RealtimeVehicle) => {
          // Validate and correct speed (255 or >250 is GPS error)
          let correctedSpeed = v.speed_kmh;
          if (correctedSpeed >= 250 || correctedSpeed < 0) {
            console.warn(`⚠️ Invalid speed for ${v.vehicle_plate_number}: ${correctedSpeed}km/h → 0`);
            correctedSpeed = 0;
          }
          return { ...v, speed_kmh: correctedSpeed };
        });
      
      setVehicles(validVehicles);
      
      // Auto-center map to first vehicle if available
      if (validVehicles.length > 0 && validVehicles[0].latitude && validVehicles[0].longitude) {
        setMapCenter([validVehicles[0].latitude, validVehicles[0].longitude]);
      }
    } catch (error) {
      console.error('Failed to fetch realtime vehicles:', error);
      toast.error('차량 위치 정보를 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRealtimeVehicles();
    
    // Auto-refresh every 10 seconds (더 빠른 업데이트)
    const vehicleInterval = setInterval(fetchRealtimeVehicles, 10000);
    
    // Auto GPS sync every 2 minutes (UVIS 서버에서 최신 데이터 가져오기)
    const gpsInterval = setInterval(() => {
      console.log('🔄 Auto GPS sync triggered');
      handleSyncGPS();
    }, 120000);
    
    // Update clock every second
    const clockInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    
    return () => {
      clearInterval(vehicleInterval);
      clearInterval(gpsInterval);
      clearInterval(clockInterval);
    };
  }, []);

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ko-KR').format(num);
  };

  // Format time ago (e.g., "2분 전", "5초 전")
  const formatTimeAgo = (dateString: string): string => {
    if (!dateString) return '시간 정보 없음';
    
    // Use currentTime for real-time updates
    const now = currentTime;
    const past = new Date(dateString);
    const diffMs = now.getTime() - past.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSeconds < 10) return '방금 전';
    if (diffSeconds < 60) return `${diffSeconds}초 전`;
    if (diffMinutes < 60) return `${diffMinutes}분 전`;
    if (diffHours < 24) return `${diffHours}시간 전`;
    if (diffDays < 7) return `${diffDays}일 전`;
    
    // 7일 이상이면 날짜 표시
    return past.toLocaleString('ko-KR', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  const getMetricValue = () => {
    if (!dashboardData) return 0;
    
    switch (selectedMetric) {
      case 'today':
        return dashboardData.completed_today || 0;
      case 'hour':
        return 0; // Would need to be added to the DashboardMetrics type
      case 'active':
        return dashboardData.active_dispatches || 0;
      default:
        return 0;
    }
  };

  const getAlertCount = (severity: string) => {
    return alerts.filter(alert => alert.severity === severity).length;
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">실시간 모니터링 대시보드</h1>
              <p className="text-sm text-gray-500 mt-1">
                UVIS GPS 실시간 차량 추적 및 모니터링
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedMetric('today')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedMetric === 'today'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                오늘
              </button>
              <button
                onClick={() => setSelectedMetric('hour')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedMetric === 'hour'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                1시간
              </button>
              <button
                onClick={() => setSelectedMetric('active')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedMetric === 'active'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                활성
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {/* Active Dispatches */}
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">활성 배차</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {formatNumber(dashboardData?.active_dispatches || 0)}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
            </div>
          </div>

          {/* Completed Today */}
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">오늘 완료</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {formatNumber(dashboardData?.completed_today || 0)}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Active Vehicles */}
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">운행 차량</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {formatNumber(dashboardData?.vehicles_in_transit || 0)}
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
              </div>
            </div>
          </div>

          {/* Temperature Alerts */}
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">온도 알림</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {formatNumber(dashboardData?.temperature_alerts || 0)}
                </p>
              </div>
              <div className="p-3 bg-red-100 rounded-full">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Map View */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b bg-gray-50">
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">실시간 차량 위치</h2>
                    <p className="text-sm text-gray-500 mt-1">
                      UVIS GPS 실시간 추적 - {vehicles.length}대 운행 중
                      {loading && ' (불러오는 중...)'}
                    </p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      📡 10초마다 자동 새로고침 · 2분마다 GPS 동기화
                    </p>
                  </div>
                  <button
                    onClick={handleSyncGPS}
                    disabled={syncing || loading}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      syncing || loading
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    <svg
                      className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      />
                    </svg>
                    {syncing ? 'GPS 동기화 중...' : 'GPS 동기화'}
                  </button>
                </div>
                
                {/* Vehicle selector */}
                {vehicles.length > 0 && (
                  <div className="flex items-center gap-3">
                    <label htmlFor="vehicle-select" className="text-sm font-medium text-gray-700 whitespace-nowrap">
                      차량 찾기:
                    </label>
                    <select
                      id="vehicle-select"
                      value={selectedVehicleId}
                      onChange={(e) => handleVehicleSelect(e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">-- 차량을 선택하세요 --</option>
                      {vehicles
                        .sort((a, b) => a.vehicle_plate_number.localeCompare(b.vehicle_plate_number, 'ko-KR'))
                        .map((vehicle) => (
                          <option key={vehicle.vehicle_id} value={vehicle.vehicle_id}>
                            {vehicle.vehicle_plate_number}
                            {vehicle.is_engine_on ? ' 🟢' : ' 🟡'}
                            {vehicle.speed_kmh > 0 ? ` (${vehicle.speed_kmh}km/h)` : ''}
                          </option>
                        ))}
                    </select>
                  </div>
                )}
              </div>
              <div style={{ height: '500px' }}>
                {loading ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                      <p className="text-gray-600">차량 위치 정보를 불러오는 중...</p>
                    </div>
                  </div>
                ) : vehicles.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                      </svg>
                      <p className="mt-2 text-gray-600">운행 중인 차량이 없습니다</p>
                      <p className="mt-1 text-sm text-gray-500">차량에 UVIS GPS가 연결되면 여기에 표시됩니다</p>
                    </div>
                  </div>
                ) : (
                <MapContainer
                  center={mapCenter}
                  zoom={mapZoom}
                  style={{ height: '100%', width: '100%' }}
                  scrollWheelZoom={true}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  <MapCenterUpdater center={mapCenter} zoom={mapZoom} />
                  {vehicles.map((vehicle) => {
                    if (!vehicle.latitude || !vehicle.longitude) return null;
                    
                    // Determine vehicle status based on engine and speed
                    // is_engine_on can be true, false, or null/undefined
                    let status = 'idle'; // Default: 시동꺼짐
                    
                    if (vehicle.is_engine_on === true) {
                      // Engine is ON
                      if (vehicle.speed_kmh > 0) {
                        status = 'active'; // 운행중 (시동 ON + 주행)
                      } else {
                        status = 'active'; // 시동 ON (정차)
                      }
                    } else {
                      // Engine is OFF or unknown
                      status = 'idle'; // 시동꺼짐
                    }
                    
                    // Use temperature_a as primary, fallback to temperature_b
                    const temp = vehicle.temperature_a !== null ? vehicle.temperature_a : vehicle.temperature_b;
                    
                    return (
                      <Marker
                        key={vehicle.vehicle_id}
                        position={[vehicle.latitude, vehicle.longitude]}
                        icon={createVehicleIcon(vehicle.vehicle_plate_number, status, temp || undefined)}
                      >
                        <Popup>
                          <div className="p-2 min-w-[240px]">
                            <h3 className="font-bold text-base mb-2">{vehicle.vehicle_plate_number}</h3>
                            <div className="space-y-1 text-sm">
                              {/* Driver Information */}
                              {(vehicle.driver_name || vehicle.driver_phone) && (
                                <div className="pb-2 mb-2 border-b border-gray-200">
                                  {vehicle.driver_name && (
                                    <p className="text-gray-700 font-medium">
                                      👤 운전자: {vehicle.driver_name}
                                    </p>
                                  )}
                                  {vehicle.driver_phone && (
                                    <p className="text-gray-700">
                                      📞 연락처:{' '}
                                      <a
                                        href={`tel:${vehicle.driver_phone}`}
                                        className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          console.log(`📞 Calling ${vehicle.driver_name || vehicle.vehicle_plate_number}: ${vehicle.driver_phone}`);
                                        }}
                                      >
                                        {vehicle.driver_phone}
                                      </a>
                                    </p>
                                  )}
                                </div>
                              )}
                              <p>
                                <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${
                                  vehicle.is_engine_on ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                }`}>
                                  {vehicle.is_engine_on ? '🟢 시동 ON' : '🟡 시동 OFF'}
                                </span>
                                {vehicle.is_engine_on && vehicle.speed_kmh > 0 && (
                                  <span className="ml-2 inline-block px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800">
                                    🚗 운행중
                                  </span>
                                )}
                              </p>
                              <p className="text-gray-700">🚗 속도: {vehicle.speed_kmh} km/h</p>
                              {(vehicle.temperature_a !== null || vehicle.temperature_b !== null) && (
                                <>
                                  {vehicle.temperature_a !== null && (
                                    <p className={`font-semibold ${
                                      vehicle.temperature_a < -18 ? 'text-blue-600' :
                                      vehicle.temperature_a < 5 ? 'text-cyan-600' :
                                      vehicle.temperature_a < 15 ? 'text-green-600' :
                                      'text-orange-600'
                                    }`}>
                                      🌡️ 온도A: {vehicle.temperature_a.toFixed(1)}°C
                                    </p>
                                  )}
                                  {vehicle.temperature_b !== null && (
                                    <p className={`font-semibold ${
                                      vehicle.temperature_b < -18 ? 'text-blue-600' :
                                      vehicle.temperature_b < 5 ? 'text-cyan-600' :
                                      vehicle.temperature_b < 15 ? 'text-green-600' :
                                      'text-orange-600'
                                    }`}>
                                      🌡️ 온도B: {vehicle.temperature_b.toFixed(1)}°C
                                    </p>
                                  )}
                                </>
                              )}
                              <p className="text-gray-600 text-xs">
                                📍 {vehicle.latitude.toFixed(4)}, {vehicle.longitude.toFixed(4)}
                              </p>
                              <p className="text-gray-500 text-xs">
                                🔄 업데이트: {formatTimeAgo(vehicle.last_updated)}
                              </p>
                              <p className="text-gray-400 text-xs">
                                🕐 {new Date(vehicle.last_updated).toLocaleString('ko-KR', {
                                  month: '2-digit',
                                  day: '2-digit',
                                  hour: '2-digit',
                                  minute: '2-digit',
                                  second: '2-digit',
                                  hour12: false
                                })}
                              </p>
                              <p className="text-gray-400 text-xs">
                                ID: {vehicle.tid_id}
                              </p>
                            </div>
                          </div>
                        </Popup>
                      </Marker>
                    );
                  })}
                </MapContainer>
                )}
              </div>
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            {/* Recent Alerts */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b bg-gray-50">
                <h2 className="text-lg font-semibold text-gray-900">최근 알림</h2>
                <p className="text-sm text-gray-500 mt-1">실시간 알림 현황</p>
              </div>
              <div className="p-4 max-h-64 overflow-y-auto">
                {alerts.length > 0 ? (
                  <div className="space-y-2">
                    {alerts.slice(0, 5).map((alert, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg border-l-4 ${
                          alert.severity === 'critical' ? 'border-red-500 bg-red-50' :
                          alert.severity === 'warning' ? 'border-yellow-500 bg-yellow-50' :
                          'border-blue-500 bg-blue-50'
                        }`}
                      >
                        <p className="text-sm font-medium text-gray-900">
                          {alert.alert_type.replace(/_/g, ' ').toUpperCase()}
                        </p>
                        <p className="text-xs text-gray-600 mt-1">{alert.message}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(alert.timestamp).toLocaleTimeString('ko-KR')}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                    <p className="mt-2 text-sm">알림이 없습니다</p>
                  </div>
                )}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b bg-gray-50">
                <h2 className="text-lg font-semibold text-gray-900">빠른 통계</h2>
              </div>
              <div className="p-4 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">대기 주문</span>
                  <span className="text-lg font-bold text-gray-900">
                    {formatNumber(dashboardData?.pending_orders || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">완료 건수</span>
                  <span className="text-lg font-bold text-green-600">
                    {formatNumber(dashboardData?.completed_today || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">온도 알림</span>
                  <span className="text-lg font-bold text-red-600">
                    {formatNumber(dashboardData?.temperature_alerts || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">운행 차량</span>
                  <span className="text-lg font-bold text-purple-600">
                    {formatNumber(dashboardData?.vehicles_in_transit || 0)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      </div>
    </Layout>
  );
};

export default RealtimeDashboardPage;

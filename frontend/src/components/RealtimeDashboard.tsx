import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Icon, LatLngExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { uvisAPI } from '../services/api';

interface VehicleLocation {
  vehicle_id: number;
  vehicle_code: string;
  plate_number: string;
  latitude: number;
  longitude: number;
  speed: number;
  heading: number;
  timestamp: string;
}

interface VehicleTemperature {
  vehicle_id: number;
  vehicle_code: string;
  plate_number: string;
  temperature: number;
  zone: string;
  status: string;
  timestamp: string;
}

interface Alert {
  vehicle_id: number;
  vehicle_code: string;
  plate_number: string;
  type: string;
  severity: string;
  message: string;
  timestamp: string;
}

interface DashboardData {
  total_vehicles: number;
  active_vehicles: number;
  locations: VehicleLocation[];
  temperatures: VehicleTemperature[];
  alerts: Alert[];
}

// Vehicle marker icons
const createVehicleIcon = (zone: string, status: string) => {
  let color = '#10b981'; // default green
  
  if (status === 'warning') {
    color = '#f59e0b'; // orange
  }
  
  if (zone === 'frozen') {
    color = '#3b82f6'; // blue
  } else if (zone === 'chilled') {
    color = '#10b981'; // green
  } else {
    color = '#8b5cf6'; // purple
  }
  
  return new Icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${color}" width="32" height="32">
        <path d="M18 18.5C18 19.328 17.328 20 16.5 20H7.5C6.672 20 6 19.328 6 18.5V5.5C6 4.672 6.672 4 7.5 4H16.5C17.328 4 18 4.672 18 5.5V18.5ZM8 6V18H16V6H8Z"/>
      </svg>
    `)}`,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32]
  });
};

const RealtimeDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds

  // Seoul center coordinates
  const seoulCenter: LatLngExpression = [37.5665, 126.9780];

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await uvisAPI.getDashboard();
      setDashboardData(data);
    } catch (err: any) {
      console.error('Failed to fetch dashboard data:', err);
      setError(err.message || '대시보드 데이터 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchDashboardData();
    }, refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  const getTemperatureColor = (zone: string, status: string) => {
    if (status === 'warning') return 'text-orange-600';
    if (zone === 'frozen') return 'text-blue-600';
    if (zone === 'chilled') return 'text-green-600';
    return 'text-purple-600';
  };

  const getTemperatureIcon = (zone: string) => {
    if (zone === 'frozen') return '❄️';
    if (zone === 'chilled') return '🧊';
    return '🌡️';
  };

  const getSeverityColor = (severity: string) => {
    if (severity === 'critical') return 'bg-red-100 border-red-500 text-red-800';
    if (severity === 'warning') return 'bg-orange-100 border-orange-500 text-orange-800';
    return 'bg-blue-100 border-blue-500 text-blue-800';
  };

  if (!dashboardData) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">대시보드 로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">실시간 차량 모니터링</h1>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">자동 새로고침</span>
            </label>
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              disabled={!autoRefresh}
              className="rounded border-gray-300 text-sm"
            >
              <option value={10}>10초</option>
              <option value={30}>30초</option>
              <option value={60}>1분</option>
              <option value={300}>5분</option>
            </select>
          </div>
          <button
            onClick={fetchDashboardData}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm"
          >
            {loading ? '새로고침 중...' : '수동 새로고침'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
              <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">총 차량</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData.total_vehicles}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">활성 차량</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData.active_vehicles}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-purple-100 rounded-md p-3">
              <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">온도 정상</p>
              <p className="text-2xl font-semibold text-gray-900">
                {dashboardData.temperatures.filter(t => t.status === 'normal').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-orange-100 rounded-md p-3">
              <svg className="h-6 w-6 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">알림</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData.alerts.length}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">차량 위치</h2>
          </div>
          <div className="p-4">
            <div style={{ height: '600px' }}>
              <MapContainer
                center={seoulCenter}
                zoom={11}
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {dashboardData.locations.map((location) => {
                  const temp = dashboardData.temperatures.find(
                    (t) => t.vehicle_id === location.vehicle_id
                  );
                  const zone = temp?.zone || 'ambient';
                  const status = temp?.status || 'normal';
                  
                  return (
                    <Marker
                      key={location.vehicle_id}
                      position={[location.latitude, location.longitude]}
                      icon={createVehicleIcon(zone, status)}
                    >
                      <Popup>
                        <div className="p-2">
                          <h3 className="font-bold text-lg mb-2">{location.plate_number}</h3>
                          <p className="text-sm text-gray-600">차량코드: {location.vehicle_code}</p>
                          <p className="text-sm text-gray-600">속도: {location.speed.toFixed(1)} km/h</p>
                          {temp && (
                            <>
                              <p className={`text-sm font-semibold ${getTemperatureColor(temp.zone, temp.status)}`}>
                                {getTemperatureIcon(temp.zone)} {temp.temperature.toFixed(1)}°C
                              </p>
                              <p className="text-xs text-gray-500">
                                {temp.zone === 'frozen' ? '냉동' : temp.zone === 'chilled' ? '냉장' : '상온'}
                              </p>
                            </>
                          )}
                          <p className="text-xs text-gray-400 mt-2">
                            {new Date(location.timestamp).toLocaleString('ko-KR')}
                          </p>
                        </div>
                      </Popup>
                    </Marker>
                  );
                })}
              </MapContainer>
            </div>
          </div>
        </div>

        {/* Temperature and Alerts */}
        <div className="space-y-6">
          {/* Alerts */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">알림</h2>
            </div>
            <div className="p-4 max-h-80 overflow-y-auto">
              {dashboardData.alerts.length === 0 ? (
                <p className="text-gray-500 text-center py-4">알림이 없습니다</p>
              ) : (
                <div className="space-y-2">
                  {dashboardData.alerts.map((alert, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded border-l-4 ${getSeverityColor(alert.severity)}`}
                    >
                      <p className="font-semibold text-sm">{alert.plate_number}</p>
                      <p className="text-sm">{alert.message}</p>
                      <p className="text-xs mt-1 opacity-75">
                        {new Date(alert.timestamp).toLocaleString('ko-KR')}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Temperature List */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">차량 온도</h2>
            </div>
            <div className="p-4 max-h-80 overflow-y-auto">
              {dashboardData.temperatures.length === 0 ? (
                <p className="text-gray-500 text-center py-4">온도 데이터가 없습니다</p>
              ) : (
                <div className="space-y-2">
                  {dashboardData.temperatures.map((temp) => (
                    <div key={temp.vehicle_id} className="p-3 border border-gray-200 rounded">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-semibold text-sm">{temp.plate_number}</p>
                          <p className="text-xs text-gray-500">{temp.vehicle_code}</p>
                        </div>
                        <div className="text-right">
                          <p className={`text-lg font-bold ${getTemperatureColor(temp.zone, temp.status)}`}>
                            {getTemperatureIcon(temp.zone)} {temp.temperature.toFixed(1)}°C
                          </p>
                          <p className="text-xs text-gray-500">
                            {temp.zone === 'frozen' ? '냉동' : temp.zone === 'chilled' ? '냉장' : '상온'}
                          </p>
                        </div>
                      </div>
                      {temp.status === 'warning' && (
                        <p className="text-xs text-orange-600 mt-2">⚠️ 온도 이상</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealtimeDashboard;

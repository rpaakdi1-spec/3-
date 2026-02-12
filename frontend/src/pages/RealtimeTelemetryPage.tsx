import React, { useState, useEffect, useRef } from 'react';
import Layout from '../components/common/Layout';
import {
import Layout from '../components/common/Layout';
  MapPin,
  Activity,
  Zap,
  AlertTriangle,
  Thermometer,
  Gauge,
  Fuel,
  Clock,
  TrendingUp,
  RefreshCw,
  Circle,
  PlayCircle,
  StopCircle,
  CheckCircle
} from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';
const WS_URL = API_URL.replace('http', 'ws');

interface VehicleStatus {
  vehicle_id: number;
  plate_number: string;
  code: string;
  vehicle_type: string;
  status: 'moving' | 'idle' | 'offline';
  location: {
    latitude: number;
    longitude: number;
    speed: number;
    timestamp: string;
  } | null;
  active_dispatch: {
    dispatch_id: number;
    order_number: string;
    status: string;
  } | null;
}

interface TelemetryData {
  vehicle_id: number;
  latitude: number;
  longitude: number;
  speed: number;
  temperature?: number;
  fuel_level?: number;
  engine_status: string;
  timestamp: string;
}

interface Anomaly {
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  value: number;
  threshold: number;
}

interface Summary {
  total_vehicles: number;
  moving: number;
  idle: number;
  offline: number;
}

const RealtimeTelemetryPage: React.FC = () => {
  const [vehicles, setVehicles] = useState<VehicleStatus[]>([]);
  const [summary, setSummary] = useState<Summary>({
    total_vehicles: 0,
    moving: 0,
    idle: 0,
    offline: 0
  });
  const [selectedVehicle, setSelectedVehicle] = useState<VehicleStatus | null>(null);
  const [recentAnomalies, setRecentAnomalies] = useState<Array<{
    vehicle_id: number;
    vehicle_plate: string;
    anomaly: Anomaly;
    timestamp: string;
  }>>([]);
  const [loading, setLoading] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Load initial data
  useEffect(() => {
    loadVehicles();
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(`${WS_URL}/api/v1/ws/telemetry`);
      
      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        setWsConnected(true);
        
        // Send ping every 30 seconds
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 30000);
        
        (ws as any).pingInterval = pingInterval;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'telemetry_update') {
            handleTelemetryUpdate(message.data, message.anomalies);
          }
        } catch (error) {
          console.error('WebSocket message parse error:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setWsConnected(false);
        clearInterval((ws as any).pingInterval);
        
        // Reconnect after 5 seconds
        setTimeout(() => {
          connectWebSocket();
        }, 5000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  };

  const handleTelemetryUpdate = (data: TelemetryData, anomalies: Anomaly[]) => {
    // Update vehicle in list
    setVehicles(prev => prev.map(v => {
      if (v.vehicle_id === data.vehicle_id) {
        return {
          ...v,
          status: data.speed > 5 ? 'moving' : 'idle',
          location: {
            latitude: data.latitude,
            longitude: data.longitude,
            speed: data.speed,
            timestamp: data.timestamp
          }
        };
      }
      return v;
    }));

    // Add anomalies
    if (anomalies && anomalies.length > 0) {
      const vehicle = vehicles.find(v => v.vehicle_id === data.vehicle_id);
      if (vehicle) {
        anomalies.forEach(anomaly => {
          setRecentAnomalies(prev => [
            {
              vehicle_id: data.vehicle_id,
              vehicle_plate: vehicle.plate_number,
              anomaly,
              timestamp: new Date().toISOString()
            },
            ...prev.slice(0, 19) // Keep last 20
          ]);
        });
      }
    }
  };

  const loadVehicles = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const res = await axios.get(`${API_URL}/telemetry/vehicles/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setVehicles(res.data.vehicles);
      setSummary(res.data.summary);
    } catch (error) {
      console.error('Failed to load vehicles:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'moving': return 'text-green-600 bg-green-100';
      case 'idle': return 'text-yellow-600 bg-yellow-100';
      case 'offline': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getAnomalyIcon = (type: string) => {
    switch (type) {
      case 'speeding': return <Zap className="w-4 h-4" />;
      case 'harsh_braking': return <AlertTriangle className="w-4 h-4" />;
      case 'harsh_acceleration': return <TrendingUp className="w-4 h-4" />;
      case 'temperature_violation': return <Thermometer className="w-4 h-4" />;
      case 'low_fuel': return <Fuel className="w-4 h-4" />;
      case 'long_idle': return <Clock className="w-4 h-4" />;
      default: return <AlertTriangle className="w-4 h-4" />;
    }
  };

  return (
    <Layout>
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <Activity className="w-8 h-8 text-blue-600" />
                실시간 차량 텔레메트리
              </h1>
              <p className="text-gray-600 mt-1">차량 위치, 속도, 온도 등을 실시간으로 모니터링</p>
            </div>
            <div className="flex gap-2 items-center">
              <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
                wsConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                <Circle className={`w-2 h-2 ${wsConnected ? 'fill-green-600' : 'fill-red-600'}`} />
                <span className="text-sm font-medium">
                  {wsConnected ? 'WebSocket 연결됨' : 'WebSocket 연결 끊김'}
                </span>
              </div>
              <button
                onClick={loadVehicles}
                disabled={loading}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                새로고침
              </button>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">총 차량</span>
              <MapPin className="w-5 h-5 text-blue-500" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{summary.total_vehicles}</p>
            <p className="text-xs text-gray-500 mt-1">활성 차량</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">운행 중</span>
              <PlayCircle className="w-5 h-5 text-green-500" />
            </div>
            <p className="text-2xl font-bold text-green-600">{summary.moving}</p>
            <p className="text-xs text-gray-500 mt-1">속도 &gt; 5 km/h</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">정차 중</span>
              <StopCircle className="w-5 h-5 text-yellow-500" />
            </div>
            <p className="text-2xl font-bold text-yellow-600">{summary.idle}</p>
            <p className="text-xs text-gray-500 mt-1">속도 &le; 5 km/h</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">오프라인</span>
              <Circle className="w-5 h-5 text-gray-500" />
            </div>
            <p className="text-2xl font-bold text-gray-600">{summary.offline}</p>
            <p className="text-xs text-gray-500 mt-1">5분 이상 미수신</p>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Vehicle List */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">차량 목록</h2>
              <p className="text-sm text-gray-600 mt-1">
                {vehicles.length}대 차량 실시간 모니터링
              </p>
            </div>

            <div className="p-6 max-h-[600px] overflow-y-auto">
              {loading ? (
                <div className="text-center py-12">
                  <RefreshCw className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-4" />
                  <p className="text-gray-500">데이터 로딩 중...</p>
                </div>
              ) : vehicles.length === 0 ? (
                <div className="text-center py-12">
                  <MapPin className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">차량 없음</h3>
                  <p className="text-gray-500">활성 차량이 없습니다</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {vehicles.map((vehicle) => (
                    <div
                      key={vehicle.vehicle_id}
                      onClick={() => setSelectedVehicle(vehicle)}
                      className={`border rounded-lg p-4 cursor-pointer transition-all ${
                        selectedVehicle?.vehicle_id === vehicle.vehicle_id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                            {vehicle.plate_number}
                            <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(vehicle.status)}`}>
                              {vehicle.status === 'moving' ? '운행중' : vehicle.status === 'idle' ? '정차' : '오프라인'}
                            </span>
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">{vehicle.code}</p>
                        </div>
                        <MapPin className="w-5 h-5 text-gray-400" />
                      </div>

                      {vehicle.location && (
                        <div className="grid grid-cols-3 gap-3 text-sm">
                          <div className="bg-gray-50 p-2 rounded">
                            <span className="text-gray-500">속도</span>
                            <p className="font-bold text-gray-900">{vehicle.location.speed.toFixed(1)} km/h</p>
                          </div>
                          <div className="bg-gray-50 p-2 rounded">
                            <span className="text-gray-500">위도</span>
                            <p className="font-bold text-gray-900">{vehicle.location.latitude.toFixed(4)}</p>
                          </div>
                          <div className="bg-gray-50 p-2 rounded">
                            <span className="text-gray-500">경도</span>
                            <p className="font-bold text-gray-900">{vehicle.location.longitude.toFixed(4)}</p>
                          </div>
                        </div>
                      )}

                      {vehicle.active_dispatch && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <p className="text-xs text-gray-600">
                            활성 배차: <span className="font-medium text-gray-900">{vehicle.active_dispatch.order_number}</span>
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Recent Anomalies */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-orange-500" />
                최근 이상 감지
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                실시간 알림 ({recentAnomalies.length})
              </p>
            </div>

            <div className="p-6 max-h-[600px] overflow-y-auto">
              {recentAnomalies.length === 0 ? (
                <div className="text-center py-12">
                  <CheckCircle className="w-16 h-16 text-green-300 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">이상 없음</h3>
                  <p className="text-gray-500">모든 차량이 정상 운행 중입니다</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentAnomalies.map((item, idx) => (
                    <div
                      key={idx}
                      className={`border-l-4 p-3 rounded ${getSeverityColor(item.anomaly.severity)}`}
                    >
                      <div className="flex items-start gap-2">
                        {getAnomalyIcon(item.anomaly.type)}
                        <div className="flex-1">
                          <h4 className="font-semibold text-sm">{item.vehicle_plate}</h4>
                          <p className="text-sm mt-1">{item.anomaly.message}</p>
                          <p className="text-xs mt-1 opacity-75">
                            {new Date(item.timestamp).toLocaleTimeString('ko-KR')}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Selected Vehicle Details */}
        {selectedVehicle && selectedVehicle.location && (
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              선택된 차량: {selectedVehicle.plate_number}
            </h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                <div className="flex items-center gap-2 text-blue-700 mb-2">
                  <Gauge className="w-5 h-5" />
                  <span className="text-sm font-medium">속도</span>
                </div>
                <p className="text-2xl font-bold text-blue-900">
                  {selectedVehicle.location.speed.toFixed(1)} km/h
                </p>
              </div>

              <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
                <div className="flex items-center gap-2 text-green-700 mb-2">
                  <MapPin className="w-5 h-5" />
                  <span className="text-sm font-medium">위치</span>
                </div>
                <p className="text-sm font-bold text-green-900">
                  {selectedVehicle.location.latitude.toFixed(4)}, {selectedVehicle.location.longitude.toFixed(4)}
                </p>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                <div className="flex items-center gap-2 text-purple-700 mb-2">
                  <Activity className="w-5 h-5" />
                  <span className="text-sm font-medium">상태</span>
                </div>
                <p className="text-lg font-bold text-purple-900">
                  {selectedVehicle.status === 'moving' ? '운행중' : selectedVehicle.status === 'idle' ? '정차' : '오프라인'}
                </p>
              </div>

              <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg">
                <div className="flex items-center gap-2 text-orange-700 mb-2">
                  <Clock className="w-5 h-5" />
                  <span className="text-sm font-medium">업데이트</span>
                </div>
                <p className="text-sm font-bold text-orange-900">
                  {new Date(selectedVehicle.location.timestamp).toLocaleTimeString('ko-KR')}
                </p>
              </div>
            </div>

            {/* Map Placeholder */}
            <div className="mt-6 bg-gray-100 rounded-lg p-8 text-center">
              <MapPin className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-700 mb-2">지도 위치 표시</h3>
              <p className="text-gray-600">
                위도: {selectedVehicle.location.latitude}, 경도: {selectedVehicle.location.longitude}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Google Maps 또는 Mapbox API 연동으로 실제 지도에 표시 가능
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
    </Layout>
  );
};

export default RealtimeTelemetryPage;

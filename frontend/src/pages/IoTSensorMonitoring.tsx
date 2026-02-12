/**
 * IoT Sensor Monitoring Dashboard - Phase 13
 * Real-time vehicle sensor monitoring with alerts
 */
import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, ThermometerSun, Gauge, Battery, Droplet, TrendingUp, TrendingDown, Clock, CheckCircle, XCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { apiClient } from '../api/client';

interface Sensor {
  id: number;
  vehicle_id: number;
  sensor_type: string;
  sensor_name: string;
  min_threshold: number | null;
  max_threshold: number | null;
  unit: string;
  is_active: boolean;
}

interface SensorReading {
  id: number;
  sensor_id: number;
  vehicle_id: number;
  value: number;
  unit: string;
  is_anomaly: boolean;
  anomaly_score: number;
  recorded_at: string;
}

interface Alert {
  id: number;
  vehicle_id: number;
  severity: string;
  title: string;
  message: string;
  sensor_value: number;
  threshold_value: number;
  is_acknowledged: boolean;
  is_resolved: boolean;
  created_at: string;
}

const IoTSensorMonitoring: React.FC = () => {
  const [selectedVehicle, setSelectedVehicle] = useState<number>(1);
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedSensorType, setSelectedSensorType] = useState<string>('temperature');
  const [loading, setLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState<any>(null);

  useEffect(() => {
    loadDashboardData();
    loadVehicleSensors();
    loadAlerts();

    // 10초마다 자동 새로고침
    const interval = setInterval(() => {
      loadDashboardData();
      loadLatestReadings();
      loadAlerts();
    }, 10000);

    return () => clearInterval(interval);
  }, [selectedVehicle]);

  useEffect(() => {
    if (selectedSensorType) {
      loadLatestReadings();
    }
  }, [selectedSensorType, selectedVehicle]);

  const loadDashboardData = async () => {
    try {
      const response = await apiClient.get('/api/v1/iot/sensors/dashboard');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const loadVehicleSensors = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/api/v1/iot/sensors/vehicle/${selectedVehicle}`);
      setSensors(response.data.sensors || []);
    } catch (error) {
      console.error('Failed to load sensors:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadLatestReadings = async () => {
    try {
      const response = await apiClient.get(`/api/v1/iot/sensors/readings/${selectedVehicle}`, {
        params: {
          sensor_type: selectedSensorType,
          limit: 50
        }
      });
      setReadings(response.data.readings || []);
    } catch (error) {
      console.error('Failed to load readings:', error);
    }
  };

  const loadAlerts = async () => {
    try {
      const response = await apiClient.get('/api/v1/iot/sensors/alerts', {
        params: {
          vehicle_id: selectedVehicle,
          unresolved_only: true
        }
      });
      setAlerts(response.data.alerts || []);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    }
  };

  const acknowledgeAlert = async (alertId: number) => {
    try {
      await apiClient.post('/api/v1/iot/sensors/alerts/acknowledge', { alert_id: alertId });
      loadAlerts();
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const resolveAlert = async (alertId: number) => {
    try {
      await apiClient.post('/api/v1/iot/sensors/alerts/resolve', { 
        alert_id: alertId,
        resolution_notes: '확인 완료'
      });
      loadAlerts();
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    }
  };

  const getSensorIcon = (sensorType: string) => {
    const icons: { [key: string]: any } = {
      temperature: ThermometerSun,
      vibration: Activity,
      fuel: Droplet,
      tire_pressure: Gauge,
      battery: Battery
    };
    return icons[sensorType] || Activity;
  };

  const getSeverityColor = (severity: string) => {
    const colors: { [key: string]: string } = {
      info: 'text-blue-600 bg-blue-100',
      warning: 'text-yellow-600 bg-yellow-100',
      critical: 'text-red-600 bg-red-100'
    };
    return colors[severity] || 'text-gray-600 bg-gray-100';
  };

  // 차트 데이터 준비
  const chartData = readings
    .slice(0, 30)
    .reverse()
    .map(r => ({
      time: new Date(r.recorded_at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
      value: r.value,
      anomaly: r.is_anomaly ? r.value : null
    }));

  const latestReading = readings[0];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">🔌 IoT 센서 모니터링</h1>
          <p className="text-gray-600 mt-1">실시간 차량 센서 데이터 모니터링 및 이상 감지</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 px-4 py-2 bg-green-50 rounded-lg">
            <Activity className="w-5 h-5 text-green-600 animate-pulse" />
            <span className="text-sm font-medium text-green-700">실시간 업데이트</span>
          </div>
          <select
            value={selectedVehicle}
            onChange={(e) => setSelectedVehicle(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {[1, 2, 3, 4, 5].map(id => (
              <option key={id} value={id}>차량 {id}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Statistics Cards */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">모니터링 차량</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{dashboardData.vehicle_count}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">총 센서 데이터</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{dashboardData.total_readings}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Gauge className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">활성 알림</p>
                <p className="text-3xl font-bold text-red-600 mt-2">{dashboardData.active_alerts}</p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">이상 감지</p>
                <p className="text-3xl font-bold text-yellow-600 mt-2">{dashboardData.anomaly_count}</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sensor Type Selector */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">센서 선택</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {['temperature', 'vibration', 'fuel', 'tire_pressure', 'battery'].map(type => {
            const Icon = getSensorIcon(type);
            const sensorNames: { [key: string]: string } = {
              temperature: '온도',
              vibration: '진동',
              fuel: '연료',
              tire_pressure: '타이어 압력',
              battery: '배터리'
            };
            return (
              <button
                key={type}
                onClick={() => setSelectedSensorType(type)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedSensorType === type
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <Icon className={`w-6 h-6 mx-auto mb-2 ${
                  selectedSensorType === type ? 'text-blue-600' : 'text-gray-600'
                }`} />
                <p className={`text-sm font-medium ${
                  selectedSensorType === type ? 'text-blue-600' : 'text-gray-700'
                }`}>
                  {sensorNames[type]}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Real-time Chart */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-800">실시간 센서 데이터</h2>
          {latestReading && (
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-2xl font-bold text-gray-900">
                  {latestReading.value} {latestReading.unit}
                </p>
                <p className="text-sm text-gray-500">
                  {new Date(latestReading.recorded_at).toLocaleString('ko-KR')}
                </p>
              </div>
              {latestReading.is_anomaly && (
                <div className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                  ⚠️ 이상 감지
                </div>
              )}
            </div>
          )}
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#3B82F6"
              fill="#93C5FD"
              name="측정값"
            />
            <Line
              type="monotone"
              dataKey="anomaly"
              stroke="#EF4444"
              strokeWidth={3}
              dot={{ fill: '#EF4444', r: 6 }}
              name="이상값"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Active Alerts */}
      {alerts.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">🚨 활성 알림</h2>
          <div className="space-y-3">
            {alerts.map(alert => (
              <div
                key={alert.id}
                className={`p-4 rounded-lg border-2 ${
                  alert.severity === 'critical' ? 'border-red-300 bg-red-50' :
                  alert.severity === 'warning' ? 'border-yellow-300 bg-yellow-50' :
                  'border-blue-300 bg-blue-50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${getSeverityColor(alert.severity)}`}>
                        {alert.severity.toUpperCase()}
                      </span>
                      <h3 className="font-semibold text-gray-900">{alert.title}</h3>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{alert.message}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(alert.created_at).toLocaleString('ko-KR')}
                    </p>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    {!alert.is_acknowledged && (
                      <button
                        onClick={() => acknowledgeAlert(alert.id)}
                        className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                      >
                        확인
                      </button>
                    )}
                    <button
                      onClick={() => resolveAlert(alert.id)}
                      className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                    >
                      해결
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default IoTSensorMonitoring;

import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import Layout from '../components/common/Layout';
import { Thermometer, AlertTriangle, TrendingUp, TrendingDown, Activity, Clock, CheckCircle } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface TemperatureAlert {
  id: number;
  vehicle_id: number;
  vehicle_number: string;
  alert_type: string;
  severity: string;
  temperature: number;
  threshold_min: number;
  threshold_max: number;
  detected_at: string;
  message: string;
  notification_sent: boolean;
}

interface TemperatureHistory {
  timestamp: string;
  sensor: string;
  temperature: number;
}

interface VehicleTemperature {
  vehicle_id: number;
  vehicle_number: string;
  current_temp_a?: number;
  current_temp_b?: number;
  status: 'normal' | 'warning' | 'critical';
  last_updated: string;
}

const TemperatureMonitoringPage: React.FC = () => {
  const [activeAlerts, setActiveAlerts] = useState<TemperatureAlert[]>([]);
  const [vehicles, setVehicles] = useState<VehicleTemperature[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<number | null>(null);
  const [temperatureHistory, setTemperatureHistory] = useState<TemperatureHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [collectingData, setCollectingData] = useState(false);

  useEffect(() => {
    loadActiveAlerts();
    loadVehicles();
    
    // Auto refresh every 30 seconds
    const interval = setInterval(() => {
      loadActiveAlerts();
      if (selectedVehicle) {
        loadTemperatureHistory(selectedVehicle);
      }
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedVehicle) {
      loadTemperatureHistory(selectedVehicle);
    }
  }, [selectedVehicle]);

  const loadActiveAlerts = async () => {
    try {
      const response = await apiClient.get('/temperature-monitoring/alerts/active');
      setActiveAlerts(response.data);
    } catch (error) {
      console.error('Failed to load active alerts:', error);
    }
  };

  const loadVehicles = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/vehicles');
      
      // Mock temperature data for vehicles (in real scenario, this comes from backend)
      const vehiclesWithTemp = response.data.map((vehicle: any) => ({
        vehicle_id: vehicle.id,
        vehicle_number: vehicle.plate_number,
        current_temp_a: vehicle.gps_data?.temperature_a,
        current_temp_b: vehicle.gps_data?.temperature_b,
        status: getVehicleStatus(vehicle.gps_data?.temperature_a, vehicle.gps_data?.temperature_b),
        last_updated: vehicle.gps_data?.updated_at || new Date().toISOString()
      }));
      
      setVehicles(vehiclesWithTemp);
    } catch (error) {
      console.error('Failed to load vehicles:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTemperatureHistory = async (vehicleId: number) => {
    try {
      const response = await apiClient.get(`/temperature-monitoring/vehicles/${vehicleId}/history?hours=24`);
      setTemperatureHistory(response.data);
    } catch (error) {
      console.error('Failed to load temperature history:', error);
    }
  };

  const collectTemperatureData = async () => {
    try {
      setCollectingData(true);
      await apiClient.post('/temperature-monitoring/collect');
      await loadActiveAlerts();
      await loadVehicles();
      alert('온도 데이터 수집이 완료되었습니다.');
    } catch (error) {
      console.error('Failed to collect temperature data:', error);
      alert('온도 데이터 수집에 실패했습니다.');
    } finally {
      setCollectingData(false);
    }
  };

  const resolveAlert = async (alertId: number) => {
    try {
      await apiClient.post(`/temperature-monitoring/alerts/${alertId}/resolve`, {
        notes: '관리자가 수동으로 해결 처리함'
      });
      await loadActiveAlerts();
      alert('알림이 해결되었습니다.');
    } catch (error) {
      console.error('Failed to resolve alert:', error);
      alert('알림 해결에 실패했습니다.');
    }
  };

  const getVehicleStatus = (tempA?: number, tempB?: number): 'normal' | 'warning' | 'critical' => {
    if (!tempA && !tempB) return 'normal';
    
    // Frozen vehicle check (-25°C ~ -15°C)
    if (tempA !== undefined && (tempA < -25 || tempA > -15)) return 'critical';
    if (tempB !== undefined && (tempB < -25 || tempB > -15)) return 'critical';
    
    // Warning range
    if (tempA !== undefined && (tempA < -22 || tempA > -18)) return 'warning';
    if (tempB !== undefined && (tempB < -22 || tempB > -18)) return 'warning';
    
    return 'normal';
  };

  const getTemperatureColor = (temp?: number): string => {
    if (!temp) return 'text-gray-500';
    if (temp < -18) return 'text-blue-600';
    if (temp < 5) return 'text-cyan-600';
    if (temp < 15) return 'text-green-600';
    return 'text-orange-600';
  };

  const getSeverityBadge = (severity: string) => {
    const classes = severity === 'CRITICAL' 
      ? 'bg-red-100 text-red-800 border border-red-300'
      : 'bg-yellow-100 text-yellow-800 border border-yellow-300';
    
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${classes}`}>
        {severity === 'CRITICAL' ? '🚨 Critical' : '⚠️  Warning'}
      </span>
    );
  };

  const getStatusIcon = (status: string) => {
    if (status === 'critical') return <AlertTriangle className="w-5 h-5 text-red-500" />;
    if (status === 'warning') return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    return <CheckCircle className="w-5 h-5 text-green-500" />;
  };

  // Chart data
  const chartData = {
    labels: temperatureHistory
      .filter((h, i) => i % Math.ceil(temperatureHistory.length / 24) === 0) // Sample 24 points
      .map(h => new Date(h.timestamp).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })),
    datasets: [
      {
        label: 'Sensor A',
        data: temperatureHistory
          .filter((h, i) => h.sensor === 'A' && i % Math.ceil(temperatureHistory.length / 24) === 0)
          .map(h => h.temperature),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Sensor B',
        data: temperatureHistory
          .filter((h, i) => h.sensor === 'B' && i % Math.ceil(temperatureHistory.length / 24) === 0)
          .map(h => h.temperature),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '온도 이력 (24시간)'
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: '온도 (°C)'
        }
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Thermometer className="w-8 h-8 text-blue-600" />
            온도 모니터링
          </h1>
          <p className="text-sm text-gray-600 mt-1">실시간 차량 온도 모니터링 및 알림 관리</p>
        </div>
        <button
          onClick={collectTemperatureData}
          disabled={collectingData}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center gap-2"
        >
          <Activity className="w-4 h-4" />
          {collectingData ? '수집 중...' : '온도 데이터 수집'}
        </button>
      </div>

      {/* Active Alerts */}
      {activeAlerts.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <h2 className="text-lg font-semibold text-red-800">
              활성 알림 ({activeAlerts.length})
            </h2>
          </div>
          <div className="space-y-2">
            {activeAlerts.map(alert => (
              <div key={alert.id} className="bg-white rounded-lg p-3 flex justify-between items-center">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    {getSeverityBadge(alert.severity)}
                    <span className="font-medium">{alert.vehicle_number}</span>
                  </div>
                  <p className="text-sm text-gray-700">{alert.message}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    <Clock className="w-3 h-3 inline mr-1" />
                    {new Date(alert.detected_at).toLocaleString('ko-KR')}
                  </p>
                </div>
                <button
                  onClick={() => resolveAlert(alert.id)}
                  className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                >
                  해결
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Vehicle Temperature Grid */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">차량 온도 현황</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {vehicles.map(vehicle => (
            <div
              key={vehicle.vehicle_id}
              onClick={() => setSelectedVehicle(vehicle.vehicle_id)}
              className={`border rounded-lg p-4 cursor-pointer hover:shadow-lg transition-shadow ${
                selectedVehicle === vehicle.vehicle_id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <div className="font-medium text-gray-900">{vehicle.vehicle_number}</div>
                {getStatusIcon(vehicle.status)}
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Sensor A:</span>
                  <span className={`font-semibold ${getTemperatureColor(vehicle.current_temp_a)}`}>
                    {vehicle.current_temp_a !== undefined ? `${vehicle.current_temp_a.toFixed(1)}°C` : 'N/A'}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Sensor B:</span>
                  <span className={`font-semibold ${getTemperatureColor(vehicle.current_temp_b)}`}>
                    {vehicle.current_temp_b !== undefined ? `${vehicle.current_temp_b.toFixed(1)}°C` : 'N/A'}
                  </span>
                </div>
              </div>
              
              <div className="mt-3 pt-3 border-t border-gray-200">
                <p className="text-xs text-gray-500">
                  최종 업데이트: {new Date(vehicle.last_updated).toLocaleString('ko-KR')}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Temperature History Chart */}
      {selectedVehicle && temperatureHistory.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">
            온도 이력 - {vehicles.find(v => v.vehicle_id === selectedVehicle)?.vehicle_number}
          </h2>
          <div style={{ height: '400px' }}>
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>
      )}
      </div>
    </Layout>
  );
};

export default TemperatureMonitoringPage;

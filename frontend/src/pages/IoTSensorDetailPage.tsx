/**
 * IoT 센서 상세 페이지
 * 개별 차량의 센서 이력 및 차트 표시
 */

import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import { useParams, Link } from 'react-router-dom';
import {
  Thermometer,
  ArrowLeft,
  RefreshCw,
  Battery,
  Droplets,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
} from 'lucide-react';
import {
  getVehicleSensorDetail,
  type VehicleSensorDetail,
} from '../services/iotSensorService';

const IoTSensorDetailPage: React.FC = () => {
  const { vehicleId } = useParams<{ vehicleId: string }>();
  const [detail, setDetail] = useState<VehicleSensorDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('24h');

  const fetchDetail = async () => {
    if (!vehicleId) return;
    
    try {
      setLoading(true);
      const data = await getVehicleSensorDetail(vehicleId);
      setDetail(data);
    } catch (error) {
      console.error('센서 상세 정보 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
    
    // 30초마다 자동 새로고침
    const interval = setInterval(fetchDetail, 30000);
    
    return () => clearInterval(interval);
  }, [vehicleId]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'normal': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'normal': return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'warning': return <AlertTriangle className="w-6 h-6 text-yellow-600" />;
      case 'critical': return <XCircle className="w-6 h-6 text-red-600" />;
      default: return <Thermometer className="w-6 h-6 text-gray-600" />;
    }
  };

  const getBatteryColor = (level?: number) => {
    if (!level) return 'text-gray-400';
    if (level > 50) return 'text-green-600';
    if (level > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  // 온도 변화 계산
  const getTemperatureTrend = () => {
    if (!detail || detail.history.length < 2) return null;
    
    const latest = detail.history[detail.history.length - 1];
    const previous = detail.history[detail.history.length - 2];
    const diff = latest.temperature - previous.temperature;
    
    if (Math.abs(diff) < 0.5) return null;
    
    return diff > 0 ? (
      <div className="flex items-center gap-1 text-red-600">
        <TrendingUp className="w-4 h-4" />
        <span>+{diff.toFixed(1)}°C</span>
      </div>
    ) : (
      <div className="flex items-center gap-1 text-blue-600">
        <TrendingDown className="w-4 h-4" />
        <span>{diff.toFixed(1)}°C</span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-3 text-gray-600">데이터 로딩 중...</span>
        </div>
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="text-center py-12">
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <p className="text-xl text-gray-600">센서 데이터를 찾을 수 없습니다</p>
          <Link
            to="/iot/sensors"
            className="mt-4 inline-block text-blue-600 hover:text-blue-800"
          >
            ← 목록으로 돌아가기
          </Link>
        </div>
      </div>
    );
  }

  return (
    <Layout>
    <div className="min-h-screen bg-gray-50 p-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link
            to="/iot/sensors"
            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-6 h-6 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              {detail.vehicle_id} 센서 상세
            </h1>
            <p className="text-gray-600 mt-1">
              센서 ID: {detail.sensor_id}
            </p>
          </div>
        </div>
        <button
          onClick={fetchDetail}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          새로고침
        </button>
      </div>

      {/* 현재 상태 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">현재 온도</p>
            <Thermometer className="w-5 h-5 text-blue-500" />
          </div>
          <div className="flex items-end gap-2">
            <p className="text-3xl font-bold text-gray-900">
              {detail.current_temperature.toFixed(1)}°C
            </p>
            {getTemperatureTrend()}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">배터리</p>
            <Battery className={`w-5 h-5 ${getBatteryColor(detail.battery_level)}`} />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {detail.battery_level || '-'}%
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">상태</p>
            {getStatusIcon(detail.current_status)}
          </div>
          <p className={`text-2xl font-bold ${getStatusColor(detail.current_status)}`}>
            {detail.current_status === 'normal' ? '정상' : 
             detail.current_status === 'warning' ? '경고' : 
             detail.current_status === 'critical' ? '위험' : '알 수 없음'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">마지막 업데이트</p>
            <RefreshCw className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-sm font-medium text-gray-900">
            {new Date(detail.last_update).toLocaleString('ko-KR')}
          </p>
        </div>
      </div>

      {/* 온도 이력 차트 (간단한 텍스트 기반) */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900">온도 이력</h2>
          <div className="flex gap-2">
            {(['1h', '6h', '24h', '7d'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 text-sm rounded ${
                  timeRange === range
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {range === '1h' ? '1시간' : range === '6h' ? '6시간' : range === '24h' ? '24시간' : '7일'}
              </button>
            ))}
          </div>
        </div>
        
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="text-xs text-gray-500 uppercase">
                  <th className="text-left py-2">시간</th>
                  <th className="text-left py-2">온도</th>
                  <th className="text-left py-2">습도</th>
                  <th className="text-left py-2">배터리</th>
                  <th className="text-left py-2">상태</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {detail.history.slice(-20).reverse().map((item, idx) => (
                  <tr key={idx} className="text-sm">
                    <td className="py-2 text-gray-600">
                      {new Date(item.timestamp).toLocaleTimeString('ko-KR')}
                    </td>
                    <td className="py-2">
                      <div className="flex items-center gap-2">
                        <Thermometer className="w-4 h-4 text-gray-400" />
                        <span className="font-medium">{item.temperature.toFixed(1)}°C</span>
                      </div>
                    </td>
                    <td className="py-2">
                      {item.humidity ? (
                        <div className="flex items-center gap-2">
                          <Droplets className="w-4 h-4 text-blue-400" />
                          <span>{item.humidity.toFixed(0)}%</span>
                        </div>
                      ) : '-'}
                    </td>
                    <td className="py-2">
                      {item.battery_level ? `${item.battery_level}%` : '-'}
                    </td>
                    <td className="py-2">
                      <span className={`text-xs font-medium ${getStatusColor(item.status)}`}>
                        {item.status === 'normal' ? '정상' : 
                         item.status === 'warning' ? '경고' : 
                         item.status === 'critical' ? '위험' : item.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* 알림 이력 */}
      {detail.alerts && detail.alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">알림 이력</h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {detail.alerts.slice(0, 10).map((alert) => (
                <div
                  key={alert.id}
                  className={`flex items-start gap-3 p-4 rounded-lg border ${
                    alert.alert_level === 'CRITICAL'
                      ? 'bg-red-50 border-red-200'
                      : alert.alert_level === 'WARNING'
                      ? 'bg-yellow-50 border-yellow-200'
                      : 'bg-blue-50 border-blue-200'
                  }`}
                >
                  {alert.alert_level === 'CRITICAL' ? (
                    <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  ) : alert.alert_level === 'WARNING' ? (
                    <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  ) : (
                    <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(alert.timestamp).toLocaleString('ko-KR')}
                    </p>
                  </div>
                  {alert.acknowledged && (
                    <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">
                      확인됨
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
    </Layout>
  );
};

export default IoTSensorDetailPage;

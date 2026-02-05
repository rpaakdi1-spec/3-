/**
 * IoT 센서 모니터링 대시보드
 * 실시간 센서 데이터 표시 및 알림 관리
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Thermometer, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  RefreshCw,
  Bell,
  Battery,
  Droplets
} from 'lucide-react';
import {
  getSensorData,
  getSensorStatistics,
  type SensorData,
  type SensorStatistics,
} from '../services/iotSensorService';

const IoTSensorsPage: React.FC = () => {
  const [sensors, setSensors] = useState<SensorData[]>([]);
  const [stats, setStats] = useState<SensorStatistics>({ total: 0, normal: 0, warning: 0, critical: 0 });
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // 데이터 로딩
  const fetchData = async () => {
    try {
      setLoading(true);
      const [sensorData, statistics] = await Promise.all([
        getSensorData(),
        getSensorStatistics(),
      ]);
      
      setSensors(sensorData);
      setStats(statistics);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('센서 데이터 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // 10초마다 자동 새로고침
    const interval = setInterval(fetchData, 10000);
    
    return () => clearInterval(interval);
  }, []);

  // 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'normal': return 'bg-green-100 text-green-800 border-green-300';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'normal': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'critical': return <XCircle className="w-5 h-5 text-red-600" />;
      default: return <Thermometer className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'normal': return '정상';
      case 'warning': return '경고';
      case 'critical': return '위험';
      default: return '알 수 없음';
    }
  };

  // 배터리 색상
  const getBatteryColor = (level?: number) => {
    if (!level) return 'text-gray-400';
    if (level > 50) return 'text-green-600';
    if (level > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Thermometer className="w-8 h-8 text-blue-600" />
            IoT 센서 모니터링
          </h1>
          <p className="text-gray-600 mt-1">
            실시간 센서 데이터 모니터링 및 알림 관리
          </p>
        </div>
        <div className="flex gap-3">
          <Link
            to="/iot/alerts"
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Bell className="w-4 h-4" />
            알림 센터
          </Link>
          <button
            onClick={fetchData}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            새로고침
          </button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">전체 센서</p>
              <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <Thermometer className="w-10 h-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">정상</p>
              <p className="text-3xl font-bold text-green-600">{stats.normal}</p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">경고</p>
              <p className="text-3xl font-bold text-yellow-600">{stats.warning}</p>
            </div>
            <AlertTriangle className="w-10 h-10 text-yellow-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">위험</p>
              <p className="text-3xl font-bold text-red-600">{stats.critical}</p>
            </div>
            <XCircle className="w-10 h-10 text-red-500" />
          </div>
        </div>
      </div>

      {/* 센서 목록 */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">센서 현황</h2>
          <p className="text-sm text-gray-500 mt-1">
            마지막 업데이트: {lastUpdate.toLocaleString('ko-KR')}
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-3 text-gray-600">데이터 로딩 중...</span>
          </div>
        ) : sensors.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            센서 데이터가 없습니다
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    차량 ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    센서 ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    온도
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    습도
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    배터리
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    상태
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    업데이트 시간
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    작업
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sensors.map((sensor) => (
                  <tr key={sensor.sensor_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {sensor.vehicle_id}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{sensor.sensor_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <Thermometer className="w-4 h-4 text-gray-400" />
                        <span className="text-sm font-medium">{sensor.temperature.toFixed(1)}°C</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {sensor.humidity ? (
                        <div className="flex items-center gap-2">
                          <Droplets className="w-4 h-4 text-blue-400" />
                          <span className="text-sm">{sensor.humidity.toFixed(0)}%</span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {sensor.battery_level ? (
                        <div className="flex items-center gap-2">
                          <Battery className={`w-4 h-4 ${getBatteryColor(sensor.battery_level)}`} />
                          <span className="text-sm">{sensor.battery_level}%</span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(sensor.status)}`}>
                        {getStatusIcon(sensor.status)}
                        {getStatusText(sensor.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(sensor.timestamp).toLocaleString('ko-KR')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Link
                        to={`/iot/sensors/${sensor.vehicle_id}`}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        상세보기 →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 알림 메시지 (있는 경우) */}
      {sensors.some(s => s.messages && s.messages.length > 0) && (
        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-yellow-800 mb-2 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            활성 알림
          </h3>
          <ul className="space-y-1">
            {sensors
              .filter(s => s.messages && s.messages.length > 0)
              .flatMap(s => s.messages?.map((msg, idx) => (
                <li key={`${s.sensor_id}-${idx}`} className="text-sm text-yellow-700">
                  [{s.vehicle_id} / {s.sensor_id}] {msg}
                </li>
              )))
            }
          </ul>
        </div>
      )}
    </div>
  );
};

export default IoTSensorsPage;

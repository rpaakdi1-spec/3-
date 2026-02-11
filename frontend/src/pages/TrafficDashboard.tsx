import React, { useEffect, useState } from 'react';
import { MapPin, AlertTriangle, TrendingUp, Clock, DollarSign, Navigation } from 'lucide-react';

interface TrafficCondition {
  id: number;
  road_name: string;
  section_name: string | null;
  traffic_level: string;
  speed: number | null;
  travel_time: number | null;
  api_provider: string;
  collected_at: string;
}

interface TrafficAlert {
  id: number;
  alert_type: string;
  title: string;
  description: string | null;
  road_name: string | null;
  severity: string;
  is_active: boolean;
  created_at: string;
}

interface TrafficStats {
  level: string;
  count: number;
  avg_speed: number;
}

const TrafficDashboard: React.FC = () => {
  const [conditions, setConditions] = useState<TrafficCondition[]>([]);
  const [alerts, setAlerts] = useState<TrafficAlert[]>([]);
  const [statistics, setStatistics] = useState<TrafficStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // 30초마다 갱신
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // 교통 상황
      const conditionsRes = await fetch('/api/v1/traffic/conditions?limit=10', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const conditionsData = await conditionsRes.json();
      setConditions(conditionsData.conditions || []);

      // 교통 알림
      const alertsRes = await fetch('/api/v1/traffic/alerts?is_active=true&limit=10', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const alertsData = await alertsRes.json();
      setAlerts(alertsData.alerts || []);

      // 교통 통계
      const statsRes = await fetch('/api/v1/traffic/statistics?days=7', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const statsData = await statsRes.json();
      setStatistics(statsData.traffic_levels || []);

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch traffic data:', error);
      setLoading(false);
    }
  };

  const getTrafficLevelColor = (level: string) => {
    switch (level) {
      case 'SMOOTH': return 'bg-green-100 text-green-800';
      case 'NORMAL': return 'bg-blue-100 text-blue-800';
      case 'SLOW': return 'bg-yellow-100 text-yellow-800';
      case 'CONGESTED': return 'bg-orange-100 text-orange-800';
      case 'BLOCKED': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTrafficLevelText = (level: string) => {
    switch (level) {
      case 'SMOOTH': return '원활';
      case 'NORMAL': return '보통';
      case 'SLOW': return '서행';
      case 'CONGESTED': return '혼잡';
      case 'BLOCKED': return '정체';
      default: return level;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'LOW': return 'bg-blue-100 text-blue-800';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800';
      case 'HIGH': return 'bg-orange-100 text-orange-800';
      case 'CRITICAL': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Navigation className="h-8 w-8 mr-3 text-blue-600" />
          실시간 교통 현황
        </h1>
        <p className="text-gray-600 mt-2">도로 혼잡도 및 교통 알림</p>
      </div>

      {/* Traffic Statistics */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <TrendingUp className="h-6 w-6 mr-2 text-blue-600" />
          최근 7일 교통 통계
        </h2>
        
        {statistics.length === 0 ? (
          <p className="text-gray-500">통계 데이터가 없습니다</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {statistics.map((stat, index) => (
              <div key={index} className={`rounded-lg p-4 ${getTrafficLevelColor(stat.level)}`}>
                <p className="text-sm font-medium">{getTrafficLevelText(stat.level)}</p>
                <p className="text-2xl font-bold mt-1">{stat.count}</p>
                <p className="text-xs mt-1">평균 {stat.avg_speed.toFixed(1)} km/h</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Traffic Alerts */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <AlertTriangle className="h-6 w-6 mr-2 text-orange-600" />
          교통 알림
        </h2>
        
        {alerts.length === 0 ? (
          <p className="text-gray-500">현재 활성 알림이 없습니다</p>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div key={alert.id} className="border-l-4 border-orange-500 bg-orange-50 p-4 rounded">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                      <span className="text-xs text-gray-500">{alert.alert_type}</span>
                    </div>
                    <h3 className="font-bold text-gray-900 mt-2">{alert.title}</h3>
                    {alert.description && (
                      <p className="text-gray-700 mt-1">{alert.description}</p>
                    )}
                    {alert.road_name && (
                      <p className="text-sm text-gray-600 mt-2">
                        <MapPin className="h-4 w-4 inline mr-1" />
                        {alert.road_name}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Traffic Conditions */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
          <Clock className="h-6 w-6 mr-2 text-blue-600" />
          실시간 교통 상황
        </h2>
        
        {conditions.length === 0 ? (
          <p className="text-gray-500">교통 상황 데이터가 없습니다</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    도로명
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    구간
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    혼잡도
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    평균 속도
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    수집 시각
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {conditions.map((condition) => (
                  <tr key={condition.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {condition.road_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {condition.section_name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getTrafficLevelColor(condition.traffic_level)}`}>
                        {getTrafficLevelText(condition.traffic_level)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {condition.speed ? `${condition.speed.toFixed(1)} km/h` : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(condition.collected_at).toLocaleString('ko-KR')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrafficDashboard;

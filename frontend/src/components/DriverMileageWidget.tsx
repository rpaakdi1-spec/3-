import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { TrendingUp, User, Activity } from 'lucide-react';
import Card from './common/Card';

interface TopDriver {
  rank: number;
  driver_id: number;
  driver_code: string;
  driver_name: string;
  total_distance_km: number;
  driving_days: number;
  avg_distance_per_day: number;
  avg_speed_kmh: number;
}

interface DriverMileageWidgetProps {
  limit?: number;
}

const DriverMileageWidget: React.FC<DriverMileageWidgetProps> = ({ limit = 5 }) => {
  const [topDrivers, setTopDrivers] = useState<TopDriver[]>([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState<string>('');
  const navigate = useNavigate();

  const API_BASE_URL = '';

  useEffect(() => {
    fetchTopDrivers();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchTopDrivers, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [limit]);

  const fetchTopDrivers = async () => {
    try {
      const response = await api.get(
        `${API_BASE_URL}/driver-mileage/top-drivers?limit=${limit}`
      );
      setTopDrivers(response.data.top_drivers || []);
      setPeriod(response.data.period || '');
      setLoading(false);
    } catch (error) {
      console.error('Top drivers fetch failed:', error);
      setLoading(false);
    }
  };

  const getMedalEmoji = (rank: number) => {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return `${rank}위`;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="flex items-center mb-4">
          <div className="w-5 h-5 bg-gray-200 rounded mr-2" />
          <div className="h-5 bg-gray-200 rounded w-36" />
        </div>
        {[...Array(4)].map((_, i) => (
          <div key={i} className="flex items-center py-3 border-b border-gray-100 last:border-0">
            <div className="w-8 h-8 bg-gray-200 rounded-full mr-3" />
            <div className="flex-1">
              <div className="h-4 bg-gray-200 rounded w-24 mb-1" />
              <div className="h-3 bg-gray-100 rounded w-16" />
            </div>
            <div className="h-4 bg-gray-200 rounded w-16" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <Card>
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
              Top 운전자 주행거리
            </h3>
            {period && (
              <p className="text-sm text-gray-500 mt-1">{period}</p>
            )}
          </div>
          <button
            onClick={() => navigate('/driver-mileage')}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            전체 보기 →
          </button>
        </div>

        {topDrivers.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Activity className="w-12 h-12 mx-auto mb-2 text-gray-400" />
            <p>주행 데이터가 없습니다</p>
          </div>
        ) : (
          <div className="space-y-3">
            {topDrivers.map((driver) => (
              <div
                key={driver.driver_id}
                className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex-shrink-0 w-12 text-center">
                  <span className="text-lg font-bold">
                    {getMedalEmoji(driver.rank)}
                  </span>
                </div>
                
                <div className="flex-1 min-w-0 ml-3">
                  <div className="flex items-center mb-1">
                    <User className="w-4 h-4 mr-1 text-gray-500" />
                    <span className="text-sm font-medium text-gray-900 truncate">
                      {driver.driver_name}
                    </span>
                    <span className="ml-2 text-xs text-gray-500">
                      ({driver.driver_code})
                    </span>
                  </div>
                  
                  <div className="flex items-center text-xs text-gray-600">
                    <span className="mr-3">
                      <span className="font-semibold text-blue-600">
                        {driver.total_distance_km.toFixed(0)}
                      </span>{' '}
                      km
                    </span>
                    <span className="mr-3">
                      {driver.driving_days}일 운행
                    </span>
                    <span>
                      평균 {driver.avg_distance_per_day.toFixed(0)} km/일
                    </span>
                  </div>
                </div>
                
                <div className="flex-shrink-0 text-right ml-3">
                  <div className="text-sm font-semibold text-gray-900">
                    {driver.avg_speed_kmh.toFixed(1)}
                  </div>
                  <div className="text-xs text-gray-500">
                    km/h
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-4 pt-4 border-t border-gray-200">
          <button
            onClick={() => navigate('/driver-mileage')}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            상세 보기
          </button>
        </div>
      </div>
    </Card>
  );
};

export default DriverMileageWidget;

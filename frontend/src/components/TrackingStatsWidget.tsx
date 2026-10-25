import React, { useEffect, useState } from 'react';
import { MapPin, TrendingUp, CheckCircle, Clock, Navigation } from 'lucide-react';
import apiClient from '../api/client';
import Card from './common/Card';

interface TrackingStats {
  in_progress: number;
  completed_today: number;
  avg_delivery_time_minutes: number;
  active_deliveries: Array<{
    tracking_number: string;
    dispatch_number: string;
    current_location: { lat: number; lon: number } | null;
    progress_percent: number;
    vehicle_plate: string;
  }>;
  last_updated: string;
}

const TrackingStatsWidget: React.FC = () => {
  const [stats, setStats] = useState<TrackingStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await apiClient.get('/dispatch/tracking/statistics');
      setStats(response.data);
      if (loading) setLoading(false);
    } catch (error) {
      console.error('추적 통계 조회 실패:', error);
      if (loading) setLoading(false);
    }
  };

  const formatTime = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}시간 ${mins}분`;
    }
    return `${mins}분`;
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-4 animate-pulse">
            <div className="flex items-center justify-between">
              <div>
                <div className="h-3 bg-gray-200 rounded w-20 mb-2" />
                <div className="h-8 bg-gray-200 rounded w-12" />
              </div>
              <div className="w-12 h-12 bg-gray-100 rounded-full" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="space-y-4">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* In Progress */}
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">진행 중 배송</p>
                <p className="text-3xl font-bold text-blue-600">{stats.in_progress}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <Navigation size={24} className="text-blue-600" />
              </div>
            </div>
          </div>
        </Card>

        {/* Completed Today */}
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">오늘 완료</p>
                <p className="text-3xl font-bold text-green-600">{stats.completed_today}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <CheckCircle size={24} className="text-green-600" />
              </div>
            </div>
          </div>
        </Card>

        {/* Average Time */}
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">평균 배송 시간</p>
                <p className="text-3xl font-bold text-purple-600">
                  {formatTime(stats.avg_delivery_time_minutes)}
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <Clock size={24} className="text-purple-600" />
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Active Deliveries List */}
      {stats.active_deliveries && stats.active_deliveries.length > 0 && (
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <MapPin size={20} className="mr-2 text-blue-600" />
                실시간 배송 현황
              </h3>
              <span className="text-xs text-gray-500">
                {new Date(stats.last_updated).toLocaleTimeString('ko-KR')} 업데이트
              </span>
            </div>

            <div className="space-y-3">
              {stats.active_deliveries.slice(0, 5).map((delivery) => (
                <div
                  key={delivery.tracking_number}
                  className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-medium text-gray-900">
                        {delivery.tracking_number}
                      </span>
                      {delivery.vehicle_plate && (
                        <span className="text-xs text-gray-600">
                          ({delivery.vehicle_plate})
                        </span>
                      )}
                    </div>
                    <span className="text-sm font-medium text-blue-600">
                      {delivery.progress_percent}%
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${delivery.progress_percent}%` }}
                    ></div>
                  </div>

                  {/* Location */}
                  {delivery.current_location && (
                    <div className="flex items-center text-xs text-gray-600">
                      <MapPin size={14} className="mr-1" />
                      <span>
                        {delivery.current_location.lat.toFixed(4)}, {delivery.current_location.lon.toFixed(4)}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {stats.active_deliveries.length > 5 && (
              <div className="mt-3 text-center">
                <button
                  onClick={() => window.location.href = '/dispatches'}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  전체 {stats.active_deliveries.length}건 보기 →
                </button>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};

export default TrackingStatsWidget;

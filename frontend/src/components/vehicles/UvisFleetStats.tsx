import React, { useState, useEffect } from 'react';
import { TrendingUp, Activity, Gauge, MapPin } from 'lucide-react';
import Card from '../common/Card';
import { toast } from 'react-hot-toast';

interface VehicleStat {
  vehicle_id: number;
  vehicle_plate: string;
  total_distance_km: number;
  max_speed_kmh: number;
  avg_speed_kmh: number;
  engine_on_ratio: number;
  data_points: number;
}

interface FleetStats {
  total_vehicles: number;
  active_vehicles: number;
  total_distance_km: number;
  avg_distance_per_vehicle_km: number;
  vehicle_stats: VehicleStat[];
}

interface UvisFleetStatsProps {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const UvisFleetStats: React.FC<UvisFleetStatsProps> = ({
  autoRefresh = true,
  refreshInterval = 30000, // 30초
}) => {
  const [stats, setStats] = useState<FleetStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const today = new Date();
      const endDate = today.toISOString().split('T')[0];
      
      // 최근 7일 데이터 조회 (GPS 데이터가 오래된 경우를 위해)
      const startDate = new Date(today);
      startDate.setDate(today.getDate() - 7);
      const start = startDate.toISOString().split('T')[0];
      
      const response = await fetch(`/api/v1/vehicles/analytics/fleet?start_date=${start}&end_date=${endDate}`);
      const data = await response.json();
      
      setStats(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch fleet stats:', error);
      toast.error('차량 통계 조회에 실패했습니다');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    
    if (autoRefresh) {
      const interval = setInterval(fetchStats, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-24 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-16"></div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  // Calculate statistics from vehicle_stats
  const vehicleStats = stats.vehicle_stats || [];
  const engineOnCount = vehicleStats.filter(v => v.engine_on_ratio > 50).length;
  const avgSpeed = vehicleStats.length > 0
    ? vehicleStats.reduce((sum, v) => sum + (v.avg_speed_kmh || 0), 0) / vehicleStats.length
    : 0;
  const maxSpeed = vehicleStats.length > 0
    ? Math.max(...vehicleStats.map(v => v.max_speed_kmh || 0))
    : 0;

  const statCards = [
    {
      title: '운행 중 차량',
      value: engineOnCount,
      total: stats.total_vehicles,
      unit: '대',
      icon: <Activity className="text-green-600" size={24} />,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: '총 주행 거리',
      value: (stats.total_distance_km || 0).toFixed(1),
      unit: 'km',
      icon: <MapPin className="text-blue-600" size={24} />,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      subtitle: `${stats.active_vehicles}대 GPS 데이터`,
    },
    {
      title: '평균 속도',
      value: avgSpeed.toFixed(1),
      unit: 'km/h',
      icon: <Gauge className="text-purple-600" size={24} />,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: '최고 속도',
      value: maxSpeed.toFixed(1),
      unit: 'km/h',
      icon: <TrendingUp className="text-orange-600" size={24} />,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">UVIS 실시간 통계</h2>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span>실시간 업데이트</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <div className="space-y-3">
              {/* 아이콘 및 제목 */}
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-gray-600 font-medium">{stat.title}</p>
                  {stat.subtitle && (
                    <p className="text-xs text-gray-400 mt-1">{stat.subtitle}</p>
                  )}
                </div>
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  {stat.icon}
                </div>
              </div>
              
              {/* 값 */}
              <div className="flex items-baseline gap-2">
                <span className={`text-3xl font-bold ${stat.color}`}>
                  {stat.value}
                </span>
                <span className="text-sm text-gray-500">{stat.unit}</span>
                {stat.total !== undefined && (
                  <span className="text-sm text-gray-400">/ {stat.total}대</span>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default UvisFleetStats;

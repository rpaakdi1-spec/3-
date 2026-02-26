import React, { useEffect, useState } from 'react';
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
  Filler,
} from 'chart.js';
import { Thermometer, AlertTriangle, Snowflake } from 'lucide-react';
import Card from '../common/Card';
import { toast } from 'react-hot-toast';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

interface TemperatureDataPoint {
  timestamp: string;
  temperature: number;
  recorded_at: string | null;
}

interface Thresholds {
  frozen_min: number;
  frozen_max: number;
  refrigerated_min: number;
  refrigerated_max: number;
  warning: number;
  critical: number;
}

interface VehicleTempRange {
  min: number;
  max: number;
}

interface TemperatureData {
  vehicle_id: number;
  vehicle_plate: string;
  vehicle_type: string;
  vehicle_temp_range: VehicleTempRange;
  hours: number;
  data_points: TemperatureDataPoint[];
  total_points: number;
  thresholds: Thresholds;
}

interface UvisTemperatureChartProps {
  vehicleId: number;
  hours?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const UvisTemperatureChart: React.FC<UvisTemperatureChartProps> = ({
  vehicleId,
  hours = 24,
  autoRefresh = true,
  refreshInterval = 30000,
}) => {
  const [data, setData] = useState<TemperatureData | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const response = await fetch(`/api/v1/vehicles/${vehicleId}/temperature/history?hours=${hours}`);
      if (!response.ok) {
        throw new Error('Failed to fetch temperature data');
      }
      const result = await response.json();
      setData(result);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch temperature data:', error);
      toast.error('온도 데이터 조회에 실패했습니다');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    if (autoRefresh) {
      const interval = setInterval(fetchData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [vehicleId, hours, autoRefresh, refreshInterval]);

  if (loading) {
    return (
      <Card title="온도 이력">
        <div className="h-80 flex items-center justify-center">
          <div className="animate-pulse text-gray-400">데이터 로딩 중...</div>
        </div>
      </Card>
    );
  }

  if (!data || data.data_points.length === 0) {
    return (
      <Card title="온도 이력">
        <div className="h-80 flex flex-col items-center justify-center text-gray-400">
          <Thermometer size={48} className="mb-4" />
          <p>온도 데이터가 없습니다</p>
          <p className="text-sm mt-2">최근 {hours}시간 동안 기록된 데이터가 없습니다</p>
        </div>
      </Card>
    );
  }

  // 차트 데이터 준비
  const labels = data.data_points.map((point) => {
    const date = new Date(point.timestamp);
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
  });

  const temperatures = data.data_points.map((point) => point.temperature);

  // 현재 온도
  const currentTemp = temperatures[temperatures.length - 1] || 0;

  // 온도 상태 판단
  const getTempStatus = (temp: number) => {
    if (temp >= data.thresholds.critical) {
      return { status: '치명적', color: 'text-red-600', bgColor: 'bg-red-50', icon: AlertTriangle };
    } else if (temp >= data.thresholds.warning) {
      return { status: '경고', color: 'text-orange-600', bgColor: 'bg-orange-50', icon: AlertTriangle };
    } else if (temp <= data.thresholds.frozen_max && temp >= data.thresholds.frozen_min) {
      return { status: '냉동', color: 'text-blue-600', bgColor: 'bg-blue-50', icon: Snowflake };
    } else if (temp <= data.thresholds.refrigerated_max && temp >= data.thresholds.refrigerated_min) {
      return { status: '냉장', color: 'text-cyan-600', bgColor: 'bg-cyan-50', icon: Thermometer };
    }
    return { status: '정상', color: 'text-green-600', bgColor: 'bg-green-50', icon: Thermometer };
  };

  const tempStatus = getTempStatus(currentTemp);
  const StatusIcon = tempStatus.icon;

  // Chart.js 데이터 설정
  const chartData = {
    labels,
    datasets: [
      {
        label: '온도 (°C)',
        data: temperatures,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 2,
        pointHoverRadius: 5,
      },
    ],
  };

  // Chart.js 옵션
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            return `온도: ${context.parsed.y.toFixed(1)}°C`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        min: Math.min(...temperatures, data.vehicle_temp_range.min) - 5,
        max: Math.max(...temperatures, data.vehicle_temp_range.max) + 5,
        ticks: {
          callback: (value: any) => `${value}°C`,
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45,
        },
      },
    },
    annotation: {
      annotations: [
        // 차량 최소 온도 라인
        {
          type: 'line',
          yMin: data.vehicle_temp_range.min,
          yMax: data.vehicle_temp_range.min,
          borderColor: 'rgba(59, 130, 246, 0.5)',
          borderWidth: 2,
          borderDash: [5, 5],
          label: {
            content: `최소: ${data.vehicle_temp_range.min}°C`,
            enabled: true,
            position: 'end',
          },
        },
        // 차량 최대 온도 라인
        {
          type: 'line',
          yMin: data.vehicle_temp_range.max,
          yMax: data.vehicle_temp_range.max,
          borderColor: 'rgba(239, 68, 68, 0.5)',
          borderWidth: 2,
          borderDash: [5, 5],
          label: {
            content: `최대: ${data.vehicle_temp_range.max}°C`,
            enabled: true,
            position: 'end',
          },
        },
      ],
    },
  };

  // 통계 계산
  const minTemp = Math.min(...temperatures);
  const maxTemp = Math.max(...temperatures);
  const avgTemp = temperatures.reduce((a, b) => a + b, 0) / temperatures.length;

  return (
    <Card
      title={
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Thermometer size={20} />
            <span>온도 이력 (최근 {hours}시간)</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-gray-500">실시간 업데이트</span>
          </div>
        </div>
      }
    >
      <div className="space-y-4">
        {/* 현재 온도 및 상태 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className={`${tempStatus.bgColor} rounded-lg p-4`}>
            <div className="flex items-center gap-2 mb-2">
              <StatusIcon className={tempStatus.color} size={20} />
              <span className="text-sm text-gray-600">현재 온도</span>
            </div>
            <div className={`text-2xl font-bold ${tempStatus.color}`}>
              {currentTemp.toFixed(1)}°C
            </div>
            <div className={`text-xs ${tempStatus.color} mt-1`}>{tempStatus.status}</div>
          </div>

          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Snowflake className="text-blue-600" size={20} />
              <span className="text-sm text-gray-600">최저 온도</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">{minTemp.toFixed(1)}°C</div>
          </div>

          <div className="bg-red-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Thermometer className="text-red-600" size={20} />
              <span className="text-sm text-gray-600">최고 온도</span>
            </div>
            <div className="text-2xl font-bold text-red-600">{maxTemp.toFixed(1)}°C</div>
          </div>

          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Thermometer className="text-purple-600" size={20} />
              <span className="text-sm text-gray-600">평균 온도</span>
            </div>
            <div className="text-2xl font-bold text-purple-600">{avgTemp.toFixed(1)}°C</div>
          </div>
        </div>

        {/* 차트 */}
        <div className="h-80">
          <Line data={chartData} options={options} />
        </div>

        {/* 임계값 정보 */}
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span className="text-gray-600">
              냉동: {data.thresholds.frozen_min}°C ~ {data.thresholds.frozen_max}°C
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-cyan-500 rounded"></div>
            <span className="text-gray-600">
              냉장: {data.thresholds.refrigerated_min}°C ~ {data.thresholds.refrigerated_max}°C
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-orange-500 rounded"></div>
            <span className="text-gray-600">경고: {data.thresholds.warning}°C 이상</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span className="text-gray-600">치명적: {data.thresholds.critical}°C 이상</span>
          </div>
        </div>

        {/* 데이터 포인트 수 */}
        <div className="text-xs text-gray-500 text-right">
          총 {data.total_points}개 데이터 포인트 ({data.vehicle_plate})
        </div>
      </div>
    </Card>
  );
};

export default UvisTemperatureChart;

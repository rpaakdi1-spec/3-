/**
 * Phase 12: 배차 분석 대시보드
 * 통계, 성과, 패턴, 최적화 제안
 */
import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, Clock, AlertCircle, CheckCircle, Zap } from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import apiClient from '../api/client';

interface DispatchStatistics {
  total_dispatches: number;
  success_rate: number;
  avg_distance_km: number;
  avg_duration_min: number;
  by_status: { [key: string]: number };
  by_vehicle_type: { [key: string]: number };
  period: {
    start: string;
    end: string;
  };
}

interface DriverPerformance {
  driver_id: number;
  driver_name: string;
  total_dispatches: number;
  completed: number;
  completion_rate: number;
  avg_rating: number;
  total_distance_km: number;
}

interface Suggestion {
  type: 'warning' | 'info';
  title: string;
  description: string;
  action: string;
}

interface HourlyPattern {
  [hour: string]: number;
}

const DispatchAnalyticsDashboard: React.FC = () => {
  const [statistics, setStatistics] = useState<DispatchStatistics | null>(null);
  const [driverPerformance, setDriverPerformance] = useState<DriverPerformance[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [hourlyPattern, setHourlyPattern] = useState<HourlyPattern>({});
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('30'); // 기본 30일

  useEffect(() => {
    loadAnalytics();
  }, [dateRange]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      // 병렬로 모든 데이터 로드
      const [statsRes, driversRes, suggestionsRes, patternRes] = await Promise.all([
        apiClient.get('/dispatch/analytics/statistics'),
        apiClient.get('/dispatch/analytics/driver-performance'),
        apiClient.get('/dispatch/analytics/suggestions'),
        apiClient.get('/dispatch/analytics/hourly-pattern'),
      ]);

      setStatistics(statsRes.data);
      setDriverPerformance(driversRes.data.drivers || []);
      setSuggestions(suggestionsRes.data.suggestions || []);
      setHourlyPattern(patternRes.data.pattern || {});
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  // 차트 데이터 준비
  const statusChartData = statistics
    ? Object.entries(statistics.by_status).map(([status, count]) => ({
        name: status === 'completed' ? '완료' : status === 'assigned' ? '배정' : status === 'cancelled' ? '취소' : status,
        count,
      }))
    : [];

  const vehicleTypeChartData = statistics
    ? Object.entries(statistics.by_vehicle_type).map(([type, count]) => ({
        name: type,
        count,
      }))
    : [];

  const hourlyChartData = Object.entries(hourlyPattern).map(([hour, count]) => ({
    hour: `${hour}시`,
    count,
  }));

  const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">데이터 로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <BarChart3 className="w-7 h-7 text-blue-500" />
            배차 분석 대시보드
          </h1>
          <p className="text-gray-600 mt-1">배차 성과와 패턴을 분석합니다</p>
        </div>
        <div className="flex gap-2">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="7">최근 7일</option>
            <option value="30">최근 30일</option>
            <option value="90">최근 90일</option>
          </select>
        </div>
      </div>

      {/* 주요 지표 카드 */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">총 배차</span>
              <BarChart3 className="w-5 h-5 text-blue-500" />
            </div>
            <p className="text-3xl font-bold">{statistics.total_dispatches}</p>
            <p className="text-xs text-gray-500 mt-1">건</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">성공률</span>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <p className="text-3xl font-bold text-green-600">
              {statistics.success_rate.toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">완료율</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">평균 거리</span>
              <Zap className="w-5 h-5 text-amber-500" />
            </div>
            <p className="text-3xl font-bold text-amber-600">
              {statistics.avg_distance_km.toFixed(1)}
            </p>
            <p className="text-xs text-gray-500 mt-1">km</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">평균 시간</span>
              <Clock className="w-5 h-5 text-purple-500" />
            </div>
            <p className="text-3xl font-bold text-purple-600">
              {statistics.avg_duration_min.toFixed(0)}
            </p>
            <p className="text-xs text-gray-500 mt-1">분</p>
          </div>
        </div>
      )}

      {/* 최적화 제안 */}
      {suggestions.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-500" />
            AI 최적화 제안
          </h2>
          <div className="space-y-3">
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className={`flex items-start gap-3 p-4 rounded-lg border-l-4 ${
                  suggestion.type === 'warning'
                    ? 'bg-yellow-50 border-yellow-500'
                    : 'bg-blue-50 border-blue-500'
                }`}
              >
                {suggestion.type === 'warning' ? (
                  <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                ) : (
                  <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                )}
                <div className="flex-1">
                  <h3
                    className={`font-bold mb-1 ${
                      suggestion.type === 'warning' ? 'text-yellow-900' : 'text-blue-900'
                    }`}
                  >
                    {suggestion.title}
                  </h3>
                  <p
                    className={`text-sm mb-2 ${
                      suggestion.type === 'warning' ? 'text-yellow-700' : 'text-blue-700'
                    }`}
                  >
                    {suggestion.description}
                  </p>
                  <p
                    className={`text-xs font-medium ${
                      suggestion.type === 'warning' ? 'text-yellow-800' : 'text-blue-800'
                    }`}
                  >
                    💡 {suggestion.action}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 차트 그리드 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 상태별 배차 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-bold mb-4">상태별 배차</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, count }) => `${name}: ${count}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="count"
              >
                {statusChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* 차량 타입별 배차 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-bold mb-4">차량 타입별 배차</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={vehicleTypeChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 시간대별 배차 패턴 */}
        <div className="bg-white rounded-lg shadow-md p-6 lg:col-span-2">
          <h2 className="text-lg font-bold mb-4">시간대별 배차 패턴</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={hourlyChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#3b82f6"
                strokeWidth={2}
                name="배차 건수"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 기사 성과 테이블 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Users className="w-5 h-5 text-green-500" />
          기사별 성과 (상위 10명)
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  순위
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  기사명
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  총 배차
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  완료
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  완료율
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  평점
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  총 거리
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {driverPerformance.map((driver, index) => (
                <tr key={driver.driver_id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm">
                    <span
                      className={`inline-flex items-center justify-center w-6 h-6 rounded-full ${
                        index === 0
                          ? 'bg-yellow-100 text-yellow-800'
                          : index === 1
                          ? 'bg-gray-100 text-gray-800'
                          : index === 2
                          ? 'bg-orange-100 text-orange-800'
                          : 'bg-blue-50 text-blue-800'
                      } font-bold text-xs`}
                    >
                      {index + 1}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm font-medium">{driver.driver_name}</td>
                  <td className="px-4 py-3 text-sm text-center">
                    {driver.total_dispatches}
                  </td>
                  <td className="px-4 py-3 text-sm text-center text-green-600">
                    {driver.completed}
                  </td>
                  <td className="px-4 py-3 text-sm text-center">
                    <span
                      className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                        driver.completion_rate >= 95
                          ? 'bg-green-100 text-green-800'
                          : driver.completion_rate >= 90
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {driver.completion_rate.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-center">
                    <span className="text-yellow-500">
                      ⭐ {driver.avg_rating.toFixed(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-right text-gray-600">
                    {driver.total_distance_km.toFixed(1)} km
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DispatchAnalyticsDashboard;

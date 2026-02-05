import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Calendar,
  Users,
  DollarSign,
  Package,
  Clock,
  Truck,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Download
} from 'lucide-react';
import axios from 'axios';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface KPI {
  name: string;
  value: number;
  unit: string;
  target: number;
  status: string;
  change: number;
  trend: string;
}

interface TrendData {
  labels: string[];
  values: number[];
  period_type: string;
}

interface TopClient {
  client_id: number;
  client_name: string;
  order_count: number;
  total_revenue: number;
  percentage: number;
}

interface HourlyDistribution {
  hour: number;
  count: number;
}

interface DashboardData {
  kpis: KPI[];
  revenue_trend: TrendData;
  order_trend: TrendData;
  top_clients: TopClient[];
  hourly_distribution: HourlyDistribution[];
}

const AnalyticsDashboardPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<DashboardData | null>(null);
  const [period, setPeriod] = useState('last_7_days');

  useEffect(() => {
    loadDashboard();
  }, [period]);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const res = await axios.get(`${API_URL}/api/v1/analytics/dashboard`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { period }
      });
      setData(res.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good': return 'bg-green-100 text-green-800 border-green-300';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getKPIIcon = (name: string) => {
    if (name.includes('주문') || name.includes('처리율')) return <Package className="w-6 h-6" />;
    if (name.includes('배송')) return <CheckCircle className="w-6 h-6" />;
    if (name.includes('차량')) return <Truck className="w-6 h-6" />;
    if (name.includes('시간')) return <Clock className="w-6 h-6" />;
    if (name.includes('매출') || name.includes('금액')) return <DollarSign className="w-6 h-6" />;
    return <BarChart3 className="w-6 h-6" />;
  };

  const formatValue = (value: number, unit: string) => {
    if (unit === 'M원') {
      return `₩${value.toFixed(1)}M`;
    } else if (unit === '천원') {
      return `₩${value.toFixed(0)}K`;
    } else if (unit === '%') {
      return `${value.toFixed(1)}%`;
    } else if (unit === '시간') {
      return `${value.toFixed(1)}h`;
    } else if (unit === '건') {
      return `${value.toFixed(0)}건`;
    }
    return `${value} ${unit}`;
  };

  const formatRevenueTrend = (trend: TrendData) => {
    return trend.labels.map((label, index) => ({
      name: label,
      매출: trend.values[index]
    }));
  };

  const formatOrderTrend = (trend: TrendData) => {
    return trend.labels.map((label, index) => ({
      name: label,
      주문: trend.values[index]
    }));
  };

  const formatHourlyData = (distribution: HourlyDistribution[]) => {
    return distribution.map(item => ({
      시간대: `${item.hour}시`,
      주문수: item.count
    }));
  };

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <BarChart3 className="w-8 h-8 text-blue-600" />
                고급 분석 & BI 대시보드
              </h1>
              <p className="text-gray-600 mt-1">실시간 KPI 모니터링 및 트렌드 분석</p>
            </div>
            <div className="flex gap-3">
              {/* 기간 선택 */}
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="today">오늘</option>
                <option value="yesterday">어제</option>
                <option value="last_7_days">최근 7일</option>
                <option value="last_30_days">최근 30일</option>
                <option value="this_week">이번 주</option>
                <option value="this_month">이번 달</option>
                <option value="last_month">지난 달</option>
              </select>
              <button
                onClick={loadDashboard}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                새로고침
              </button>
            </div>
          </div>
        </div>

        {loading && !data ? (
          <div className="text-center py-12">
            <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">데이터 로딩 중...</p>
          </div>
        ) : data ? (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {data.kpis.map((kpi, index) => (
                <div key={index} className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-600 mb-1">{kpi.name}</p>
                      <p className="text-3xl font-bold text-gray-900">{formatValue(kpi.value, kpi.unit)}</p>
                    </div>
                    <div className={`p-3 rounded-lg ${
                      kpi.status === 'good' ? 'bg-green-100' :
                      kpi.status === 'warning' ? 'bg-yellow-100' : 'bg-red-100'
                    }`}>
                      {getKPIIcon(kpi.name)}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      {kpi.trend === 'up' ? (
                        <TrendingUp className={`w-4 h-4 ${
                          kpi.name.includes('시간') ? 'text-red-600' : 'text-green-600'
                        }`} />
                      ) : kpi.trend === 'down' ? (
                        <TrendingDown className={`w-4 h-4 ${
                          kpi.name.includes('시간') ? 'text-green-600' : 'text-red-600'
                        }`} />
                      ) : null}
                      <span className={`text-sm font-medium ${
                        Math.abs(kpi.change) < 0.1 ? 'text-gray-600' :
                        (kpi.trend === 'up' && !kpi.name.includes('시간')) || (kpi.trend === 'down' && kpi.name.includes('시간'))
                          ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {kpi.change > 0 ? '+' : ''}{kpi.change.toFixed(1)}{kpi.unit === '%' ? 'p' : kpi.unit === '건' ? '건' : '%'}
                      </span>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full border ${getStatusColor(kpi.status)}`}>
                      목표: {formatValue(kpi.target, kpi.unit)}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* 매출 트렌드 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-green-600" />
                  매출 트렌드 (최근 30일)
                </h2>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={formatRevenueTrend(data.revenue_trend)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value) => `₩${value}M`} />
                    <Legend />
                    <Line type="monotone" dataKey="매출" stroke="#10b981" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* 주문 트렌드 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Package className="w-5 h-5 text-blue-600" />
                  주문 트렌드 (최근 30일)
                </h2>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={formatOrderTrend(data.order_trend)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}건`} />
                    <Legend />
                    <Line type="monotone" dataKey="주문" stroke="#3b82f6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* 상위 고객 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5 text-purple-600" />
                  상위 고객 Top 10
                </h2>
                <div className="space-y-3 max-h-[250px] overflow-y-auto">
                  {data.top_clients.slice(0, 10).map((client, index) => (
                    <div key={client.client_id} className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-bold text-blue-600">{index + 1}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{client.client_name}</p>
                        <p className="text-xs text-gray-500">{client.order_count}건 • ₩{(client.total_revenue / 1000000).toFixed(1)}M</p>
                      </div>
                      <div className="flex-shrink-0">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${Math.min(100, (client.order_count / data.top_clients[0].order_count) * 100)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 시간대별 주문 분포 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-orange-600" />
                  시간대별 주문 분포
                </h2>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={formatHourlyData(data.hourly_distribution)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="시간대" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}건`} />
                    <Bar dataKey="주문수" fill="#f59e0b" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 상세 통계 테이블 */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">KPI 상세 정보</h2>
                <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2">
                  <Download className="w-4 h-4" />
                  Excel 다운로드
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        지표
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        현재값
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        목표
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        달성률
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        변화
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        상태
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {data.kpis.map((kpi, index) => {
                      const achievement = kpi.name.includes('시간')
                        ? (kpi.target / kpi.value) * 100
                        : (kpi.value / kpi.target) * 100;
                      
                      return (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {kpi.name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatValue(kpi.value, kpi.unit)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                            {formatValue(kpi.target, kpi.unit)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span className={`font-medium ${
                              achievement >= 100 ? 'text-green-600' :
                              achievement >= 90 ? 'text-yellow-600' : 'text-red-600'
                            }`}>
                              {achievement.toFixed(0)}%
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <span className={`flex items-center gap-1 ${
                              Math.abs(kpi.change) < 0.1 ? 'text-gray-600' :
                              (kpi.trend === 'up' && !kpi.name.includes('시간')) || (kpi.trend === 'down' && kpi.name.includes('시간'))
                                ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {kpi.trend === 'up' ? <TrendingUp className="w-4 h-4" /> :
                               kpi.trend === 'down' ? <TrendingDown className="w-4 h-4" /> : null}
                              {kpi.change > 0 ? '+' : ''}{kpi.change.toFixed(1)}{kpi.unit === '%' ? 'p' : '%'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              kpi.status === 'good' ? 'bg-green-100 text-green-800' :
                              kpi.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {kpi.status === 'good' ? '양호' : kpi.status === 'warning' ? '주의' : '경고'}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-12">
            <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">데이터 없음</h3>
            <p className="text-gray-500">기간을 선택하고 새로고침 버튼을 클릭하세요</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsDashboardPage;

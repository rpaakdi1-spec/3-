import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Minus,
  Calendar,
  RefreshCw,
  Download,
  Filter,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Users,
  Package,
  Truck,
  DollarSign,
  Clock,
  Target
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

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

interface KPI {
  name: string;
  value: number;
  unit: string;
  target: number;
  status: 'good' | 'warning' | 'critical';
  change: number;
  trend: 'up' | 'down' | 'stable';
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
  const [activeTab, setActiveTab] = useState<'overview' | 'trends' | 'clients'>('overview');

  useEffect(() => {
    loadDashboard();
  }, [period]);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const res = await axios.get(`${API_URL}/analytics/dashboard`, {
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'good':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good':
        return 'bg-green-50 border-green-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'critical':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getTrendIcon = (trend: string, change: number) => {
    if (trend === 'up') {
      return <TrendingUp className={`w-4 h-4 ${change > 0 ? 'text-green-600' : 'text-red-600'}`} />;
    } else if (trend === 'down') {
      return <TrendingDown className={`w-4 h-4 ${change < 0 ? 'text-red-600' : 'text-green-600'}`} />;
    } else {
      return <Minus className="w-4 h-4 text-gray-600" />;
    }
  };

  const getKPIIcon = (name: string) => {
    if (name.includes('주문')) return <Package className="w-6 h-6" />;
    if (name.includes('배송')) return <Truck className="w-6 h-6" />;
    if (name.includes('차량')) return <Truck className="w-6 h-6" />;
    if (name.includes('시간')) return <Clock className="w-6 h-6" />;
    if (name.includes('매출') || name.includes('금액')) return <DollarSign className="w-6 h-6" />;
    return <Target className="w-6 h-6" />;
  };

  const formatChartData = (trend: TrendData) => {
    return trend.labels.map((label, index) => ({
      name: label,
      value: trend.values[index]
    }));
  };

  const formatHourlyData = (distribution: HourlyDistribution[]) => {
    return distribution.map(item => ({
      name: `${item.hour}시`,
      count: item.count
    }));
  };

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

  return (<div className="min-h-screen bg-gray-50 p-6">
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
            
            <div className="flex gap-3 items-center">
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
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:bg-gray-400"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                새로고침
              </button>
            </div>
          </div>
        </div>

        {loading && !data ? (
          <div className="text-center py-12">
            <RefreshCw className="w-12 h-12 text-gray-400 animate-spin mx-auto mb-4" />
            <p className="text-gray-500">데이터 로딩 중...</p>
          </div>
        ) : data ? (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {data.kpis.map((kpi, index) => (
                <div
                  key={index}
                  className={`border rounded-lg p-6 transition-all hover:shadow-lg ${getStatusColor(kpi.status)}`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="text-gray-700">
                      {getKPIIcon(kpi.name)}
                    </div>
                    {getStatusIcon(kpi.status)}
                  </div>
                  
                  <h3 className="text-sm font-medium text-gray-600 mb-2">{kpi.name}</h3>
                  
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="text-3xl font-bold text-gray-900">
                      {kpi.value.toLocaleString()}
                    </span>
                    <span className="text-sm text-gray-600">{kpi.unit}</span>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-1">
                      {getTrendIcon(kpi.trend, kpi.change)}
                      <span className={kpi.change >= 0 ? 'text-green-600' : 'text-red-600'}>
                        {kpi.change > 0 ? '+' : ''}{kpi.change.toFixed(1)}%
                      </span>
                    </div>
                    <span className="text-gray-500">
                      목표: {kpi.target}{kpi.unit}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Tabs */}
            <div className="bg-white rounded-lg shadow mb-6">
              <div className="border-b border-gray-200">
                <div className="flex gap-4 px-6">
                  <button
                    onClick={() => setActiveTab('overview')}
                    className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === 'overview'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <BarChart3 className="w-4 h-4 inline mr-2" />
                    개요
                  </button>
                  <button
                    onClick={() => setActiveTab('trends')}
                    className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === 'trends'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <TrendingUp className="w-4 h-4 inline mr-2" />
                    트렌드
                  </button>
                  <button
                    onClick={() => setActiveTab('clients')}
                    className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === 'clients'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <Users className="w-4 h-4 inline mr-2" />
                    고객 분석
                  </button>
                </div>
              </div>

              <div className="p-6">
                {/* 개요 탭 */}
                {activeTab === 'overview' && (
                  <div className="space-y-6">
                    {/* 매출 & 주문 트렌드 */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">매출 추이 (최근 30일)</h3>
                        <ResponsiveContainer width="100%" height={250}>
                          <LineChart data={formatChartData(data.revenue_trend)}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip formatter={(value: any) => `${value.toFixed(1)}M원`} />
                            <Line 
                              type="monotone" 
                              dataKey="value" 
                              stroke="#3b82f6" 
                              strokeWidth={2}
                              dot={{ fill: '#3b82f6', r: 4 }}
                              activeDot={{ r: 6 }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>

                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">주문 추이 (최근 30일)</h3>
                        <ResponsiveContainer width="100%" height={250}>
                          <LineChart data={formatChartData(data.order_trend)}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip formatter={(value: any) => `${value}건`} />
                            <Line 
                              type="monotone" 
                              dataKey="value" 
                              stroke="#10b981" 
                              strokeWidth={2}
                              dot={{ fill: '#10b981', r: 4 }}
                              activeDot={{ r: 6 }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* 시간대별 주문 분포 */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">시간대별 주문 분포</h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={formatHourlyData(data.hourly_distribution)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="count" fill="#8b5cf6" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}

                {/* 트렌드 탭 */}
                {activeTab === 'trends' && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {/* 매출 상세 */}
                      <div className="border rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">매출 분석</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={formatChartData(data.revenue_trend)}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip formatter={(value: any) => `${value.toFixed(1)}M원`} />
                            <Bar dataKey="value" fill="#3b82f6" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>

                      {/* 주문 상세 */}
                      <div className="border rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">주문량 분석</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={formatChartData(data.order_trend)}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip formatter={(value: any) => `${value}건`} />
                            <Bar dataKey="value" fill="#10b981" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* 트렌드 인사이트 */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-blue-900 mb-3">📊 트렌드 인사이트</h3>
                      <ul className="space-y-2 text-blue-800">
                        <li>• 최근 7일간 매출이 평균 대비 {data.kpis.find(k => k.name.includes('매출'))?.change.toFixed(1)}% 증가했습니다</li>
                        <li>• 주문량이 전 기간 대비 {data.kpis.find(k => k.name.includes('주문'))?.change.toFixed(0)}건 증가했습니다</li>
                        <li>• 차량 가동률이 목표치를 {data.kpis.find(k => k.name.includes('가동률'))?.status === 'good' ? '달성' : '미달성'}했습니다</li>
                      </ul>
                    </div>
                  </div>
                )}

                {/* 고객 분석 탭 */}
                {activeTab === 'clients' && (
                  <div className="space-y-6">
                    {/* 상위 고객 */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">상위 고객 Top 10</h3>
                      <div className="space-y-2">
                        {data.top_clients.map((client, index) => (
                          <div
                            key={client.client_id}
                            className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                          >
                            <div className="flex items-center gap-4">
                              <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold">
                                {index + 1}
                              </div>
                              <div>
                                <h4 className="font-semibold text-gray-900">{client.client_name}</h4>
                                <p className="text-sm text-gray-600">{client.order_count}건 주문</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-gray-900">
                                ₩{(client.total_revenue / 1000000).toFixed(1)}M
                              </p>
                              <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                                <div
                                  className="bg-blue-600 h-2 rounded-full"
                                  style={{ width: `${Math.min(client.order_count / Math.max(...data.top_clients.map(c => c.order_count)) * 100, 100)}%` }}
                                ></div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* 고객 분포 파이 차트 */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">고객별 매출 비중</h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={data.top_clients.slice(0, 8).map(c => ({
                              name: c.client_name,
                              value: c.total_revenue
                            }))}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {data.top_clients.slice(0, 8).map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value: any) => `₩${(value / 1000000).toFixed(1)}M`} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <BarChart3 className="w-20 h-20 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">데이터 없음</h3>
            <p className="text-gray-600 mb-4">
              선택한 기간에 대한 데이터가 없습니다
            </p>
            <button
              onClick={loadDashboard}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              다시 시도
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsDashboardPage;

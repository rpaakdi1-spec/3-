import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import {
  Truck,
  MapPin,
  Clock,
  Package,
  TrendingDown,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  PlayCircle,
  Settings,
  RefreshCw,
  BarChart3,
  Calendar,
  Users,
  DollarSign
} from 'lucide-react';
import axios from 'axios';
import {
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

interface OptimizationConstraints {
  max_vehicles: number;
  max_route_time: number;
  priority_orders: number[];
  excluded_vehicles: number[];
}

interface OptimizationOptions {
  use_traffic_data: boolean;
  optimize_fuel: boolean;
  balance_workload: boolean;
}

interface RouteSequencePoint {
  type: string;
  order_id?: number;
  location: {
    latitude: number;
    longitude: number;
    address?: string;
  };
  arrival_time: string;
  service_time?: number;
  departure_time: string;
  load_weight?: number;
  load_pallets?: number;
}

interface Route {
  route_id: number;
  vehicle_id: number;
  driver_id: number;
  orders: number[];
  sequence: RouteSequencePoint[];
  total_distance: number;
  total_time: number;
  total_load_weight: number;
  total_load_pallets: number;
  estimated_cost: number;
}

interface OptimizationSummary {
  total_vehicles: number;
  total_orders: number;
  unassigned_orders: number;
  total_distance: number;
  total_time: number;
  empty_distance: number;
  estimated_cost: number;
  optimization_time: number;
  improvement_vs_manual: {
    distance: number;
    time: number;
    cost: number;
  };
}

interface OptimizationResult {
  optimization_id: string;
  status: string;
  summary: OptimizationSummary;
  routes: Route[];
  unassigned_orders: number[];
  created_at: string;
}

const DispatchOptimizationPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);
  const [activeTab, setActiveTab] = useState<'routes' | 'map' | 'performance'>('routes');
  
  // 제약 조건
  const [constraints, setConstraints] = useState<OptimizationConstraints>({
    max_vehicles: 10,
    max_route_time: 480,
    priority_orders: [],
    excluded_vehicles: []
  });
  
  // 옵션
  const [options, setOptions] = useState<OptimizationOptions>({
    use_traffic_data: true,
    optimize_fuel: true,
    balance_workload: true
  });
  
  // 선택된 주문
  const [selectedOrders, setSelectedOrders] = useState<number[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  // 대기 중인 주문 로드
  useEffect(() => {
    loadPendingOrders();
  }, [selectedDate]);

  const loadPendingOrders = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await axios.get(`${API_URL}/orders`, {
        headers: { Authorization: `Bearer ${token}` },
        params: {
          status: 'CONFIRMED',
          limit: 100
        }
      });
      
      // 주문 ID 자동 선택
      const orderIds = res.data.orders?.map((o: any) => o.id) || [];
      setSelectedOrders(orderIds);
    } catch (error) {
      console.error('Failed to load orders:', error);
    }
  };

  const runOptimization = async () => {
    if (selectedOrders.length === 0) {
      alert('배차할 주문을 선택해주세요');
      return;
    }

    setOptimizing(true);
    try {
      const token = localStorage.getItem('access_token');
      const res = await axios.post(
        `${API_URL}/dispatch-optimization/optimize`,
        {
          order_ids: selectedOrders,
          date: selectedDate,
          constraints,
          options
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setResult(res.data);
      setActiveTab('routes');
    } catch (error: any) {
      console.error('Optimization failed:', error);
      alert(error.response?.data?.detail || '최적화 실패');
    } finally {
      setOptimizing(false);
    }
  };

  const approveOptimization = async () => {
    if (!result) return;
    
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_URL}/dispatch-optimization/${result.optimization_id}/approve`,
        {
          approved_by: 1, // TODO: 실제 사용자 ID
          notes: '승인함'
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      alert('배차가 승인되었습니다!');
    } catch (error) {
      console.error('Approval failed:', error);
      alert('승인 실패');
    }
  };

  const formatCurrency = (value: number) => {
    return `₩${value.toLocaleString()}`;
  };

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}시간 ${mins}분`;
  };

  // 성과 비교 차트 데이터
  const getComparisonChartData = () => {
    if (!result) return [];
    
    const manual = {
      distance: result.summary.total_distance / (1 + result.summary.improvement_vs_manual.distance / 100),
      time: result.summary.total_time / (1 + result.summary.improvement_vs_manual.time / 100),
      cost: result.summary.estimated_cost / (1 + result.summary.improvement_vs_manual.cost / result.summary.estimated_cost)
    };
    
    return [
      {
        name: '수동 배차',
        거리: Math.round(manual.distance),
        시간: Math.round(manual.time),
        비용: Math.round(manual.cost / 1000)
      },
      {
        name: 'AI 최적화',
        거리: Math.round(result.summary.total_distance),
        시간: result.summary.total_time,
        비용: Math.round(result.summary.estimated_cost / 1000)
      }
    ];
  };

  // 차량 사용률 파이 차트 데이터
  const getVehicleUtilizationData = () => {
    if (!result) return [];
    
    return [
      { name: '사용', value: result.summary.total_vehicles, color: '#10b981' },
      { name: '미사용', value: constraints.max_vehicles - result.summary.total_vehicles, color: '#e5e7eb' }
    ];
  };

  return (
    <Layout>
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Truck className="w-8 h-8 text-blue-600" />
            자동 배차 최적화
          </h1>
          <p className="text-gray-600 mt-1">AI 기반 다중 차량 경로 최적화 시스템</p>
        </div>

        {/* 제약 조건 설정 */}
        <div className="bg-white rounded-lg shadow mb-6 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Settings className="w-5 h-5 text-blue-600" />
              최적화 설정
            </h2>
            <button
              onClick={runOptimization}
              disabled={optimizing || selectedOrders.length === 0}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:bg-gray-400"
            >
              {optimizing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  최적화 중...
                </>
              ) : (
                <>
                  <PlayCircle className="w-4 h-4" />
                  최적화 실행
                </>
              )}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* 날짜 선택 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-1" />
                배차 날짜
              </label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* 최대 차량 수 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Truck className="w-4 h-4 inline mr-1" />
                최대 차량 수
              </label>
              <input
                type="number"
                value={constraints.max_vehicles}
                onChange={(e) => setConstraints({ ...constraints, max_vehicles: parseInt(e.target.value) })}
                min="1"
                max="20"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* 최대 경로 시간 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Clock className="w-4 h-4 inline mr-1" />
                최대 경로 시간 (분)
              </label>
              <input
                type="number"
                value={constraints.max_route_time}
                onChange={(e) => setConstraints({ ...constraints, max_route_time: parseInt(e.target.value) })}
                min="60"
                max="600"
                step="30"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* 주문 수 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Package className="w-4 h-4 inline mr-1" />
                선택된 주문
              </label>
              <div className="px-3 py-2 border border-gray-300 rounded-lg bg-gray-50">
                <span className="text-lg font-bold text-gray-900">{selectedOrders.length}건</span>
              </div>
            </div>
          </div>

          {/* 옵션 체크박스 */}
          <div className="mt-4 flex flex-wrap gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={options.use_traffic_data}
                onChange={(e) => setOptions({ ...options, use_traffic_data: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">실시간 교통 정보 사용</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={options.optimize_fuel}
                onChange={(e) => setOptions({ ...options, optimize_fuel: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">연료 최적화</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={options.balance_workload}
                onChange={(e) => setOptions({ ...options, balance_workload: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">업무량 균등 배분</span>
            </label>
          </div>
        </div>

        {/* 최적화 결과 */}
        {result && (
          <>
            {/* 요약 카드 */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">사용 차량</span>
                  <Truck className="w-5 h-5 text-blue-500" />
                </div>
                <p className="text-2xl font-bold text-gray-900">{result.summary.total_vehicles}대</p>
                <p className="text-xs text-green-600 mt-1">
                  {constraints.max_vehicles - result.summary.total_vehicles}대 절감
                </p>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">배정 주문</span>
                  <Package className="w-5 h-5 text-green-500" />
                </div>
                <p className="text-2xl font-bold text-gray-900">{result.summary.total_orders}건</p>
                {result.summary.unassigned_orders > 0 && (
                  <p className="text-xs text-red-600 mt-1">
                    {result.summary.unassigned_orders}건 미배정
                  </p>
                )}
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">총 거리</span>
                  <MapPin className="w-5 h-5 text-purple-500" />
                </div>
                <p className="text-2xl font-bold text-gray-900">{result.summary.total_distance.toFixed(1)}km</p>
                <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                  <TrendingDown className="w-3 h-3" />
                  {Math.abs(result.summary.improvement_vs_manual.distance).toFixed(1)}% 단축
                </p>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">총 시간</span>
                  <Clock className="w-5 h-5 text-orange-500" />
                </div>
                <p className="text-2xl font-bold text-gray-900">{formatTime(result.summary.total_time)}</p>
                <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                  <TrendingDown className="w-3 h-3" />
                  {Math.abs(result.summary.improvement_vs_manual.time).toFixed(1)}% 단축
                </p>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">예상 비용</span>
                  <DollarSign className="w-5 h-5 text-red-500" />
                </div>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(result.summary.estimated_cost)}</p>
                <p className="text-xs text-green-600 mt-1">
                  {formatCurrency(Math.abs(result.summary.improvement_vs_manual.cost))} 절감
                </p>
              </div>
            </div>

            {/* 탭 네비게이션 */}
            <div className="bg-white rounded-lg shadow mb-6">
              <div className="border-b border-gray-200">
                <div className="flex gap-4 px-6">
                  <button
                    onClick={() => setActiveTab('routes')}
                    className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === 'routes'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <Truck className="w-4 h-4 inline mr-2" />
                    경로 목록
                  </button>
                  <button
                    onClick={() => setActiveTab('map')}
                    className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === 'map'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <MapPin className="w-4 h-4 inline mr-2" />
                    지도 시각화
                  </button>
                  <button
                    onClick={() => setActiveTab('performance')}
                    className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === 'performance'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <BarChart3 className="w-4 h-4 inline mr-2" />
                    성과 비교
                  </button>
                </div>
              </div>

              <div className="p-6">
                {/* 경로 목록 탭 */}
                {activeTab === 'routes' && (
                  <div className="space-y-4">
                    {result.routes.map((route) => (
                      <div
                        key={route.route_id}
                        onClick={() => setSelectedRoute(route)}
                        className={`border rounded-lg p-4 cursor-pointer transition-all ${
                          selectedRoute?.route_id === route.route_id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                              경로 #{route.route_id}
                              <span className="text-sm font-normal text-gray-600">
                                차량 #{route.vehicle_id} | 운전자 #{route.driver_id}
                              </span>
                            </h3>
                            
                            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-3">
                              <div className="bg-white p-2 rounded border border-gray-200">
                                <span className="text-xs text-gray-500">배송 건수</span>
                                <p className="font-bold text-gray-900">{route.orders.length}건</p>
                              </div>
                              <div className="bg-white p-2 rounded border border-gray-200">
                                <span className="text-xs text-gray-500">거리</span>
                                <p className="font-bold text-gray-900">{route.total_distance.toFixed(1)}km</p>
                              </div>
                              <div className="bg-white p-2 rounded border border-gray-200">
                                <span className="text-xs text-gray-500">시간</span>
                                <p className="font-bold text-gray-900">{formatTime(route.total_time)}</p>
                              </div>
                              <div className="bg-white p-2 rounded border border-gray-200">
                                <span className="text-xs text-gray-500">적재량</span>
                                <p className="font-bold text-gray-900">{route.total_load_weight.toFixed(1)}톤</p>
                              </div>
                              <div className="bg-white p-2 rounded border border-gray-200">
                                <span className="text-xs text-gray-500">비용</span>
                                <p className="font-bold text-gray-900">{formatCurrency(route.estimated_cost)}</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* 지도 시각화 탭 */}
                {activeTab === 'map' && (
                  <div className="bg-gray-100 rounded-lg p-8 text-center">
                    <MapPin className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">지도 시각화</h3>
                    <p className="text-gray-600">
                      각 경로를 지도에 표시합니다
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      Leaflet 또는 Google Maps API 연동으로 구현 예정
                    </p>
                  </div>
                )}

                {/* 성과 비교 탭 */}
                {activeTab === 'performance' && (
                  <div className="space-y-6">
                    {/* 비교 차트 */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">수동 배차 vs AI 최적화</h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={getComparisonChartData()}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Bar dataKey="거리" fill="#8b5cf6" name="거리 (km)" />
                          <Bar dataKey="시간" fill="#10b981" name="시간 (분)" />
                          <Bar dataKey="비용" fill="#f59e0b" name="비용 (천원)" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    {/* 차량 사용률 */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">차량 사용률</h3>
                        <ResponsiveContainer width="100%" height={250}>
                          <PieChart>
                            <Pie
                              data={getVehicleUtilizationData()}
                              cx="50%"
                              cy="50%"
                              labelLine={false}
                              label={({ name, value }) => `${name}: ${value}대`}
                              outerRadius={80}
                              fill="#8884d8"
                              dataKey="value"
                            >
                              {getVehicleUtilizationData().map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                              ))}
                            </Pie>
                            <Tooltip />
                          </PieChart>
                        </ResponsiveContainer>
                      </div>

                      {/* 개선 지표 */}
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">개선 지표</h3>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                            <span className="text-gray-700">거리 단축</span>
                            <span className="font-bold text-green-600 flex items-center gap-1">
                              <TrendingDown className="w-4 h-4" />
                              {Math.abs(result.summary.improvement_vs_manual.distance).toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                            <span className="text-gray-700">시간 단축</span>
                            <span className="font-bold text-green-600 flex items-center gap-1">
                              <TrendingDown className="w-4 h-4" />
                              {Math.abs(result.summary.improvement_vs_manual.time).toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                            <span className="text-gray-700">비용 절감</span>
                            <span className="font-bold text-green-600">
                              {formatCurrency(Math.abs(result.summary.improvement_vs_manual.cost))}
                            </span>
                          </div>
                          <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                            <span className="text-gray-700">최적화 시간</span>
                            <span className="font-bold text-blue-600">
                              {result.summary.optimization_time.toFixed(1)}초
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* 액션 버튼 */}
            <div className="flex justify-end gap-4">
              <button
                onClick={() => setResult(null)}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                초기화
              </button>
              <button
                onClick={approveOptimization}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
              >
                <CheckCircle className="w-4 h-4" />
                배차 승인
              </button>
            </div>
          </>
        )}

        {/* 최적화 전 안내 */}
        {!result && !optimizing && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Truck className="w-20 h-20 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">배차 최적화 준비 완료</h3>
            <p className="text-gray-600 mb-4">
              설정을 확인하고 '최적화 실행' 버튼을 클릭하세요
            </p>
            <div className="text-sm text-gray-500">
              <p>✓ {selectedOrders.length}개 주문 대기 중</p>
              <p>✓ 최대 {constraints.max_vehicles}대 차량 사용 가능</p>
              <p>✓ 경로당 최대 {formatTime(constraints.max_route_time)}</p>
            </div>
          </div>
        )}

        {/* 선택된 경로 상세 모달 */}
        {selectedRoute && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">
                  경로 #{selectedRoute.route_id} 상세
                </h2>
                <button
                  onClick={() => setSelectedRoute(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>

              <div className="p-6">
                {/* 경로 요약 */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <span className="text-sm text-gray-600">차량</span>
                    <p className="font-bold text-gray-900">#{selectedRoute.vehicle_id}</p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <span className="text-sm text-gray-600">운전자</span>
                    <p className="font-bold text-gray-900">#{selectedRoute.driver_id}</p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <span className="text-sm text-gray-600">배송</span>
                    <p className="font-bold text-gray-900">{selectedRoute.orders.length}건</p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <span className="text-sm text-gray-600">거리</span>
                    <p className="font-bold text-gray-900">{selectedRoute.total_distance.toFixed(1)}km</p>
                  </div>
                </div>

                {/* 배송 순서 */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">배송 순서</h3>
                  <div className="space-y-2">
                    {selectedRoute.sequence.map((point, idx) => (
                      <div
                        key={idx}
                        className={`p-3 rounded-lg border ${
                          point.type === 'depot'
                            ? 'bg-blue-50 border-blue-200'
                            : 'bg-white border-gray-200'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                            {idx + 1}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <h4 className="font-semibold text-gray-900">
                                {point.type === 'depot' ? '창고 출발/도착' : `배송 - 주문 #${point.order_id}`}
                              </h4>
                              <span className="text-sm text-gray-600">{point.arrival_time}</span>
                            </div>
                            <p className="text-sm text-gray-600 mt-1">
                              {point.location.address || `${point.location.latitude.toFixed(4)}, ${point.location.longitude.toFixed(4)}`}
                            </p>
                            {point.type === 'delivery' && (
                              <div className="flex gap-4 mt-2 text-xs text-gray-600">
                                <span>서비스: {point.service_time}분</span>
                                <span>출발: {point.departure_time}</span>
                                <span>적재: {point.load_weight?.toFixed(1)}톤</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
    </Layout>
  );
};

export default DispatchOptimizationPage;

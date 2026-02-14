/**
 * 실시간 배차 모니터링 대시보드
 * AI Agent 성능 추적 및 최적화 효과 시각화
 */
import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import {
  Activity,
  Truck,
  Package,
  TrendingUp,
  TrendingDown,
  Zap,
  CheckCircle,
  Clock,
  DollarSign,
  MapPin
} from 'lucide-react';
import {
  AreaChart,
  Area,
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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import apiClient from '../api/client';

interface LiveStats {
  date: string;
  timestamp: string;
  dispatch: {
    total: number;
    in_progress: number;
    completed: number;
    draft: number;
    avg_empty_distance_km: number;
    total_distance_km: number;
  };
  vehicle: {
    total: number;
    available: number;
    in_use: number;
    maintenance: number;
    utilization_rate: number;
  };
  order: {
    total: number;
    pending: number;
    assigned: number;
    in_transit: number;
    delivered: number;
    completion_rate: number;
  };
  ai_optimization: {
    enabled_dispatches: number;
    estimated_savings_km: number;
    estimated_savings_cost: number;
    avg_optimization_score: number;
  };
}

interface AgentPerformance {
  agent_name: string;
  correlation: number;
  sample_count: number;
  recommendation: string;
}

const DispatchMonitoringDashboard: React.FC = () => {
  const [liveStats, setLiveStats] = useState<LiveStats | null>(null);
  const [agentPerformance, setAgentPerformance] = useState<Record<string, AgentPerformance>>({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedDateRange, setSelectedDateRange] = useState<string>('today');

  // 실시간 통계 조회
  const fetchLiveStats = async () => {
    try {
      const response = await apiClient.get('/dispatch/monitoring/live-stats');
      if (response && response.data) {
        setLiveStats(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch live stats:', error);
    }
  };

  // Agent 성능 분석
  const fetchAgentPerformance = async () => {
    try {
      const response = await apiClient.get('/dispatch/monitoring/agent-performance', {
        params: { days: 30 }
      });
      if (response && response.data && response.data.agent_performance) {
        setAgentPerformance(response.data.agent_performance);
      }
    } catch (error) {
      console.error('Failed to fetch agent performance:', error);
    }
  };

  // 수동 새로고침
  const handleManualRefresh = async () => {
    setRefreshing(true);
    try {
      await Promise.all([
        fetchLiveStats(),
        fetchAgentPerformance()
      ]);
    } catch (error) {
      console.error('Manual refresh failed:', error);
    } finally {
      setTimeout(() => setRefreshing(false), 500);
    }
  };

  useEffect(() => {
    fetchLiveStats();
    fetchAgentPerformance();
    setLoading(false);

    // 자동 새로고침 (5초마다)
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchLiveStats();
      }, 5000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  if (loading || !liveStats) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <Activity className="w-12 h-12 text-blue-500 animate-pulse mx-auto mb-4" />
            <p className="text-gray-600">실시간 데이터 로딩 중...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-6 space-y-6 bg-gray-50">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Activity className="w-8 h-8 text-blue-600" />
            실시간 배차 모니터링
          </h1>
          <p className="text-gray-500 mt-1">
            마지막 업데이트: {new Date(liveStats.timestamp).toLocaleTimeString('ko-KR')}
          </p>
        </div>
        <div className="flex gap-2 items-center">
          {/* 날짜 범위 선택 */}
          <select
            value={selectedDateRange}
            onChange={(e) => setSelectedDateRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="today">오늘</option>
            <option value="yesterday">어제</option>
            <option value="week">최근 7일</option>
            <option value="month">최근 30일</option>
          </select>
          
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              autoRefresh
                ? 'bg-green-500 text-white hover:bg-green-600'
                : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
            }`}
          >
            {autoRefresh ? '🟢 자동 새로고침' : '⏸️ 일시정지'}
          </button>
          <button
            onClick={handleManualRefresh}
            disabled={refreshing}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              refreshing
                ? 'bg-gray-400 text-white cursor-not-allowed'
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            {refreshing ? '⏳ 새로고침 중...' : '🔄 수동 새로고침'}
          </button>
        </div>
      </div>

      {/* 핵심 지표 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 배차 현황 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-700">배차 현황</h3>
            <Package className="w-6 h-6 text-blue-500" />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">총 배차:</span>
              <span className="font-bold text-2xl text-blue-600">{liveStats.dispatch.total}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">진행중:</span>
              <span className="text-yellow-600 font-medium">{liveStats.dispatch.in_progress}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">완료:</span>
              <span className="text-green-600 font-medium">{liveStats.dispatch.completed}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">대기:</span>
              <span className="text-gray-600 font-medium">{liveStats.dispatch.draft}</span>
            </div>
          </div>
        </div>

        {/* 차량 가동률 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-700">차량 가동률</h3>
            <Truck className="w-6 h-6 text-green-500" />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">가동률:</span>
              <span className="font-bold text-2xl text-green-600">
                {liveStats.vehicle.utilization_rate}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-green-500 h-2 rounded-full transition-all"
                style={{ width: `${liveStats.vehicle.utilization_rate}%` }}
              />
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs mt-4">
              <div className="text-center">
                <div className="text-green-600 font-bold">{liveStats.vehicle.in_use}</div>
                <div className="text-gray-500">운행중</div>
              </div>
              <div className="text-center">
                <div className="text-blue-600 font-bold">{liveStats.vehicle.available}</div>
                <div className="text-gray-500">대기</div>
              </div>
              <div className="text-center">
                <div className="text-red-600 font-bold">{liveStats.vehicle.maintenance}</div>
                <div className="text-gray-500">정비</div>
              </div>
            </div>
          </div>
        </div>

        {/* 주문 처리율 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-700">주문 처리율</h3>
            <CheckCircle className="w-6 h-6 text-purple-500" />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">완료율:</span>
              <span className="font-bold text-2xl text-purple-600">
                {liveStats.order.completion_rate}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-purple-500 h-2 rounded-full transition-all"
                style={{ width: `${liveStats.order.completion_rate}%` }}
              />
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs mt-4">
              <div>
                <div className="text-gray-500">배송완료</div>
                <div className="text-purple-600 font-bold">{liveStats.order.delivered}</div>
              </div>
              <div>
                <div className="text-gray-500">배송중</div>
                <div className="text-yellow-600 font-bold">{liveStats.order.in_transit}</div>
              </div>
            </div>
          </div>
        </div>

        {/* AI 최적화 효과 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-700">AI 최적화</h3>
            <Zap className="w-6 h-6 text-yellow-500" />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">절감 거리:</span>
              <span className="font-bold text-xl text-yellow-600">
                {liveStats.ai_optimization.estimated_savings_km.toFixed(1)} km
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">절감 비용:</span>
              <span className="font-bold text-xl text-yellow-600">
                ₩{liveStats.ai_optimization.estimated_savings_cost.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between text-sm mt-2">
              <span className="text-gray-500">AI 배차 건수:</span>
              <span className="font-medium">{liveStats.ai_optimization.enabled_dispatches}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">평균 점수:</span>
              <span className="font-medium">
                {liveStats.ai_optimization.avg_optimization_score.toFixed(3)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Agent 성능 레이더 차트 */}
      {Object.keys(agentPerformance).length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            ML Agent 성능 분석 (최근 30일)
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 레이더 차트 */}
            <div>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={Object.entries(agentPerformance).map(([name, data]) => ({
                  agent: data.agent_name,
                  correlation: Math.max(0, data.correlation) * 100,
                  sample_count: Math.min(data.sample_count / 10, 100)
                }))}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="agent" />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar
                    name="상관계수 (%)"
                    dataKey="correlation"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.6}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Agent 상세 정보 */}
            <div className="space-y-3">
              {Object.entries(agentPerformance).map(([name, data]) => (
                <div key={name} className="border-l-4 border-blue-500 pl-4">
                  <div className="flex justify-between items-start mb-1">
                    <h4 className="font-semibold text-gray-700">{data.agent_name}</h4>
                    <span className={`text-sm px-2 py-1 rounded ${
                      data.correlation > 0.7
                        ? 'bg-green-100 text-green-700'
                        : data.correlation > 0.4
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      상관계수: {data.correlation.toFixed(2)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{data.recommendation}</p>
                  <p className="text-xs text-gray-500 mt-1">샘플 수: {data.sample_count}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 공차 거리 트렌드 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <MapPin className="w-6 h-6 text-red-600" />
          공차 거리 현황
        </h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-gray-600 text-sm">평균 공차거리</div>
            <div className="text-3xl font-bold text-red-600 mt-2">
              {liveStats.dispatch.avg_empty_distance_km.toFixed(1)} km
            </div>
          </div>
          <div>
            <div className="text-gray-600 text-sm">총 주행거리</div>
            <div className="text-3xl font-bold text-blue-600 mt-2">
              {liveStats.dispatch.total_distance_km.toFixed(1)} km
            </div>
          </div>
          <div>
            <div className="text-gray-600 text-sm">공차 비율</div>
            <div className="text-3xl font-bold text-purple-600 mt-2">
              {(
                (liveStats.dispatch.avg_empty_distance_km /
                  (liveStats.dispatch.total_distance_km || 1)) *
                100
              ).toFixed(1)}
              %
            </div>
          </div>
        </div>
      </div>
      </div>
    </Layout>
  );
};

export default DispatchMonitoringDashboard;

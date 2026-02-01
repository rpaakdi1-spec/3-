import React, { useState, useEffect } from 'react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { DollarSign, TrendingUp, TrendingDown, Activity, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '../api/client';

interface CostSummary {
  period: string;
  period_days: number;
  total_cost: number;
  today_cost: number;
  yesterday_cost: number;
  avg_daily_cost: number;
  model_costs: {
    [model: string]: {
      cost: number;
      percentage: number;
    };
  };
  total_requests: number;
  success_rate: number;
}

interface UsageStats {
  total_requests: number;
  total_cost: number;
  total_tokens: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  by_model: {
    [model: string]: {
      requests: number;
      total_cost: number;
      total_tokens: number;
      prompt_tokens: number;
      completion_tokens: number;
      avg_response_time_ms: number;
      success_rate: number;
    };
  };
  by_date: Array<{
    date: string;
    requests: number;
    total_cost: number;
    total_tokens: number;
  }>;
  by_status: {
    success: number;
    error: number;
  };
  by_intent: {
    [intent: string]: {
      requests: number;
      total_cost: number;
    };
  };
}

const AICostDashboardPage: React.FC = () => {
  const [period, setPeriod] = useState<'7d' | '30d' | '90d'>('7d');
  const [costSummary, setCostSummary] = useState<CostSummary | null>(null);
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [period]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [summaryRes, statsRes] = await Promise.all([
        apiClient.getAICostSummary(period),
        apiClient.getAIUsageStats({})
      ]);

      setCostSummary(summaryRes);
      setUsageStats(statsRes);
    } catch (error) {
      console.error('데이터 로드 실패:', error);
      toast.error('데이터를 불러오는데 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // 차트 색상
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  // 모델별 비용 데이터 (파이 차트용)
  const modelCostData = costSummary
    ? Object.entries(costSummary.model_costs).map(([model, data]) => ({
        name: model,
        value: data.cost,
        percentage: data.percentage
      }))
    : [];

  // 날짜별 비용 데이터 (라인 차트용)
  const dailyCostData = usageStats?.by_date.map(item => ({
    date: new Date(item.date).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }),
    cost: item.total_cost,
    requests: item.requests
  })) || [];

  // 모델별 요청 수 (바 차트용)
  const modelRequestData = usageStats
    ? Object.entries(usageStats.by_model).map(([model, data]) => ({
        model,
        requests: data.requests,
        avgTime: Math.round(data.avg_response_time_ms)
      }))
    : [];

  // Intent별 비용 (바 차트용)
  const intentCostData = usageStats
    ? Object.entries(usageStats.by_intent)
        .map(([intent, data]) => ({
          intent: intent === 'create_order' ? '주문 등록' :
                  intent === 'create_multiple_orders' ? '다중 주문' :
                  intent === 'update_order' ? '주문 수정' :
                  intent === 'query_order' ? '주문 조회' :
                  intent,
          cost: data.total_cost,
          requests: data.requests
        }))
        .sort((a, b) => b.cost - a.cost)
    : [];

  // 비용 증감 계산
  const costChange = costSummary
    ? ((costSummary.today_cost - costSummary.yesterday_cost) / (costSummary.yesterday_cost || 1)) * 100
    : 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">데이터 로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">💰 AI 비용 모니터링</h1>
          <p className="text-gray-600 mt-1">OpenAI & Gemini API 사용량 및 비용 분석</p>
        </div>

        {/* 기간 선택 */}
        <div className="flex gap-2">
          {(['7d', '30d', '90d'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                period === p
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {p === '7d' ? '7일' : p === '30d' ? '30일' : '90일'}
            </button>
          ))}
        </div>
      </div>

      {/* 요약 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {/* 총 비용 */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">총 비용 ({period})</p>
              <p className="text-3xl font-bold text-gray-900">
                ${costSummary?.total_cost.toFixed(2) || '0.00'}
              </p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <DollarSign className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className={`mt-4 flex items-center text-sm ${costChange >= 0 ? 'text-red-600' : 'text-green-600'}`}>
            {costChange >= 0 ? (
              <TrendingUp className="w-4 h-4 mr-1" />
            ) : (
              <TrendingDown className="w-4 h-4 mr-1" />
            )}
            <span>전일 대비 {Math.abs(costChange).toFixed(1)}%</span>
          </div>
        </div>

        {/* 오늘 비용 */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">오늘 비용</p>
              <p className="text-3xl font-bold text-gray-900">
                ${costSummary?.today_cost.toFixed(2) || '0.00'}
              </p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <Activity className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <p className="mt-4 text-sm text-gray-600">
            평균: ${costSummary?.avg_daily_cost.toFixed(2) || '0.00'}/일
          </p>
        </div>

        {/* 총 요청 수 */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">총 요청 수</p>
              <p className="text-3xl font-bold text-gray-900">
                {costSummary?.total_requests.toLocaleString() || '0'}
              </p>
            </div>
            <div className="bg-purple-100 rounded-full p-3">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <p className="mt-4 text-sm text-gray-600">
            성공률: {costSummary?.success_rate.toFixed(1) || '0'}%
          </p>
        </div>

        {/* 총 토큰 */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">총 토큰</p>
              <p className="text-3xl font-bold text-gray-900">
                {((usageStats?.total_tokens || 0) / 1000).toFixed(1)}K
              </p>
            </div>
            <div className="bg-orange-100 rounded-full p-3">
              <AlertCircle className="w-6 h-6 text-orange-600" />
            </div>
          </div>
          <p className="mt-4 text-sm text-gray-600">
            입력: {((usageStats?.total_prompt_tokens || 0) / 1000).toFixed(1)}K | 
            출력: {((usageStats?.total_completion_tokens || 0) / 1000).toFixed(1)}K
          </p>
        </div>
      </div>

      {/* 차트 그리드 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* 날짜별 비용 추이 */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📈 날짜별 비용 추이</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={dailyCostData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip 
                formatter={(value: number) => `$${value.toFixed(4)}`}
                labelStyle={{ color: '#333' }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="cost"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.3}
                name="비용 (USD)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* 모델별 비용 분포 */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 모델별 비용 분포</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={modelCostData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percentage }) => `${name} (${percentage.toFixed(1)}%)`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {modelCostData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => `$${value.toFixed(4)}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 두 번째 차트 그리드 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 모델별 요청 수 */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🤖 모델별 요청 수</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={modelRequestData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="model" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="requests" fill="#3b82f6" name="요청 수" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Intent별 비용 */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 작업별 비용</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={intentCostData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="intent" />
              <YAxis />
              <Tooltip formatter={(value: number) => `$${value.toFixed(4)}`} />
              <Legend />
              <Bar dataKey="cost" fill="#10b981" name="비용 (USD)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 비용 절감 팁 */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 비용 절감 팁</h3>
        <ul className="space-y-2 text-blue-800">
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span><strong>단순 주문:</strong> GPT-3.5 Turbo 사용 (GPT-4 대비 10배 저렴)</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span><strong>개발/테스트:</strong> Gemini Pro 사용 (무료, 일일 제한 있음)</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span><strong>복잡한 주문:</strong> GPT-4만 사용 (정확도 우선)</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span><strong>현재 비용:</strong> 월 {costSummary ? `$${(costSummary.total_cost / costSummary.period_days * 30).toFixed(2)}` : '$0'} 예상 (현재 추세 기준)</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default AICostDashboardPage;

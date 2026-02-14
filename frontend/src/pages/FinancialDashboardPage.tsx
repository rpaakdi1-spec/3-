import React, { useState, useEffect, useMemo, useCallback } from 'react';
import Layout from '../components/common/Layout';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Calendar,
  Users,
  FileText,
  FileSpreadsheet,
  CreditCard,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Download
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { exportFinancialDashboard } from '../api/billing-enhanced';
import * as BillingEnhancedAPI from '../api/billing-enhanced';

// Use types from billing-enhanced API
type FinancialSummary = BillingEnhancedAPI.FinancialSummary;
type MonthlyTrend = BillingEnhancedAPI.MonthlyTrend;
type TopClient = BillingEnhancedAPI.TopClient;

const FinancialDashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [trends, setTrends] = useState<MonthlyTrend[]>([]);
  const [topClients, setTopClients] = useState<TopClient[]>([]);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [dateRange, setDateRange] = useState({
    start_date: new Date(new Date().setMonth(new Date().getMonth() - 3)).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });
  const [trendMonths, setTrendMonths] = useState(12);

  useEffect(() => {
    loadDashboardData();
  }, [dateRange, trendMonths]);


  const handleDownload = async (format: 'excel' | 'pdf') => {
    try {
      setDownloading(true);
      await exportFinancialDashboard(format, dateRange.start_date, dateRange.end_date);
    } catch (err: any) {
      console.error('Download failed:', err);
      alert('다운로드 실패: ' + err.message);
    } finally {
      setDownloading(false);
    }
  };

  const loadDashboardData = async () => {
    setLoading(true);
    
    try {
      // Load financial summary
      const summaryData = await BillingEnhancedAPI.getFinancialDashboard(
        dateRange.start_date,
        dateRange.end_date
      );
      setSummary(summaryData);

      // Load monthly trends
      const trendsData = await BillingEnhancedAPI.getMonthlyTrends(
        undefined,
        undefined,
        trendMonths
      );
      setTrends(trendsData);

      // Load top clients
      const clientsData = await BillingEnhancedAPI.getTopClients(
        dateRange.start_date,
        dateRange.end_date,
        10
      );
      setTopClients(clientsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatPercent = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

  return (
    <Layout>
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">재무 대시보드</h1>
            <p className="text-gray-600">청구/수금 현황 및 재무 분석</p>
          </div>
          <div className="flex gap-3">
            <button onClick={loadDashboardData} disabled={loading} className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50">
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
              새로고침
            </button>
          </div>
        </div>

        {/* Date Range Filter */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-col gap-4">
            {/* 빠른 선택 버튼 */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600 font-medium">빠른 선택:</span>
              <button
                onClick={() => handleQuickSelect(7)}
                className={getButtonStyle(7)}
              >
                최근 7일
              </button>
              <button
                onClick={() => handleQuickSelect(30)}
                className={getButtonStyle(30, 2)}
              >
                1개월
              </button>
              <button
                onClick={() => handleQuickSelect(90)}
                className={getButtonStyle(90, 2)}
              >
                3개월
              </button>
              <button
                onClick={() => handleQuickSelect(180)}
                className={getButtonStyle(180, 2)}
              >
                6개월
              </button>
            </div>
            
            {/* 날짜 입력 */}
            <div className="flex items-center gap-4">
              <Calendar className="w-5 h-5 text-gray-500" />
              <input
                type="date"
                value={dateRange.start_date}
                onChange={(e) => setDateRange({ ...dateRange, start_date: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <span className="text-gray-500">~</span>
              <input
                type="date"
                value={dateRange.end_date}
                onChange={(e) => setDateRange({ ...dateRange, end_date: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>


        {/* Download Buttons */}
        <div className="flex items-center gap-2 mb-6">
          <button
            onClick={() => handleDownload('excel')}
            disabled={downloading}
            className="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg disabled:opacity-50"
          >
            <FileSpreadsheet className="w-4 h-4 mr-2" />
            Excel 다운로드
          </button>
          <button
            onClick={() => handleDownload('pdf')}
            disabled={downloading}
            className="flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg disabled:opacity-50"
          >
            <FileText className="w-4 h-4 mr-2" />
            PDF 다운로드
          </button>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {/* Total Revenue */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">총 매출</span>
                <DollarSign className="w-5 h-5 text-blue-500" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(summary.total_revenue)}</p>
              <div className="flex items-center mt-2 text-sm">
                <ArrowUpRight className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-green-600">전월 대비 +12.5%</span>
              </div>
            </div>

            {/* Total Paid */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">수금액</span>
                <CreditCard className="w-5 h-5 text-green-500" />
              </div>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(summary.collected_amount)}</p>
              <p className="text-xs text-gray-500 mt-2">
                회수율: {formatPercent(summary.collection_rate)}
              </p>
            </div>

            {/* Outstanding */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">미수금</span>
                <AlertCircle className="w-5 h-5 text-orange-500" />
              </div>
              <p className="text-2xl font-bold text-orange-600">{formatCurrency(summary.total_receivables)}</p>
              <p className="text-xs text-gray-500 mt-2">
                연체: {formatCurrency(summary.overdue_receivables)} ({summary.overdue_count}건)
              </p>
            </div>

            {/* Pending Settlements */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">미지급 정산</span>
                <Users className="w-5 h-5 text-purple-500" />
              </div>
              <p className="text-2xl font-bold text-purple-600">{formatCurrency(summary.pending_settlements)}</p>
              <p className="text-xs text-gray-500 mt-2">
                정산 대기중
              </p>
            </div>
          </div>
        )}

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Monthly Revenue Trend */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">월별 매출 추이</h2>
              <select
                value={trendMonths}
                onChange={(e) => setTrendMonths(Number(e.target.value))}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={3}>최근 3개월</option>
                <option value={6}>최근 6개월</option>
                <option value={12}>최근 12개월</option>
              </select>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="month" stroke="#6B7280" style={{ fontSize: '12px' }} />
                <YAxis stroke="#6B7280" style={{ fontSize: '12px' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#FFF', border: '1px solid #E5E7EB', borderRadius: '8px' }}
                  formatter={(value: number) => formatCurrency(value)}
                />
                <Legend />
                <Line type="monotone" dataKey="revenue" stroke="#3B82F6" strokeWidth={2} name="매출" />
                <Line type="monotone" dataKey="collected" stroke="#10B981" strokeWidth={2} name="수금" />
                <Line type="monotone" dataKey="settlements" stroke="#8B5CF6" strokeWidth={2} name="정산" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Payment Rate Trend */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">월별 순이익</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="month" stroke="#6B7280" style={{ fontSize: '12px' }} />
                <YAxis stroke="#6B7280" style={{ fontSize: '12px' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#FFF', border: '1px solid #E5E7EB', borderRadius: '8px' }}
                  formatter={(value: number) => formatCurrency(value)}
                />
                <Legend />
                <Bar dataKey="net_profit" fill="#10B981" name="순이익" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Clients Table */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">주요 거래처 TOP 10</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    순위
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    거래처명
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    총 매출
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    청구 건수
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    회수율
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {topClients.map((client, index) => (
                  <tr key={client.client_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold ${
                          index === 0 ? 'bg-yellow-100 text-yellow-800' :
                          index === 1 ? 'bg-gray-100 text-gray-800' :
                          index === 2 ? 'bg-orange-100 text-orange-800' :
                          'bg-blue-50 text-blue-800'
                        }`}>
                          {index + 1}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{client.client_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm font-semibold text-gray-900">{formatCurrency(client.total_revenue)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm text-gray-900">{client.invoice_count}건</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className={`text-sm font-medium ${
                        client.collection_rate >= 90 ? 'text-green-600' :
                        client.collection_rate >= 70 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {formatPercent(client.collection_rate)}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow text-left">
            <FileText className="w-8 h-8 text-blue-500 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-1">청구서 생성</h3>
            <p className="text-sm text-gray-600">월간 청구서 일괄 생성</p>
          </button>

          <button className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow text-left">
            <AlertCircle className="w-8 h-8 text-orange-500 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-1">연체 관리</h3>
            <p className="text-sm text-gray-600">연체 청구서 알림 발송</p>
          </button>

          <button className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow text-left">
            <Users className="w-8 h-8 text-purple-500 mb-3" />
            <h3 className="font-semibold text-gray-900 mb-1">정산 처리</h3>
            <p className="text-sm text-gray-600">기사 정산 승인/지급</p>
          </button>
        </div>
      </div>
    </div>
    </Layout>
  );
};

export default FinancialDashboardPage;

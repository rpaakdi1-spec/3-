import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import { Download, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import * as BillingEnhancedAPI from '../api/billing-enhanced';
import toast from 'react-hot-toast';
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
} from 'recharts';

const FinancialDashboardPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [dateRange, setDateRange] = useState({
    start_date: '2026-01-01',
    end_date: '2026-02-12',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await BillingEnhancedAPI.getFinancialDashboard(
        dateRange.start_date,
        dateRange.end_date
      );
      setData(response);
    } catch (error) {
      toast.error('데이터 로드 실패');
      console.error('Failed to fetch financial dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (type: 'excel' | 'pdf') => {
    setDownloading(true);
    try {
      await BillingEnhancedAPI.exportFinancialDashboard(
        type,
        dateRange.start_date,
        dateRange.end_date
      );
      toast.success(`${type.toUpperCase()} 다운로드 완료`);
    } catch (error) {
      toast.error('다운로드 실패');
      console.error('Download failed:', error);
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-500">로딩 중...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">재무 대시보드</h1>
            <p className="text-gray-500 mt-1">전체 재무 현황을 확인하세요</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => handleDownload('excel')}
              disabled={downloading}
              className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Download size={20} />
              Excel 다운로드
            </button>
            <button
              onClick={() => handleDownload('pdf')}
              disabled={downloading}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Download size={20} />
              PDF 다운로드
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        {data && data.summary && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">총 매출</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      ₩{data.summary.total_revenue?.toLocaleString() || 0}
                    </p>
                  </div>
                  <div className="p-3 bg-blue-100 rounded-full">
                    <DollarSign className="text-blue-600" size={24} />
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">수금액</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      ₩{data.summary.total_collected?.toLocaleString() || 0}
                    </p>
                  </div>
                  <div className="p-3 bg-green-100 rounded-full">
                    <TrendingUp className="text-green-600" size={24} />
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">미수금</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      ₩{data.summary.total_unpaid?.toLocaleString() || 0}
                    </p>
                  </div>
                  <div className="p-3 bg-red-100 rounded-full">
                    <TrendingDown className="text-red-600" size={24} />
                  </div>
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Monthly Trend */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  월별 추이
                </h2>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={data.monthly_trend || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="revenue"
                      stroke="#3b82f6"
                      name="매출"
                    />
                    <Line
                      type="monotone"
                      dataKey="collected"
                      stroke="#10b981"
                      name="수금"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Top Clients */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  상위 고객 TOP 10
                </h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.top_clients || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="revenue" fill="#3b82f6" name="매출" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
};

export default FinancialDashboardPage;

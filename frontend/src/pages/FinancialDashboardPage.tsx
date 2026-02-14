import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import { getFinancialDashboard, exportFinancialDashboard } from '../api/billing-enhanced';
import { FileSpreadsheet, FileText, RefreshCw } from 'lucide-react';

const FinancialDashboardPage: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [downloading, setDownloading] = useState<boolean>(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const startDate = '2026-01-01';
  const endDate = '2026-02-12';

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await getFinancialDashboard(startDate, endDate);
      console.log('API Response:', result);
      
      setData(result);
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to fetch dashboard data:', err);
      setError(err.message || 'Failed to load data');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDownload = async (format: 'excel' | 'pdf') => {
    try {
      setDownloading(true);
      await exportFinancialDashboard(format, startDate, endDate);
    } catch (err: any) {
      console.error('Download failed:', err);
      alert('다운로드 실패: ' + err.message);
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="text-lg text-gray-600">데이터 로딩 중...</div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="flex flex-col justify-center items-center h-64 space-y-4">
          <div className="text-lg text-red-600">오류: {error}</div>
          <button onClick={fetchData} className="px-4 py-2 bg-blue-600 text-white rounded-lg">
            다시 시도
          </button>
        </div>
      </Layout>
    );
  }

  if (!data) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="text-lg text-gray-600">데이터가 없습니다</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">재무 대시보드</h1>
          <div className="flex space-x-2">
            <button onClick={fetchData} disabled={loading} className="flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg">
              <RefreshCw className="w-4 h-4 mr-2" />
              새로고침
            </button>
            <button onClick={() => handleDownload('excel')} disabled={downloading} className="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg">
              <FileSpreadsheet className="w-4 h-4 mr-2" />
              Excel
            </button>
            <button onClick={() => handleDownload('pdf')} disabled={downloading} className="flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg">
              <FileText className="w-4 h-4 mr-2" />
              PDF
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
            <h3 className="text-sm font-medium text-gray-500 mb-2">총 매출</h3>
            <p className="text-3xl font-bold text-blue-600">
              ₩{(data.total_revenue || 0).toLocaleString()}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
            <h3 className="text-sm font-medium text-gray-500 mb-2">수금액</h3>
            <p className="text-3xl font-bold text-green-600">
              ₩{(data.collected_amount || 0).toLocaleString()}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-orange-500">
            <h3 className="text-sm font-medium text-gray-500 mb-2">미수금</h3>
            <p className="text-3xl font-bold text-orange-600">
              ₩{(data.total_receivables || 0).toLocaleString()}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <h4 className="text-xs text-gray-500 mb-1">수금률</h4>
            <p className="text-xl font-bold text-blue-600">{(data.collection_rate || 0).toFixed(1)}%</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h4 className="text-xs text-gray-500 mb-1">연체 미수금</h4>
            <p className="text-xl font-bold text-red-600">₩{(data.overdue_receivables || 0).toLocaleString()}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h4 className="text-xs text-gray-500 mb-1">연체 건수</h4>
            <p className="text-xl font-bold text-orange-600">{data.overdue_count || 0}건</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h4 className="text-xs text-gray-500 mb-1">순현금흐름</h4>
            <p className="text-xl font-bold text-green-600">₩{(data.net_cash_flow || 0).toLocaleString()}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">상세 정보</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">청구 및 수금</h3>
              <ul className="space-y-2 text-sm">
                <li className="flex justify-between">
                  <span className="text-gray-600">청구 금액:</span>
                  <span className="font-medium">₩{(data.invoiced_amount || 0).toLocaleString()}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">수금 금액:</span>
                  <span className="font-medium">₩{(data.collected_amount || 0).toLocaleString()}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">현재 미수금:</span>
                  <span className="font-medium">₩{(data.current_receivables || 0).toLocaleString()}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">연체 미수금:</span>
                  <span className="font-medium text-red-600">₩{(data.overdue_receivables || 0).toLocaleString()}</span>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">정산 현황</h3>
              <ul className="space-y-2 text-sm">
                <li className="flex justify-between">
                  <span className="text-gray-600">총 정산액:</span>
                  <span className="font-medium">₩{(data.total_settlements || 0).toLocaleString()}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">대기 중:</span>
                  <span className="font-medium">₩{(data.pending_settlements || 0).toLocaleString()}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">완료:</span>
                  <span className="font-medium">₩{(data.paid_settlements || 0).toLocaleString()}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            📅 조회 기간: {data.period_start} ~ {data.period_end}
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default FinancialDashboardPage;

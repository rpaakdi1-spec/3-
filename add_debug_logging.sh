#!/bin/bash

echo "======================================"
echo "재무 대시보드 디버깅 버전 생성"
echo "======================================"
echo ""

cd /root/uvis

# Backup original file
cp frontend/src/pages/FinancialDashboardPage.tsx frontend/src/pages/FinancialDashboardPage.tsx.before-debug
echo "✅ 원본 파일 백업 완료"

# Add comprehensive debug logging
cat > frontend/src/pages/FinancialDashboardPage.tsx << 'EOF'
import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import { BillingEnhancedAPI } from '../api/billing-enhanced';
import { FileSpreadsheet, FileText, RefreshCw } from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const FinancialDashboardPage: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [downloading, setDownloading] = useState<boolean>(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Fixed date range
  const startDate = '2026-01-01';
  const endDate = '2026-02-12';

  const fetchData = async () => {
    console.log('📊 Fetching financial dashboard data...');
    console.log('Date range:', { startDate, endDate });
    
    try {
      setLoading(true);
      setError(null);
      
      const result = await BillingEnhancedAPI.getFinancialDashboard(startDate, endDate);
      
      console.log('✅ API Response:', result);
      console.log('Summary:', result?.summary);
      console.log('Monthly Trends:', result?.monthly_trends);
      console.log('Top Clients:', result?.top_clients);
      
      setData(result);
      setLoading(false);
    } catch (err: any) {
      console.error('❌ Failed to fetch dashboard data:', err);
      console.error('Error details:', err.message, err.response);
      setError(err.message || 'Failed to load data');
      setLoading(false);
    }
  };

  useEffect(() => {
    console.log('🔄 FinancialDashboardPage mounted');
    fetchData();
  }, []);

  const handleDownload = async (format: 'excel' | 'pdf') => {
    console.log(`📥 Download ${format} clicked`);
    
    try {
      setDownloading(true);
      await BillingEnhancedAPI.exportFinancialDashboard(format, startDate, endDate);
      console.log(`✅ ${format} download successful`);
    } catch (err: any) {
      console.error(`❌ ${format} download failed:`, err);
      alert(`다운로드 실패: ${err.message}`);
    } finally {
      setDownloading(false);
    }
  };

  console.log('🎨 Render state:', { loading, downloading, hasData: !!data, error });

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
        <div className="flex justify-center items-center h-64">
          <div className="text-lg text-red-600">오류: {error}</div>
        </div>
      </Layout>
    );
  }

  if (!data) {
    console.warn('⚠️  No data available');
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="text-lg text-gray-600">데이터가 없습니다</div>
        </div>
      </Layout>
    );
  }

  console.log('✅ Rendering dashboard with data');

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">재무 대시보드</h1>
          <div className="flex space-x-2">
            <button
              onClick={() => fetchData()}
              disabled={loading}
              className="flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              새로고침
            </button>
            <button
              onClick={() => handleDownload('excel')}
              disabled={downloading}
              className="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
            >
              <FileSpreadsheet className="w-4 h-4 mr-2" />
              Excel 다운로드
            </button>
            <button
              onClick={() => handleDownload('pdf')}
              disabled={downloading}
              className="flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              <FileText className="w-4 h-4 mr-2" />
              PDF 다운로드
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        {data.summary && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-sm font-medium text-gray-500">총 매출</h3>
              <p className="mt-2 text-3xl font-bold text-blue-600">
                ₩{data.summary.total_revenue?.toLocaleString() || '0'}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-sm font-medium text-gray-500">수금액</h3>
              <p className="mt-2 text-3xl font-bold text-green-600">
                ₩{data.summary.total_collected?.toLocaleString() || '0'}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-sm font-medium text-gray-500">미수금</h3>
              <p className="mt-2 text-3xl font-bold text-orange-600">
                ₩{data.summary.total_unpaid?.toLocaleString() || '0'}
              </p>
            </div>
          </div>
        )}

        {/* Monthly Trend Chart */}
        {data.monthly_trends && data.monthly_trends.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">월별 추이</h2>
            <div style={{ height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.monthly_trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="revenue" stroke="#3b82f6" name="총 매출" />
                  <Line type="monotone" dataKey="collected" stroke="#10b981" name="수금액" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Top Clients Chart */}
        {data.top_clients && data.top_clients.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">상위 고객 TOP 10</h2>
            <div style={{ height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.top_clients}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="client_name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="total_revenue" fill="#3b82f6" name="총 매출" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Debug Panel */}
        <details className="bg-gray-100 p-4 rounded-lg">
          <summary className="cursor-pointer font-semibold">🐛 디버그 정보 (개발자용)</summary>
          <pre className="mt-4 p-4 bg-white rounded overflow-auto text-xs">
            {JSON.stringify(data, null, 2)}
          </pre>
        </details>
      </div>
    </Layout>
  );
};

export default FinancialDashboardPage;
EOF

echo "✅ 디버깅 버전 생성 완료"
echo ""

echo "=== 빌드 및 배포 ==="
cd frontend
npm run build

if [ $? -eq 0 ]; then
    echo "✅ 빌드 성공"
    
    cd /root/uvis
    docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
    echo "✅ 파일 복사 완료"
    
    docker-compose restart frontend
    echo "✅ 컨테이너 재시작 완료"
    
    sleep 15
    
    docker ps | grep frontend
    echo ""
    
    echo "======================================"
    echo "배포 완료!"
    echo "======================================"
    echo ""
    echo "브라우저에서 다음을 확인하세요:"
    echo "1. Ctrl+Shift+R로 강력 새로고침"
    echo "2. F12 → Console에서 로그 확인"
    echo "   - 📊 Fetching..."
    echo "   - ✅ API Response: ..."
    echo "   - 🎨 Render state: ..."
    echo "3. 요약 카드, 차트 표시 확인"
    echo ""
else
    echo "❌ 빌드 실패"
    echo "오류를 확인하세요"
fi

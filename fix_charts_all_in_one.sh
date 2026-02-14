#!/bin/bash

# 재무 대시보드 차트 문제 해결 - 올인원 스크립트
# 사용법: ./fix_charts_all_in_one.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     재무 대시보드 차트 문제 해결 - 올인원 스크립트        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd /root/uvis

# ===== 1단계: 진단 =====
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  진단 단계"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📊 API 응답 확인 중..."
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJBRE1JTiIsImV4cCI6MTc3MDkxMDE5MX0.oCkeT-Yc3daW0n2TAhaCw7NJGmpoDUZlhBLggdeKDfI"
API_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/billing/enhanced/dashboard/financial?start_date=2026-01-01&end_date=2026-02-12" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

if echo "$API_RESPONSE" | jq -e '.summary' > /dev/null 2>&1; then
    echo "✅ API 응답 정상"
    echo "$API_RESPONSE" | jq '.summary'
else
    echo "❌ API 응답 오류 또는 데이터 없음"
    echo "$API_RESPONSE"
fi
echo ""

echo "📦 Recharts 패키지 확인 중..."
cd frontend
if grep -q '"recharts"' package.json; then
    RECHARTS_VERSION=$(grep '"recharts"' package.json | sed 's/.*"recharts": "\(.*\)".*/\1/')
    echo "✅ Recharts 설치됨 (버전: $RECHARTS_VERSION)"
else
    echo "⚠️  Recharts 미설치 - 설치 중..."
    npm install recharts --save
    echo "✅ Recharts 설치 완료"
fi
cd /root/uvis
echo ""

echo "📄 FinancialDashboardPage 파일 확인 중..."
if [ -f "frontend/src/pages/FinancialDashboardPage.tsx" ]; then
    FILE_SIZE=$(wc -l < frontend/src/pages/FinancialDashboardPage.tsx)
    echo "✅ 파일 존재 (라인 수: $FILE_SIZE)"
else
    echo "❌ 파일 없음!"
    exit 1
fi
echo ""

# ===== 2단계: 디버깅 버전 생성 =====
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  디버깅 버전 생성"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "💾 원본 파일 백업 중..."
cp frontend/src/pages/FinancialDashboardPage.tsx frontend/src/pages/FinancialDashboardPage.tsx.backup-$(date +%Y%m%d-%H%M%S)
echo "✅ 백업 완료"
echo ""

echo "🔧 디버깅 로그 추가 중..."
cat > frontend/src/pages/FinancialDashboardPage.tsx << 'EOFDEBUG'
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

  const startDate = '2026-01-01';
  const endDate = '2026-02-12';

  const fetchData = async () => {
    console.log('📊 [DEBUG] Fetching financial dashboard data...');
    console.log('📅 [DEBUG] Date range:', { startDate, endDate });
    
    try {
      setLoading(true);
      setError(null);
      
      const result = await BillingEnhancedAPI.getFinancialDashboard(startDate, endDate);
      
      console.log('✅ [DEBUG] API Response received:', result);
      console.log('💰 [DEBUG] Summary:', result?.summary);
      console.log('📈 [DEBUG] Monthly Trends:', result?.monthly_trends?.length, 'items');
      console.log('👥 [DEBUG] Top Clients:', result?.top_clients?.length, 'items');
      
      setData(result);
      setLoading(false);
    } catch (err: any) {
      console.error('❌ [DEBUG] Failed to fetch:', err);
      console.error('🔍 [DEBUG] Error details:', {
        message: err.message,
        response: err.response,
        stack: err.stack
      });
      setError(err.message || 'Failed to load data');
      setLoading(false);
    }
  };

  useEffect(() => {
    console.log('🚀 [DEBUG] FinancialDashboardPage mounted');
    fetchData();
  }, []);

  const handleDownload = async (format: 'excel' | 'pdf') => {
    console.log(`📥 [DEBUG] Download ${format} clicked`);
    
    try {
      setDownloading(true);
      await BillingEnhancedAPI.exportFinancialDashboard(format, startDate, endDate);
      console.log(`✅ [DEBUG] ${format} download successful`);
    } catch (err: any) {
      console.error(`❌ [DEBUG] ${format} download failed:`, err);
      alert(`다운로드 실패: ${err.message}`);
    } finally {
      setDownloading(false);
    }
  };

  console.log('🎨 [DEBUG] Current render state:', {
    loading,
    downloading,
    hasData: !!data,
    hasSummary: !!data?.summary,
    hasMonthlyTrends: !!data?.monthly_trends,
    hasTopClients: !!data?.top_clients,
    error
  });

  if (loading) {
    console.log('⏳ [DEBUG] Rendering loading state');
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="text-lg text-gray-600">데이터 로딩 중...</div>
        </div>
      </Layout>
    );
  }

  if (error) {
    console.log('⚠️  [DEBUG] Rendering error state:', error);
    return (
      <Layout>
        <div className="flex flex-col justify-center items-center h-64 space-y-4">
          <div className="text-lg text-red-600">오류: {error}</div>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
          >
            다시 시도
          </button>
        </div>
      </Layout>
    );
  }

  if (!data) {
    console.warn('⚠️  [DEBUG] No data available');
    return (
      <Layout>
        <div className="flex flex-col justify-center items-center h-64 space-y-4">
          <div className="text-lg text-gray-600">데이터가 없습니다</div>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
          >
            새로고침
          </button>
        </div>
      </Layout>
    );
  }

  console.log('✅ [DEBUG] Rendering dashboard with data');

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
              Excel
            </button>
            <button
              onClick={() => handleDownload('pdf')}
              disabled={downloading}
              className="flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              <FileText className="w-4 h-4 mr-2" />
              PDF
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        {console.log('🎴 [DEBUG] Rendering summary cards:', !!data.summary)}
        {data.summary ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
              <h3 className="text-sm font-medium text-gray-500 mb-2">총 매출</h3>
              <p className="text-3xl font-bold text-blue-600">
                ₩{(data.summary.total_revenue || 0).toLocaleString()}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
              <h3 className="text-sm font-medium text-gray-500 mb-2">수금액</h3>
              <p className="text-3xl font-bold text-green-600">
                ₩{(data.summary.total_collected || 0).toLocaleString()}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-orange-500">
              <h3 className="text-sm font-medium text-gray-500 mb-2">미수금</h3>
              <p className="text-3xl font-bold text-orange-600">
                ₩{(data.summary.total_unpaid || 0).toLocaleString()}
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-yellow-800">⚠️  요약 데이터가 없습니다</p>
          </div>
        )}

        {/* Monthly Trend Chart */}
        {console.log('📊 [DEBUG] Rendering monthly trends:', data.monthly_trends?.length)}
        {data.monthly_trends && data.monthly_trends.length > 0 ? (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">월별 추이</h2>
            <div style={{ width: '100%', height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.monthly_trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => `₩${value.toLocaleString()}`} />
                  <Legend />
                  <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} name="총 매출" />
                  <Line type="monotone" dataKey="collected" stroke="#10b981" strokeWidth={2} name="수금액" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-yellow-800">⚠️  월별 추이 데이터가 없습니다</p>
          </div>
        )}

        {/* Top Clients Chart */}
        {console.log('👥 [DEBUG] Rendering top clients:', data.top_clients?.length)}
        {data.top_clients && data.top_clients.length > 0 ? (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">상위 고객 TOP 10</h2>
            <div style={{ width: '100%', height: '400px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.top_clients}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="client_name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip formatter={(value) => `₩${value.toLocaleString()}`} />
                  <Legend />
                  <Bar dataKey="total_revenue" fill="#3b82f6" name="총 매출" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-yellow-800">⚠️  상위 고객 데이터가 없습니다</p>
          </div>
        )}

        {/* Debug Panel */}
        <details className="bg-gray-100 p-4 rounded-lg border border-gray-300">
          <summary className="cursor-pointer font-semibold text-gray-700 hover:text-gray-900">
            🐛 디버그 정보 (개발자용)
          </summary>
          <div className="mt-4 space-y-2">
            <div className="bg-white p-4 rounded border">
              <h4 className="font-semibold mb-2">상태:</h4>
              <pre className="text-xs overflow-auto">
{JSON.stringify({ loading, downloading, error, hasData: !!data }, null, 2)}
              </pre>
            </div>
            <div className="bg-white p-4 rounded border">
              <h4 className="font-semibold mb-2">API 응답 전체:</h4>
              <pre className="text-xs overflow-auto max-h-96">
{JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        </details>
      </div>
    </Layout>
  );
};

export default FinancialDashboardPage;
EOFDEBUG

echo "✅ 디버깅 로그 추가 완료"
echo ""

# ===== 3단계: 빌드 및 배포 =====
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  빌드 및 배포"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔨 프론트엔드 빌드 중..."
cd frontend
npm run build

if [ $? -ne 0 ]; then
    echo "❌ 빌드 실패!"
    exit 1
fi

BUILD_SIZE=$(du -sh dist | awk '{print $1}')
echo "✅ 빌드 성공 (크기: $BUILD_SIZE)"
echo ""

cd /root/uvis

echo "📦 Docker 컨테이너에 파일 복사 중..."
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
echo "✅ 파일 복사 완료"
echo ""

echo "🔄 프론트엔드 컨테이너 재시작 중..."
docker-compose restart frontend
sleep 15
echo "✅ 컨테이너 재시작 완료"
echo ""

# ===== 4단계: 검증 =====
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  배포 검증"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📊 컨테이너 상태 확인..."
docker ps | grep -E "CONTAINER|frontend"
echo ""

echo "📄 배포된 파일 확인..."
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/Financial* 2>&1 | head -5 || echo "(FinancialDashboard 관련 파일 확인)"
echo ""

# ===== 완료 =====
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ✅ 배포 완료!                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 다음 단계:"
echo ""
echo "1️⃣  브라우저 테스트:"
echo "   • URL: http://139.150.11.99"
echo "   • 로그인: admin / admin123"
echo "   • 메뉴: 청구/정산 → 재무 대시보드"
echo ""
echo "2️⃣  강력 새로고침:"
echo "   • Windows/Linux: Ctrl + Shift + R"
echo "   • macOS: Cmd + Shift + R"
echo ""
echo "3️⃣  개발자 도구 확인 (F12):"
echo "   • Console 탭: 디버그 로그 확인"
echo "     - 📊 [DEBUG] Fetching..."
echo "     - ✅ [DEBUG] API Response..."
echo "     - 🎨 [DEBUG] Current render state..."
echo "   • Network 탭: API 호출 상태 확인"
echo "   • Elements 탭: DOM 구조 확인"
echo ""
echo "4️⃣  디버그 패널 확인:"
echo "   • 페이지 하단의 '🐛 디버그 정보' 펼치기"
echo "   • API 응답 데이터 확인"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 문제가 지속되면:"
echo "   • Console 탭 스크린샷"
echo "   • Network 탭 스크린샷"
echo "   • 디버그 패널 내용"
echo "   위 3가지를 함께 제공해 주세요."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

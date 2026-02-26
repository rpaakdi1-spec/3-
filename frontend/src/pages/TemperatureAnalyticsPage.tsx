import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import {
  BarChart3,
  TrendingUp,
  Award,
  AlertTriangle,
  Download,
  Calendar,
  Filter,
  RefreshCw,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface AnalyticsSummary {
  period_days: number;
  compliance: {
    rate: number;
    total_records: number;
    violations: number;
  };
  performance: {
    avg_score: number;
    total_vehicles: number;
    scored_vehicles: number;
  };
  fleet_status: {
    normal_vehicles: number;
    violation_vehicles: number;
    total_alerts: number;
    critical_alerts: number;
  };
  overall_grade: string;
  key_insights: string[];
}

interface VehiclePerformance {
  vehicle_id: number;
  vehicle_number: string;
  score: number;
  grade: string;
  metrics: any;
  recommendations: string[];
}

const TemperatureAnalyticsPage: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [topPerformers, setTopPerformers] = useState<VehiclePerformance[]>([]);
  const [worstPerformers, setWorstPerformers] = useState<VehiclePerformance[]>([]);
  const [selectedDays, setSelectedDays] = useState(7);
  const [loading, setLoading] = useState(true);
  const [expandedSection, setExpandedSection] = useState<string | null>("summary");

  useEffect(() => {
    loadAllData();
  }, [selectedDays]);

  const loadAllData = async () => {
    try {
      setLoading(true);
      
      // Load summary
      const summaryRes = await apiClient.get(`/temperature-analytics/analytics-summary?days=${selectedDays}`);
      setSummary(summaryRes.data);
      
      // Load top performers
      const topRes = await apiClient.get(`/temperature-analytics/top-performers?days=${selectedDays}&limit=5`);
      setTopPerformers(topRes.data.top_performers);
      
      // Load worst performers
      const worstRes = await apiClient.get(`/temperature-analytics/worst-performers?days=${selectedDays}&limit=5`);
      setWorstPerformers(worstRes.data.worst_performers);
      
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadComplianceReport = async () => {
    try {
      const response = await apiClient.get(
        `/temperature-analytics/export/compliance-report?days=${selectedDays}`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `compliance_report_${selectedDays}days.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to download report:', error);
      alert('보고서 다운로드에 실패했습니다.');
    }
  };

  const downloadPerformanceReport = async () => {
    try {
      const response = await apiClient.get(
        `/temperature-analytics/export/performance-report?days=${selectedDays}`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `performance_report_${selectedDays}days.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to download report:', error);
      alert('보고서 다운로드에 실패했습니다.');
    }
  };

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  if (loading || !summary) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Chart data
  const complianceChartData = {
    labels: ['준수', '위반'],
    datasets: [{
      data: [summary.compliance.rate, 100 - summary.compliance.rate],
      backgroundColor: ['#10b981', '#ef4444'],
      borderWidth: 0
    }]
  };

  const performerComparisonData = {
    labels: topPerformers.map(p => p.vehicle_number),
    datasets: [{
      label: '성능 점수',
      data: topPerformers.map(p => p.score),
      backgroundColor: 'rgba(59, 130, 246, 0.6)',
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 2
    }]
  };

  return (<div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            온도 분석 대시보드
          </h1>
          <p className="text-sm text-gray-600 mt-1">고급 온도 분석 및 성능 리포트</p>
        </div>
        
        <div className="flex gap-2">
          {/* Period selector */}
          <select
            value={selectedDays}
            onChange={(e) => setSelectedDays(parseInt(e.target.value))}
            className="border border-gray-300 rounded-lg px-4 py-2"
          >
            <option value={7}>최근 7일</option>
            <option value={14}>최근 14일</option>
            <option value={30}>최근 30일</option>
            <option value={90}>최근 90일</option>
          </select>
          
          <button
            onClick={loadAllData}
            className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            새로고침
          </button>
        </div>
      </div>

      {/* Overall Grade Card */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-700 rounded-lg shadow-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold">{summary.overall_grade}</h2>
            <p className="text-blue-100 mt-1">전반적인 온도 관리 등급</p>
          </div>
          <Award className="w-16 h-16 text-blue-200" />
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-600">준수율</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {summary.compliance.rate.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {summary.compliance.total_records.toLocaleString()} 건
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-600">평균 성능 점수</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                {summary.performance.avg_score.toFixed(1)}점
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {summary.performance.scored_vehicles}대 / {summary.performance.total_vehicles}대
              </p>
            </div>
            <Award className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-600">위반 차량</p>
              <p className="text-2xl font-bold text-orange-600 mt-1">
                {summary.fleet_status.violation_vehicles}대
              </p>
              <p className="text-xs text-gray-500 mt-1">
                전체 {summary.fleet_status.normal_vehicles + summary.fleet_status.violation_vehicles}대
              </p>
            </div>
            <AlertTriangle className="w-8 h-8 text-orange-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-600">Critical 알림</p>
              <p className="text-2xl font-bold text-red-600 mt-1">
                {summary.fleet_status.critical_alerts}건
              </p>
              <p className="text-xs text-gray-500 mt-1">
                전체 {summary.fleet_status.total_alerts}건
              </p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
        </div>
      </div>

      {/* Key Insights */}
      <div className="bg-white rounded-lg shadow p-6">
        <div
          className="flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('insights')}
        >
          <h2 className="text-lg font-semibold">주요 인사이트</h2>
          {expandedSection === 'insights' ? <ChevronUp /> : <ChevronDown />}
        </div>
        
        {expandedSection === 'insights' && (
          <div className="mt-4 space-y-2">
            {summary.key_insights.map((insight, index) => (
              <div key={index} className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg">
                <div className="text-lg mt-0.5">
                  {insight.startsWith('✅') ? '✅' : insight.startsWith('⚠️') ? '⚠️' : insight.startsWith('🚨') ? '🚨' : '📊'}
                </div>
                <p className="text-sm text-gray-700">{insight}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compliance Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">준수율 현황</h2>
          <div style={{ height: '300px' }} className="flex items-center justify-center">
            <Doughnut
              data={complianceChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { position: 'bottom' }
                }
              }}
            />
          </div>
        </div>

        {/* Top Performers Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">우수 차량 성능</h2>
          <div style={{ height: '300px' }}>
            <Bar
              data={performerComparisonData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 100
                  }
                },
                plugins: {
                  legend: { display: false }
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Top Performers Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <div
          className="flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('top')}
        >
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Award className="w-5 h-5 text-yellow-500" />
            우수 차량 (Top 5)
          </h2>
          {expandedSection === 'top' ? <ChevronUp /> : <ChevronDown />}
        </div>
        
        {expandedSection === 'top' && (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4">순위</th>
                  <th className="text-left py-2 px-4">차량 번호</th>
                  <th className="text-left py-2 px-4">점수</th>
                  <th className="text-left py-2 px-4">등급</th>
                  <th className="text-left py-2 px-4">권장사항</th>
                </tr>
              </thead>
              <tbody>
                {topPerformers.map((performer, index) => (
                  <tr key={performer.vehicle_id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 font-bold text-lg">#{index + 1}</td>
                    <td className="py-3 px-4 font-medium">{performer.vehicle_number}</td>
                    <td className="py-3 px-4">
                      <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full font-semibold">
                        {performer.score.toFixed(1)}점
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full">
                        {performer.grade}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {performer.recommendations[0]}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Worst Performers Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <div
          className="flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('worst')}
        >
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            개선 필요 차량 (Bottom 5)
          </h2>
          {expandedSection === 'worst' ? <ChevronUp /> : <ChevronDown />}
        </div>
        
        {expandedSection === 'worst' && (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4">순위</th>
                  <th className="text-left py-2 px-4">차량 번호</th>
                  <th className="text-left py-2 px-4">점수</th>
                  <th className="text-left py-2 px-4">등급</th>
                  <th className="text-left py-2 px-4">개선 권장사항</th>
                </tr>
              </thead>
              <tbody>
                {worstPerformers.map((performer, index) => (
                  <tr key={performer.vehicle_id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 font-bold text-lg text-red-600">#{index + 1}</td>
                    <td className="py-3 px-4 font-medium">{performer.vehicle_number}</td>
                    <td className="py-3 px-4">
                      <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full font-semibold">
                        {performer.score.toFixed(1)}점
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full">
                        {performer.grade}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {performer.recommendations[0]}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Export Buttons */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">보고서 내보내기</h2>
        <div className="flex gap-4">
          <button
            onClick={downloadComplianceReport}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Download className="w-5 h-5" />
            준수 보고서 다운로드 (Excel)
          </button>
          
          <button
            onClick={downloadPerformanceReport}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 flex items-center gap-2"
          >
            <Download className="w-5 h-5" />
            성능 보고서 다운로드 (Excel)
          </button>
        </div>
      </div>
    </div>
  );
};

export default TemperatureAnalyticsPage;

/**
 * Reports Page - Generate and Download Business Reports
 * Provides UI for generating PDF and Excel reports
 */
import React, { useState } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { 
  FileText, Download, Calendar, Filter,
  TrendingUp, Users, Truck, DollarSign 
} from 'lucide-react';
import apiClient from '../api/client';

interface ReportConfig {
  type: 'dispatch' | 'vehicles' | 'drivers' | 'customers';
  format: 'pdf' | 'excel';
  start_date: string;
  end_date: string;
  vehicle_id?: number;
  driver_id?: number;
}

const ReportsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState<string>('dispatch');
  const [selectedFormat, setSelectedFormat] = useState<string>('pdf');
  const [startDate, setStartDate] = useState<string>(
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  );
  const [endDate, setEndDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );

  const reportTypes = [
    {
      id: 'dispatch',
      name: '배차 리포트',
      description: '배차 현황, 완료율, 상세 내역',
      icon: Truck,
      color: 'blue'
    },
    {
      id: 'vehicles',
      name: '차량 성능 리포트',
      description: '차량별 가동률, 적재율, 효율성',
      icon: TrendingUp,
      color: 'green'
    },
    {
      id: 'drivers',
      name: '운전자 평가 리포트',
      description: '운전자별 배송 완료율, 평균 주문 수',
      icon: Users,
      color: 'purple'
    },
    {
      id: 'customers',
      name: '고객 만족도 리포트',
      description: '고객별 주문 현황 및 만족도',
      icon: DollarSign,
      color: 'orange'
    }
  ];

  const handleGenerateReport = async () => {
    setLoading(true);
    
    try {
      const endpoint = `/reports/${selectedReport}/${selectedFormat}`;
      const params = {
        start_date: startDate,
        end_date: endDate
      };

      const response = await apiClient.post(endpoint, null, {
        params,
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const extension = selectedFormat === 'pdf' ? 'pdf' : 'xlsx';
      link.setAttribute('download', `${selectedReport}_report_${startDate}_${endDate}.${extension}`);
      
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      window.URL.revokeObjectURL(url);
      
      // Success notification
      alert('리포트가 성공적으로 생성되었습니다!');
    } catch (error) {
      console.error('Report generation failed:', error);
      alert('리포트 생성에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  };

  return (<div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">리포트 생성</h1>
          <p className="text-gray-600">비즈니스 리포트를 PDF 또는 Excel 형식으로 다운로드하세요</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Report Selection */}
          <div className="lg:col-span-2 space-y-4">
            <Card title="리포트 유형 선택">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {reportTypes.map((report) => {
                  const Icon = report.icon;
                  const isSelected = selectedReport === report.id;
                  
                  return (
                    <button
                      key={report.id}
                      onClick={() => setSelectedReport(report.id)}
                      className={`p-4 rounded-lg border-2 transition-all text-left ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`p-2 rounded-lg bg-${report.color}-100`}>
                          <Icon className={`text-${report.color}-600`} size={24} />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 mb-1">
                            {report.name}
                          </h3>
                          <p className="text-sm text-gray-600">
                            {report.description}
                          </p>
                        </div>
                      </div>
                      {isSelected && (
                        <div className="mt-2 flex items-center text-blue-600 text-sm font-medium">
                          <span className="w-2 h-2 bg-blue-600 rounded-full mr-2"></span>
                          선택됨
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </Card>

            {/* Date Range */}
            <Card title="기간 선택">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Calendar className="inline mr-2" size={16} />
                    시작일
                  </label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Calendar className="inline mr-2" size={16} />
                    종료일
                  </label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Quick Date Presets */}
              <div className="mt-4 flex flex-wrap gap-2">
                <button
                  onClick={() => {
                    const end = new Date();
                    const start = new Date(end.getTime() - 7 * 24 * 60 * 60 * 1000);
                    setStartDate(start.toISOString().split('T')[0]);
                    setEndDate(end.toISOString().split('T')[0]);
                  }}
                  className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  최근 7일
                </button>
                <button
                  onClick={() => {
                    const end = new Date();
                    const start = new Date(end.getTime() - 30 * 24 * 60 * 60 * 1000);
                    setStartDate(start.toISOString().split('T')[0]);
                    setEndDate(end.toISOString().split('T')[0]);
                  }}
                  className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  최근 30일
                </button>
                <button
                  onClick={() => {
                    const end = new Date();
                    const start = new Date(end.getFullYear(), end.getMonth(), 1);
                    setStartDate(start.toISOString().split('T')[0]);
                    setEndDate(end.toISOString().split('T')[0]);
                  }}
                  className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  이번 달
                </button>
                <button
                  onClick={() => {
                    const end = new Date();
                    end.setMonth(end.getMonth() - 1);
                    const lastMonth = new Date(end.getFullYear(), end.getMonth(), 1);
                    const lastMonthEnd = new Date(end.getFullYear(), end.getMonth() + 1, 0);
                    setStartDate(lastMonth.toISOString().split('T')[0]);
                    setEndDate(lastMonthEnd.toISOString().split('T')[0]);
                  }}
                  className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  지난 달
                </button>
              </div>
            </Card>
          </div>

          {/* Right: Format & Generate */}
          <div className="space-y-4">
            <Card title="파일 형식">
              <div className="space-y-3">
                <label className="flex items-center p-3 border-2 border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="radio"
                    name="format"
                    value="pdf"
                    checked={selectedFormat === 'pdf'}
                    onChange={(e) => setSelectedFormat(e.target.value)}
                    className="mr-3"
                  />
                  <FileText className="mr-2 text-red-600" size={20} />
                  <div>
                    <div className="font-medium">PDF</div>
                    <div className="text-sm text-gray-600">보기 전용 리포트</div>
                  </div>
                </label>
                
                <label className="flex items-center p-3 border-2 border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="radio"
                    name="format"
                    value="excel"
                    checked={selectedFormat === 'excel'}
                    onChange={(e) => setSelectedFormat(e.target.value)}
                    className="mr-3"
                  />
                  <FileText className="mr-2 text-green-600" size={20} />
                  <div>
                    <div className="font-medium">Excel</div>
                    <div className="text-sm text-gray-600">편집 가능한 스프레드시트</div>
                  </div>
                </label>
              </div>
            </Card>

            <Card>
              <Button
                onClick={handleGenerateReport}
                variant="primary"
                size="lg"
                className="w-full"
                isLoading={loading}
                disabled={!startDate || !endDate}
              >
                <Download className="mr-2" size={20} />
                리포트 생성
              </Button>
              
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <h4 className="text-sm font-medium text-blue-900 mb-2">선택 요약</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• 리포트: {reportTypes.find(r => r.id === selectedReport)?.name}</li>
                  <li>• 형식: {selectedFormat.toUpperCase()}</li>
                  <li>• 기간: {startDate} ~ {endDate}</li>
                </ul>
              </div>
            </Card>

            {/* Info Card */}
            <Card>
              <div className="text-sm text-gray-600 space-y-2">
                <h4 className="font-medium text-gray-900">💡 팁</h4>
                <ul className="list-disc list-inside space-y-1">
                  <li>PDF는 보기 및 인쇄에 적합합니다</li>
                  <li>Excel은 데이터 분석에 유용합니다</li>
                  <li>리포트는 즉시 다운로드됩니다</li>
                </ul>
              </div>
            </Card>
          </div>
        </div>
      </div>
  );
};

export default ReportsPage;

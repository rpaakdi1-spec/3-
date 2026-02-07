import React, { useState } from 'react';
import { Download, X, FileText, FileSpreadsheet, Calendar, Loader2 } from 'lucide-react';
import * as ReportsAPI from '../../api/reports';

interface ReportDownloadModalProps {
  isOpen: boolean;
  onClose: () => void;
  dateRange: {
    start_date: string;
    end_date: string;
  };
}

const ReportDownloadModal: React.FC<ReportDownloadModalProps> = ({
  isOpen,
  onClose,
  dateRange
}) => {
  const [reportType, setReportType] = useState<'pdf' | 'excel'>('excel');
  const [downloading, setDownloading] = useState(false);

  if (!isOpen) return null;

  const handleDownload = async () => {
    setDownloading(true);
    try {
      if (reportType === 'pdf') {
        await ReportsAPI.downloadFinancialDashboardPDF(
          dateRange.start_date,
          dateRange.end_date
        );
      } else {
        await ReportsAPI.downloadFinancialDashboardExcel(
          dateRange.start_date,
          dateRange.end_date
        );
      }
      onClose();
    } catch (error) {
      console.error('Failed to download report:', error);
      alert('리포트 다운로드 실패. 다시 시도해주세요.');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              재무 대시보드 리포트 다운로드
            </h2>
            <button
              onClick={onClose}
              disabled={downloading}
              className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Date Range Display */}
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm text-blue-900">
                <Calendar className="w-4 h-4" />
                <span className="font-medium">리포트 기간</span>
              </div>
              <p className="mt-2 text-lg font-semibold text-blue-900">
                {dateRange.start_date} ~ {dateRange.end_date}
              </p>
            </div>

            {/* Report Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                파일 형식 선택
              </label>
              <div className="grid grid-cols-2 gap-3">
                {/* Excel Option */}
                <button
                  onClick={() => setReportType('excel')}
                  disabled={downloading}
                  className={`p-4 rounded-lg border-2 transition-all disabled:opacity-50 ${
                    reportType === 'excel'
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200 hover:border-green-300'
                  }`}
                >
                  <FileSpreadsheet
                    className={`w-8 h-8 mx-auto mb-2 ${
                      reportType === 'excel' ? 'text-green-600' : 'text-gray-400'
                    }`}
                  />
                  <p
                    className={`font-medium ${
                      reportType === 'excel' ? 'text-green-900' : 'text-gray-700'
                    }`}
                  >
                    Excel
                  </p>
                  <p className="text-xs text-gray-500 mt-1">.xlsx</p>
                </button>

                {/* PDF Option */}
                <button
                  onClick={() => setReportType('pdf')}
                  disabled={downloading}
                  className={`p-4 rounded-lg border-2 transition-all disabled:opacity-50 ${
                    reportType === 'pdf'
                      ? 'border-red-500 bg-red-50'
                      : 'border-gray-200 hover:border-red-300'
                  }`}
                >
                  <FileText
                    className={`w-8 h-8 mx-auto mb-2 ${
                      reportType === 'pdf' ? 'text-red-600' : 'text-gray-400'
                    }`}
                  />
                  <p
                    className={`font-medium ${
                      reportType === 'pdf' ? 'text-red-900' : 'text-gray-700'
                    }`}
                  >
                    PDF
                  </p>
                  <p className="text-xs text-gray-500 mt-1">.pdf</p>
                </button>
              </div>
            </div>

            {/* Report Content Preview */}
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm font-medium text-gray-700 mb-2">리포트 내용</p>
              <ul className="space-y-1 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
                  14개 재무 지표 요약
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
                  최근 12개월 월별 추이
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full" />
                  Top 10 거래처 목록
                </li>
                {reportType === 'excel' && (
                  <li className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                    네이티브 Excel 차트 포함
                  </li>
                )}
                {reportType === 'pdf' && (
                  <li className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-red-500 rounded-full" />
                    한글 폰트 지원
                  </li>
                )}
              </ul>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
            <button
              onClick={onClose}
              disabled={downloading}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
            >
              취소
            </button>
            <button
              onClick={handleDownload}
              disabled={downloading}
              className={`px-6 py-2 text-white rounded-lg transition-all disabled:opacity-50 flex items-center gap-2 ${
                reportType === 'excel'
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-red-600 hover:bg-red-700'
              }`}
            >
              {downloading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  다운로드 중...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  {reportType === 'excel' ? 'Excel' : 'PDF'} 다운로드
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default ReportDownloadModal;

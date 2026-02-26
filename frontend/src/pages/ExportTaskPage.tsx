import React, { useState, useEffect } from 'react';
import {
  Download,
  FileText,
  File,
  Clock,
  CheckCircle,
  XCircle,
  RefreshCw,
  Calendar,
  Filter,
  Plus
} from 'lucide-react';
import * as BillingEnhancedAPI from '../api/billing-enhanced';

interface ExportTask {
  id: number;
  export_type: string;
  file_format: string;
  status: string;
  file_url?: string;
  filters?: any;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

const ExportTaskPage: React.FC = () => {
  const [tasks, setTasks] = useState<ExportTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    export_type: 'INVOICES',
    file_format: 'EXCEL',
    start_date: new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    client_id: undefined as number | undefined
  });

  useEffect(() => {
    loadTasks();
    const interval = setInterval(loadTasks, 10000); // Auto refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const data = await BillingEnhancedAPI.getExportTasks();
      setTasks(data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      const filters: any = {
        start_date: formData.start_date,
        end_date: formData.end_date
      };

      if (formData.client_id) {
        filters.client_id = formData.client_id;
      }

      await BillingEnhancedAPI.createExportTask({
        export_type: formData.export_type,
        file_format: formData.file_format,
        filters
      });

      setShowCreateModal(false);
      loadTasks();
      alert('내보내기 작업이 생성되었습니다. 완료되면 다운로드 버튼이 활성화됩니다.');
    } catch (error) {
      console.error('Failed to create task:', error);
      alert('내보내기 작업 생성에 실패했습니다.');
    }
  };

  const handleDownload = (task: ExportTask) => {
    if (task.file_url) {
      window.open(task.file_url, '_blank');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR');
  };

  const getExportTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      INVOICES: '청구서',
      SETTLEMENTS: '정산서',
      PAYMENTS: '결제 내역',
      FINANCIAL_REPORT: '재무 보고서'
    };
    return labels[type] || type;
  };

  const getFormatIcon = (format: string) => {
    if (format === 'EXCEL') {
      return <FileText className="w-4 h-4 text-green-600" />;
    }
    return <File className="w-4 h-4 text-red-600" />;
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <Clock className="w-3 h-3" />
            대기 중
          </span>
        );
      case 'PROCESSING':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            <RefreshCw className="w-3 h-3 animate-spin" />
            처리 중
          </span>
        );
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3" />
            완료
          </span>
        );
      case 'FAILED':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <XCircle className="w-3 h-3" />
            실패
          </span>
        );
      default:
        return null;
    }
  };

  return (<div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">내보내기 작업 관리</h1>
            <p className="text-gray-600">Excel/PDF 파일 내보내기 및 다운로드</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={loadTasks}
              disabled={loading}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:bg-gray-400 flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              새로고침
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              새 작업
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gray-100 rounded-lg">
                <FileText className="w-6 h-6 text-gray-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">총 작업</p>
                <p className="text-2xl font-bold text-gray-900">{tasks.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <RefreshCw className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">처리 중</p>
                <p className="text-2xl font-bold text-blue-600">
                  {tasks.filter(t => t.status === 'PROCESSING' || t.status === 'PENDING').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">완료</p>
                <p className="text-2xl font-bold text-green-600">
                  {tasks.filter(t => t.status === 'COMPLETED').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-100 rounded-lg">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">실패</p>
                <p className="text-2xl font-bold text-red-600">
                  {tasks.filter(t => t.status === 'FAILED').length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Tasks List */}
        <div className="bg-white rounded-lg shadow">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">유형</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">파일 형식</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">생성 시각</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">완료 시각</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">상태</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">작업</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {tasks.map((task) => (
                  <tr key={task.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                          {getExportTypeLabel(task.export_type)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-1 text-sm">
                        {getFormatIcon(task.file_format)}
                        <span className="font-medium">{task.file_format}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatDate(task.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {task.completed_at ? formatDate(task.completed_at) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(task.status)}
                      {task.status === 'FAILED' && task.error_message && (
                        <p className="text-xs text-red-600 mt-1">{task.error_message}</p>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {task.status === 'COMPLETED' && task.file_url && (
                        <button
                          onClick={() => handleDownload(task)}
                          className="inline-flex items-center gap-1 px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          <Download className="w-4 h-4" />
                          다운로드
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {tasks.length === 0 && !loading && (
            <div className="text-center py-12 text-gray-500">
              내보내기 작업이 없습니다.
            </div>
          )}
        </div>

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Plus className="w-5 h-5" />
                새 내보내기 작업
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">내보내기 유형</label>
                  <select
                    value={formData.export_type}
                    onChange={(e) => setFormData({ ...formData, export_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="INVOICES">청구서</option>
                    <option value="SETTLEMENTS">정산서</option>
                    <option value="PAYMENTS">결제 내역</option>
                    <option value="FINANCIAL_REPORT">재무 보고서</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">파일 형식</label>
                  <select
                    value={formData.file_format}
                    onChange={(e) => setFormData({ ...formData, file_format: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="EXCEL">Excel (.xlsx)</option>
                    <option value="PDF">PDF (.pdf)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">시작일</label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">종료일</label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">거래처 ID (선택)</label>
                  <input
                    type="number"
                    value={formData.client_id || ''}
                    onChange={(e) => setFormData({ ...formData, client_id: e.target.value ? parseInt(e.target.value) : undefined })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="전체 거래처"
                  />
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-sm text-blue-800">
                    💡 파일 생성에는 수 초에서 수 분이 소요될 수 있습니다. 완료되면 다운로드 버튼이 활성화됩니다.
                  </p>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  취소
                </button>
                <button
                  onClick={handleCreate}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  생성
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExportTaskPage;

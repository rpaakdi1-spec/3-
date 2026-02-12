import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import {
import Layout from '../components/common/Layout';
  Calendar,
  Clock,
  Mail,
  Play,
  Pause,
  Trash2,
  Plus,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Edit,
  Save,
  X
} from 'lucide-react';
import * as BillingEnhancedAPI from '../api/billing-enhanced';

interface AutoInvoiceSchedule {
  id: number;
  client_id: number;
  client_name: string;
  billing_cycle: string;
  billing_day: number;
  auto_send_email: boolean;
  is_active: boolean;
  last_executed_at?: string;
  next_execution_at?: string;
  created_at: string;
}

const AutoInvoiceSchedulePage: React.FC = () => {
  const [schedules, setSchedules] = useState<AutoInvoiceSchedule[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    client_id: 0,
    billing_cycle: 'MONTHLY',
    billing_day: 1,
    auto_send_email: true,
    is_active: true
  });

  useEffect(() => {
    loadSchedules();
  }, []);

  const loadSchedules = async () => {
    setLoading(true);
    try {
      const data = await BillingEnhancedAPI.getAutoInvoiceSchedules();
      setSchedules(data);
    } catch (error) {
      console.error('Failed to load schedules:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await BillingEnhancedAPI.createAutoInvoiceSchedule(formData);
      setShowCreateModal(false);
      setFormData({ client_id: 0, billing_cycle: 'MONTHLY', billing_day: 1, auto_send_email: true, is_active: true });
      loadSchedules();
    } catch (error) {
      console.error('Failed to create schedule:', error);
      alert('스케줄 생성에 실패했습니다.');
    }
  };

  const handleToggle = async (id: number, isActive: boolean) => {
    try {
      await BillingEnhancedAPI.updateAutoInvoiceSchedule(id, { is_active: !isActive });
      loadSchedules();
    } catch (error) {
      console.error('Failed to toggle schedule:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    try {
      await BillingEnhancedAPI.deleteAutoInvoiceSchedule(id);
      loadSchedules();
    } catch (error) {
      console.error('Failed to delete schedule:', error);
    }
  };

  const handleExecute = async () => {
    try {
      await BillingEnhancedAPI.executeAutoInvoices();
      alert('자동 청구서 생성이 완료되었습니다.');
      loadSchedules();
    } catch (error) {
      console.error('Failed to execute:', error);
      alert('자동 청구서 생성에 실패했습니다.');
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('ko-KR');
  };

  const getCycleLabel = (cycle: string) => {
    const labels: Record<string, string> = {
      IMMEDIATE: '즉시',
      WEEKLY: '주간',
      MONTHLY: '월간',
      CUSTOM: '사용자 정의'
    };
    return labels[cycle] || cycle;
  };

  return (
    <Layout>
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">자동 청구 스케줄 관리</h1>
            <p className="text-gray-600">거래처별 자동 청구서 생성 스케줄을 설정합니다</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={loadSchedules}
              disabled={loading}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:bg-gray-400 flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              새로고침
            </button>
            <button
              onClick={handleExecute}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              수동 실행
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              스케줄 추가
            </button>
          </div>
        </div>

        {/* Schedules List */}
        <div className="bg-white rounded-lg shadow">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">거래처</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">청구 주기</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">청구일</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">이메일 발송</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">마지막 실행</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">다음 실행</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">상태</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">작업</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {schedules.map((schedule) => (
                  <tr key={schedule.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{schedule.client_name}</div>
                      <div className="text-sm text-gray-500">ID: {schedule.client_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                        {getCycleLabel(schedule.billing_cycle)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {schedule.billing_day}일
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {schedule.auto_send_email ? (
                        <span className="flex items-center gap-1 text-sm text-green-600">
                          <Mail className="w-4 h-4" />
                          자동
                        </span>
                      ) : (
                        <span className="text-sm text-gray-400">수동</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(schedule.last_executed_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(schedule.next_execution_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => handleToggle(schedule.id, schedule.is_active)}
                        className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                          schedule.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {schedule.is_active ? (
                          <>
                            <CheckCircle className="w-3 h-3" />
                            활성
                          </>
                        ) : (
                          <>
                            <Pause className="w-3 h-3" />
                            비활성
                          </>
                        )}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleDelete(schedule.id)}
                        className="text-red-600 hover:text-red-900 ml-2"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {schedules.length === 0 && !loading && (
            <div className="text-center py-12 text-gray-500">
              등록된 자동 청구 스케줄이 없습니다.
            </div>
          )}
        </div>

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
              <h2 className="text-xl font-bold mb-4">자동 청구 스케줄 추가</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">거래처 ID</label>
                  <input
                    type="number"
                    value={formData.client_id || ''}
                    onChange={(e) => setFormData({ ...formData, client_id: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">청구 주기</label>
                  <select
                    value={formData.billing_cycle}
                    onChange={(e) => setFormData({ ...formData, billing_cycle: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="IMMEDIATE">즉시</option>
                    <option value="WEEKLY">주간</option>
                    <option value="MONTHLY">월간</option>
                    <option value="CUSTOM">사용자 정의</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">청구일</label>
                  <input
                    type="number"
                    min="1"
                    max="31"
                    value={formData.billing_day}
                    onChange={(e) => setFormData({ ...formData, billing_day: parseInt(e.target.value) || 1 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.auto_send_email}
                    onChange={(e) => setFormData({ ...formData, auto_send_email: e.target.checked })}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label className="text-sm text-gray-700">이메일 자동 발송</label>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label className="text-sm text-gray-700">활성화</label>
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
    </Layout>
  );
};

export default AutoInvoiceSchedulePage;

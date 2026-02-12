import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import {
import Layout from '../components/common/Layout';
  Bell,
  Mail,
  MessageSquare,
  Send,
  RefreshCw,
  Calendar,
  CheckCircle,
  XCircle,
  Clock,
  Plus,
  Trash2
} from 'lucide-react';
import * as BillingEnhancedAPI from '../api/billing-enhanced';

interface PaymentReminder {
  id: number;
  invoice_id: number;
  invoice_number: string;
  client_name: string;
  reminder_type: string;
  channel: string;
  scheduled_at: string;
  sent_at?: string;
  status: string;
  message?: string;
}

const PaymentReminderPage: React.FC = () => {
  const [reminders, setReminders] = useState<PaymentReminder[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    invoice_id: 0,
    reminder_type: 'DUE_DATE',
    channel: 'EMAIL',
    scheduled_at: new Date().toISOString().split('T')[0],
    message: ''
  });

  useEffect(() => {
    loadReminders();
  }, []);

  const loadReminders = async () => {
    setLoading(true);
    try {
      const data = await BillingEnhancedAPI.getPaymentReminders();
      setReminders(data);
    } catch (error) {
      console.error('Failed to load reminders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await BillingEnhancedAPI.createPaymentReminder(formData);
      setShowCreateModal(false);
      setFormData({
        invoice_id: 0,
        reminder_type: 'DUE_DATE',
        channel: 'EMAIL',
        scheduled_at: new Date().toISOString().split('T')[0],
        message: ''
      });
      loadReminders();
      alert('결제 알림이 생성되었습니다.');
    } catch (error) {
      console.error('Failed to create reminder:', error);
      alert('알림 생성에 실패했습니다.');
    }
  };

  const handleSendDue = async () => {
    if (!confirm('납기일 도래 알림을 일괄 발송하시겠습니까?')) return;

    try {
      await BillingEnhancedAPI.sendDuePaymentReminders();
      alert('납기일 알림이 발송되었습니다.');
      loadReminders();
    } catch (error) {
      console.error('Failed to send reminders:', error);
      alert('알림 발송에 실패했습니다.');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await BillingEnhancedAPI.deletePaymentReminder(id);
      loadReminders();
    } catch (error) {
      console.error('Failed to delete reminder:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR');
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'EMAIL':
        return <Mail className="w-4 h-4" />;
      case 'SMS':
        return <MessageSquare className="w-4 h-4" />;
      case 'PUSH':
        return <Bell className="w-4 h-4" />;
      default:
        return <Bell className="w-4 h-4" />;
    }
  };

  const getChannelLabel = (channel: string) => {
    const labels: Record<string, string> = {
      EMAIL: '이메일',
      SMS: 'SMS',
      PUSH: '푸시 알림'
    };
    return labels[channel] || channel;
  };

  const getReminderTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      DUE_DATE: '납기일',
      OVERDUE: '연체',
      FOLLOW_UP: '후속',
      CUSTOM: '사용자 정의'
    };
    return labels[type] || type;
  };

  const getStatusBadge = (status: string, sentAt?: string) => {
    if (status === 'SENT' && sentAt) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <CheckCircle className="w-3 h-3" />
          발송됨
        </span>
      );
    }

    if (status === 'FAILED') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <XCircle className="w-3 h-3" />
          실패
        </span>
      );
    }

    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
        <Clock className="w-3 h-3" />
        대기 중
      </span>
    );
  };

  return (
    <Layout>
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">결제 알림 관리</h1>
            <p className="text-gray-600">자동 결제 알림 발송 및 관리</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={loadReminders}
              disabled={loading}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:bg-gray-400 flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              새로고침
            </button>
            <button
              onClick={handleSendDue}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              납기일 알림 발송
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              알림 추가
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Bell className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">총 알림</p>
                <p className="text-2xl font-bold text-gray-900">{reminders.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">발송 완료</p>
                <p className="text-2xl font-bold text-green-600">
                  {reminders.filter(r => r.status === 'SENT').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <Clock className="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">대기 중</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {reminders.filter(r => r.status === 'PENDING').length}
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
                  {reminders.filter(r => r.status === 'FAILED').length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Reminders List */}
        <div className="bg-white rounded-lg shadow">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">청구서</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">거래처</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">알림 유형</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">채널</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">예정일</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">발송일</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">상태</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">작업</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {reminders.map((reminder) => (
                  <tr key={reminder.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {reminder.invoice_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {reminder.client_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                        {getReminderTypeLabel(reminder.reminder_type)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="flex items-center gap-1 text-sm text-gray-900">
                        {getChannelIcon(reminder.channel)}
                        {getChannelLabel(reminder.channel)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatDate(reminder.scheduled_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {reminder.sent_at ? formatDate(reminder.sent_at) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(reminder.status, reminder.sent_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {reminder.status === 'PENDING' && (
                        <button
                          onClick={() => handleDelete(reminder.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {reminders.length === 0 && !loading && (
            <div className="text-center py-12 text-gray-500">
              등록된 결제 알림이 없습니다.
            </div>
          )}
        </div>

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
              <h2 className="text-xl font-bold mb-4">결제 알림 추가</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">청구서 ID</label>
                  <input
                    type="number"
                    value={formData.invoice_id || ''}
                    onChange={(e) => setFormData({ ...formData, invoice_id: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">알림 유형</label>
                  <select
                    value={formData.reminder_type}
                    onChange={(e) => setFormData({ ...formData, reminder_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="DUE_DATE">납기일</option>
                    <option value="OVERDUE">연체</option>
                    <option value="FOLLOW_UP">후속</option>
                    <option value="CUSTOM">사용자 정의</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">발송 채널</label>
                  <select
                    value={formData.channel}
                    onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="EMAIL">이메일</option>
                    <option value="SMS">SMS</option>
                    <option value="PUSH">푸시 알림</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">발송 예정일</label>
                  <input
                    type="date"
                    value={formData.scheduled_at}
                    onChange={(e) => setFormData({ ...formData, scheduled_at: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">메시지 (선택)</label>
                  <textarea
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="알림 메시지를 입력하세요..."
                  />
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

export default PaymentReminderPage;

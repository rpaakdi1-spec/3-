import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import {
  CheckCircle,
  XCircle,
  Clock,
  User,
  MessageSquare,
  History,
  RefreshCw,
  AlertCircle,
  ThumbsUp,
  ThumbsDown,
  FileText
} from 'lucide-react';
import * as BillingEnhancedAPI from '../api/billing-enhanced';

interface SettlementApproval {
  id: number;
  settlement_id: number;
  settlement_number: string;
  driver_name: string;
  net_amount: number;
  status: string;
  requested_at: string;
  reviewed_by?: string;
  reviewed_at?: string;
  comments?: string;
}

interface ApprovalHistory {
  id: number;
  action: string;
  performed_by: string;
  performed_at: string;
  comments?: string;
}

const SettlementApprovalPage: React.FC = () => {
  const [approvals, setApprovals] = useState<SettlementApproval[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [history, setHistory] = useState<ApprovalHistory[]>([]);
  const [loading, setLoading] = useState(false);
  const [comment, setComment] = useState('');
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  useEffect(() => {
    loadApprovals();
  }, []);

  const loadApprovals = async () => {
    setLoading(true);
    try {
      const data = await BillingEnhancedAPI.getSettlementApprovals();
      setApprovals(data);
    } catch (error) {
      console.error('Failed to load approvals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (settlementId: number) => {
    if (!comment.trim()) {
      alert('승인 코멘트를 입력해주세요.');
      return;
    }

    try {
      await BillingEnhancedAPI.approveSettlement(settlementId, comment);
      alert('정산이 승인되었습니다.');
      setComment('');
      setSelectedId(null);
      loadApprovals();
    } catch (error) {
      console.error('Failed to approve:', error);
      alert('승인에 실패했습니다.');
    }
  };

  const handleReject = async (settlementId: number) => {
    if (!comment.trim()) {
      alert('반려 사유를 입력해주세요.');
      return;
    }

    try {
      await BillingEnhancedAPI.rejectSettlement(settlementId, comment);
      alert('정산이 반려되었습니다.');
      setComment('');
      setSelectedId(null);
      loadApprovals();
    } catch (error) {
      console.error('Failed to reject:', error);
      alert('반려에 실패했습니다.');
    }
  };

  const loadHistory = async (settlementId: number) => {
    try {
      const data = await BillingEnhancedAPI.getSettlementApprovalHistory(settlementId);
      setHistory(data);
      setShowHistoryModal(true);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR');
  };

  const getStatusBadge = (status: string) => {
    const configs: Record<string, { label: string; color: string; icon: JSX.Element }> = {
      PENDING: { label: '승인 대기', color: 'bg-yellow-100 text-yellow-800', icon: <Clock className="w-4 h-4" /> },
      APPROVED: { label: '승인됨', color: 'bg-green-100 text-green-800', icon: <CheckCircle className="w-4 h-4" /> },
      REJECTED: { label: '반려됨', color: 'bg-red-100 text-red-800', icon: <XCircle className="w-4 h-4" /> }
    };

    const config = configs[status] || configs.PENDING;

    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
        {config.icon}
        {config.label}
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">정산 승인 관리</h1>
            <p className="text-gray-600">기사 정산 승인 및 반려 처리</p>
          </div>
          <button
            onClick={loadApprovals}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            새로고침
          </button>
        </div>

        {/* Approvals List */}
        <div className="grid grid-cols-1 gap-4">
          {approvals.map((approval) => (
            <div key={approval.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {approval.settlement_number}
                  </h3>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      <User className="w-4 h-4" />
                      {approval.driver_name}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {formatDate(approval.requested_at)}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  {getStatusBadge(approval.status)}
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    {formatCurrency(approval.net_amount)}
                  </p>
                </div>
              </div>

              {approval.status === 'PENDING' && (
                <div className="border-t border-gray-200 pt-4">
                  {selectedId === approval.settlement_id ? (
                    <div className="space-y-3">
                      <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="승인/반려 코멘트를 입력하세요..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        rows={3}
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleApprove(approval.settlement_id)}
                          className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                        >
                          <ThumbsUp className="w-4 h-4" />
                          승인
                        </button>
                        <button
                          onClick={() => handleReject(approval.settlement_id)}
                          className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center gap-2"
                        >
                          <ThumbsDown className="w-4 h-4" />
                          반려
                        </button>
                        <button
                          onClick={() => {
                            setSelectedId(null);
                            setComment('');
                          }}
                          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          취소
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => setSelectedId(approval.settlement_id)}
                      className="w-full px-4 py-2 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium"
                    >
                      검토하기
                    </button>
                  )}
                </div>
              )}

              {approval.status !== 'PENDING' && (
                <div className="border-t border-gray-200 pt-4">
                  <div className="flex items-start gap-2 text-sm">
                    <MessageSquare className="w-4 h-4 text-gray-400 mt-0.5" />
                    <div>
                      <p className="text-gray-600">
                        {approval.reviewed_by} - {formatDate(approval.reviewed_at!)}
                      </p>
                      {approval.comments && (
                        <p className="text-gray-900 mt-1">{approval.comments}</p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-4">
                <button
                  onClick={() => loadHistory(approval.settlement_id)}
                  className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                >
                  <History className="w-4 h-4" />
                  승인 이력 보기
                </button>
              </div>
            </div>
          ))}
        </div>

        {approvals.length === 0 && !loading && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">승인 대기 중인 정산이 없습니다.</p>
          </div>
        )}

        {/* History Modal */}
        {showHistoryModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <History className="w-5 h-5" />
                승인 이력
              </h2>

              <div className="space-y-4">
                {history.map((item) => (
                  <div key={item.id} className="border-l-4 border-blue-500 pl-4 py-2">
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                      <span className="font-medium">{item.performed_by}</span>
                      <span>•</span>
                      <span>{formatDate(item.performed_at)}</span>
                    </div>
                    <p className="text-sm font-medium text-gray-900">{item.action}</p>
                    {item.comments && (
                      <p className="text-sm text-gray-600 mt-1">{item.comments}</p>
                    )}
                  </div>
                ))}
              </div>

              <button
                onClick={() => setShowHistoryModal(false)}
                className="mt-6 w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                닫기
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
    </Layout>
  );
};

export default SettlementApprovalPage;

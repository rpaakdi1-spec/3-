import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
import {
  Calendar,
  DollarSign,
  FileText,
  Send,
  Download,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Filter,
  Search,
  RefreshCw,
  Mail,
  CreditCard,
  User
} from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

interface Invoice {
  id: number;
  invoice_number: string;
  client: {
    id: number;
    name: string;
    code: string;
  };
  billing_period_start: string;
  billing_period_end: string;
  issue_date: string;
  due_date: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  paid_amount: number;
  status: string;
  sent_at?: string;
  paid_date?: string;
  line_items?: InvoiceLineItem[];
}

interface InvoiceLineItem {
  id: number;
  description: string;
  quantity: number;
  unit_price: number;
  amount: number;
  distance_km?: number;
  surcharge_amount?: number;
  discount_amount?: number;
}

interface Payment {
  id: number;
  payment_number: string;
  amount: number;
  payment_method: string;
  payment_date: string;
  reference_number?: string;
}

interface DriverSettlement {
  id: number;
  settlement_number: string;
  driver: {
    id: number;
    name: string;
    code: string;
  };
  settlement_period_start: string;
  settlement_period_end: string;
  total_revenue: number;
  commission_amount: number;
  expense_amount: number;
  net_amount: number;
  dispatch_count: number;
  is_paid: boolean;
  paid_date?: string;
}

interface BillingSummary {
  total_invoices: number;
  total_amount: number;
  paid_amount: number;
  outstanding_amount: number;
  payment_rate: number;
  status_breakdown: {
    [key: string]: number;
  };
}

const BillingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'invoices' | 'payments' | 'settlements'>('invoices');
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [settlements, setSettlements] = useState<DriverSettlement[]>([]);
  const [summary, setSummary] = useState<BillingSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    loadData();
  }, [activeTab, dateRange]);

  const loadData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      if (activeTab === 'invoices') {
        // Load invoices
        const invoicesRes = await axios.get(`${API_URL}/billing/invoices`, {
          headers,
          params: { limit: 100 }
        });
        setInvoices(invoicesRes.data);

        // Load summary
        const summaryRes = await axios.get(`${API_URL}/billing/invoices/summary`, {
          headers,
          params: {
            start_date: dateRange.start,
            end_date: dateRange.end
          }
        });
        setSummary(summaryRes.data);
      } else if (activeTab === 'settlements') {
        // Load driver settlements
        const settlementsRes = await axios.get(`${API_URL}/billing/settlements`, {
          headers,
          params: { limit: 100 }
        });
        setSettlements(settlementsRes.data);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInvoice = async (clientId: number) => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_URL}/billing/invoices/generate`,
        {
          client_id: clientId,
          start_date: dateRange.start,
          end_date: dateRange.end,
          auto_send: false
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('청구서가 생성되었습니다.');
      loadData();
    } catch (error) {
      console.error('Failed to generate invoice:', error);
      alert('청구서 생성에 실패했습니다.');
    }
  };

  const handleSendInvoice = async (invoiceId: number) => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_URL}/billing/invoices/${invoiceId}/send`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('청구서가 발송되었습니다.');
      loadData();
    } catch (error) {
      console.error('Failed to send invoice:', error);
      alert('청구서 발송에 실패했습니다.');
    }
  };

  const handleDownloadPDF = async (invoiceId: number, invoiceNumber: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `${API_URL}/billing/invoices/${invoiceId}/pdf`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${invoiceNumber}.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download PDF:', error);
      alert('PDF 다운로드에 실패했습니다.');
    }
  };

  const handleRecordPayment = async (invoiceId: number) => {
    const amount = prompt('결제 금액을 입력하세요:');
    if (!amount) return;

    const paymentDate = prompt('결제 날짜 (YYYY-MM-DD):', new Date().toISOString().split('T')[0]);
    if (!paymentDate) return;

    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_URL}/billing/payments`,
        {
          invoice_id: invoiceId,
          amount: parseFloat(amount),
          payment_method: 'TRANSFER',
          payment_date: paymentDate
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('결제가 기록되었습니다.');
      loadData();
    } catch (error) {
      console.error('Failed to record payment:', error);
      alert('결제 기록에 실패했습니다.');
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; color: string; icon: JSX.Element }> = {
      DRAFT: { label: '초안', color: 'bg-gray-100 text-gray-800', icon: <FileText className="w-3 h-3" /> },
      PENDING: { label: '대기', color: 'bg-yellow-100 text-yellow-800', icon: <Clock className="w-3 h-3" /> },
      SENT: { label: '발송됨', color: 'bg-blue-100 text-blue-800', icon: <Send className="w-3 h-3" /> },
      PARTIAL: { label: '부분결제', color: 'bg-orange-100 text-orange-800', icon: <DollarSign className="w-3 h-3" /> },
      PAID: { label: '결제완료', color: 'bg-green-100 text-green-800', icon: <CheckCircle className="w-3 h-3" /> },
      OVERDUE: { label: '연체', color: 'bg-red-100 text-red-800', icon: <AlertTriangle className="w-3 h-3" /> },
      CANCELLED: { label: '취소', color: 'bg-gray-100 text-gray-600', icon: <FileText className="w-3 h-3" /> }
    };

    const config = statusConfig[status] || statusConfig.DRAFT;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        {config.icon}
        {config.label}
      </span>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  const filteredInvoices = invoices.filter(invoice => {
    const matchesSearch = 
      invoice.invoice_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      invoice.client.name.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || invoice.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const filteredSettlements = settlements.filter(settlement => {
    const matchesSearch = 
      settlement.settlement_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      settlement.driver.name.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesSearch;
  });

  return (
    <Layout>
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">청구/정산 관리</h1>
          <p className="text-gray-600">거래처 청구서 및 기사 정산 자동화</p>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">총 청구액</span>
                <FileText className="w-5 h-5 text-blue-500" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(summary.total_amount)}</p>
              <p className="text-xs text-gray-500 mt-1">{summary.total_invoices}건</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">결제 완료</span>
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(summary.paid_amount)}</p>
              <p className="text-xs text-gray-500 mt-1">{summary.payment_rate.toFixed(1)}% 회수율</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">미수금</span>
                <AlertTriangle className="w-5 h-5 text-orange-500" />
              </div>
              <p className="text-2xl font-bold text-orange-600">{formatCurrency(summary.outstanding_amount)}</p>
              <p className="text-xs text-gray-500 mt-1">
                {summary.status_breakdown.OVERDUE || 0}건 연체
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">청구서 발송</span>
                <Send className="w-5 h-5 text-purple-500" />
              </div>
              <p className="text-2xl font-bold text-purple-600">
                {summary.status_breakdown.SENT || 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">대기 중</p>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('invoices')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'invoices'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  거래처 청구서
                </div>
              </button>
              <button
                onClick={() => setActiveTab('payments')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'payments'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <CreditCard className="w-4 h-4" />
                  결제 내역
                </div>
              </button>
              <button
                onClick={() => setActiveTab('settlements')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'settlements'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4" />
                  기사 정산
                </div>
              </button>
            </nav>
          </div>

          {/* Filters */}
          <div className="p-4 border-b border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="검색..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {activeTab === 'invoices' && (
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">전체 상태</option>
                  <option value="DRAFT">초안</option>
                  <option value="PENDING">대기</option>
                  <option value="SENT">발송됨</option>
                  <option value="PARTIAL">부분결제</option>
                  <option value="PAID">결제완료</option>
                  <option value="OVERDUE">연체</option>
                </select>
              )}

              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />

              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />

              <button
                onClick={loadData}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                새로고침
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {activeTab === 'invoices' && (
              <div className="space-y-4">
                {filteredInvoices.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    청구서가 없습니다.
                  </div>
                ) : (
                  filteredInvoices.map((invoice) => (
                    <div key={invoice.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{invoice.invoice_number}</h3>
                          <p className="text-sm text-gray-600 mt-1">{invoice.client.name}</p>
                          <p className="text-xs text-gray-500">
                            청구 기간: {invoice.billing_period_start} ~ {invoice.billing_period_end}
                          </p>
                        </div>
                        <div className="text-right">
                          {getStatusBadge(invoice.status)}
                          <p className="text-2xl font-bold text-gray-900 mt-2">
                            {formatCurrency(invoice.total_amount)}
                          </p>
                          {invoice.paid_amount > 0 && (
                            <p className="text-sm text-green-600">
                              결제: {formatCurrency(invoice.paid_amount)}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                        <div>
                          <span className="text-gray-500">발행일:</span>
                          <span className="ml-2 text-gray-900">{invoice.issue_date}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">납기일:</span>
                          <span className="ml-2 text-gray-900 font-medium">{invoice.due_date}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">소계:</span>
                          <span className="ml-2 text-gray-900">{formatCurrency(invoice.subtotal)}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">부가세:</span>
                          <span className="ml-2 text-gray-900">{formatCurrency(invoice.tax_amount)}</span>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={() => handleDownloadPDF(invoice.id, invoice.invoice_number)}
                          className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors flex items-center gap-1"
                        >
                          <Download className="w-4 h-4" />
                          PDF
                        </button>
                        
                        {invoice.status !== 'PAID' && invoice.status !== 'CANCELLED' && (
                          <>
                            <button
                              onClick={() => handleSendInvoice(invoice.id)}
                              className="px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors flex items-center gap-1"
                            >
                              <Mail className="w-4 h-4" />
                              이메일 발송
                            </button>
                            
                            <button
                              onClick={() => handleRecordPayment(invoice.id)}
                              className="px-3 py-1.5 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors flex items-center gap-1"
                            >
                              <DollarSign className="w-4 h-4" />
                              결제 기록
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'settlements' && (
              <div className="space-y-4">
                {filteredSettlements.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    정산 내역이 없습니다.
                  </div>
                ) : (
                  filteredSettlements.map((settlement) => (
                    <div key={settlement.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{settlement.settlement_number}</h3>
                          <p className="text-sm text-gray-600 mt-1">{settlement.driver.name} 기사</p>
                          <p className="text-xs text-gray-500">
                            정산 기간: {settlement.settlement_period_start} ~ {settlement.settlement_period_end}
                          </p>
                        </div>
                        <div className="text-right">
                          <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${
                            settlement.is_paid 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {settlement.is_paid ? (
                              <>
                                <CheckCircle className="w-3 h-3" />
                                지급완료
                              </>
                            ) : (
                              <>
                                <Clock className="w-3 h-3" />
                                미지급
                              </>
                            )}
                          </span>
                          <p className="text-2xl font-bold text-gray-900 mt-2">
                            {formatCurrency(settlement.net_amount)}
                          </p>
                          <p className="text-sm text-gray-500">순액</p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">총 매출:</span>
                          <span className="ml-2 text-gray-900">{formatCurrency(settlement.total_revenue)}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">수수료:</span>
                          <span className="ml-2 text-red-600">-{formatCurrency(settlement.commission_amount)}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">배차 건수:</span>
                          <span className="ml-2 text-gray-900">{settlement.dispatch_count}건</span>
                        </div>
                        <div>
                          <span className="text-gray-500">
                            {settlement.is_paid ? '지급일:' : '정산 대기'}
                          </span>
                          <span className="ml-2 text-gray-900">
                            {settlement.paid_date || '-'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
    </Layout>
  );
};

export default BillingPage;

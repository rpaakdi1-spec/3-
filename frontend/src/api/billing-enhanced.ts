/**
 * Phase 8: Billing Enhanced API Client
 * 재무/청구/정산 시스템 강화 API
 */

import axios from 'axios';

const API_BASE_URL = '/api/v1/billing/enhanced';

// Get auth token
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    headers: {
      Authorization: `Bearer ${token}`
    }
  };
};

// Create axios instance with auth interceptor
const apiClient = axios.create();

// Add auth header to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ============= Types =============

export interface ChargePreviewRequest {
  client_id: number;
  dispatch_date: string; // YYYY-MM-DD
  total_distance_km: number;
  pallets: number;
  weight_kg?: number;
  vehicle_type?: string;
  is_urgent: boolean;
}

export interface ChargeBreakdown {
  base_distance_charge: number;
  base_pallet_charge: number;
  base_weight_charge: number;
  subtotal: number;
  weekend_surcharge: number;
  night_surcharge: number;
  express_surcharge: number;
  temperature_control_charge: number;
  total_surcharge: number;
  volume_discount: number;
  special_discount: number;
  total_discount: number;
  subtotal_after_discount: number;
  tax_amount: number;
  total_amount: number;
}

export interface ChargePreviewResponse {
  client_id: number;
  dispatch_date: string;
  breakdown: ChargeBreakdown;
  policy_info: Record<string, any>;
  notes: string[];
}

export interface FinancialSummary {
  period_start: string;
  period_end: string;
  total_revenue: number;
  invoiced_amount: number;
  collected_amount: number;
  collection_rate: number;
  total_receivables: number;
  current_receivables: number;
  overdue_receivables: number;
  overdue_count: number;
  total_settlements: number;
  pending_settlements: number;
  paid_settlements: number;
  cash_in: number;
  cash_out: number;
  net_cash_flow: number;
}

export interface MonthlyTrend {
  month: string; // YYYY-MM
  revenue: number;
  collected: number;
  settlements: number;
  net_profit: number;
}

export interface TopClient {
  client_id: number;
  client_name: string;
  total_revenue: number;
  invoice_count: number;
  collection_rate: number;
}

export interface AutoInvoiceSchedule {
  id: number;
  client_id: number;
  enabled: boolean;
  billing_day: number;
  auto_send_email: boolean;
  send_reminder: boolean;
  reminder_days: number[];
  last_generated_at?: string;
  next_generation_date?: string;
  created_at: string;
  updated_at: string;
}

export interface AutoInvoiceScheduleRequest {
  client_id: number;
  enabled: boolean;
  billing_day: number;
  auto_send_email: boolean;
  send_reminder: boolean;
  reminder_days: number[];
}

export interface SettlementApproval {
  settlement_id: number;
  status: string;
  approved_by?: number;
  approved_at?: string;
  approval_notes?: string;
}

export interface SettlementApprovalRequest {
  settlement_id: number;
  action: 'approve' | 'reject';
  notes?: string;
}

export interface SettlementApprovalHistory {
  id: number;
  settlement_id: number;
  action: string;
  actor_id?: number;
  actor_name?: string;
  notes?: string;
  created_at: string;
}

export interface BillingStatistics {
  period_start: string;
  period_end: string;
  total_invoices: number;
  total_amount: number;
  average_amount: number;
  by_status: Record<string, { count: number; amount: number }>;
  collection_efficiency: number;
}

export interface SettlementStatistics {
  period_start: string;
  period_end: string;
  total_settlements: number;
  total_amount: number;
  average_amount: number;
  approved_count: number;
  approval_rate: number;
}

export interface ExportRequest {
  invoice_ids?: number[];
  start_date?: string;
  end_date?: string;
  client_id?: number;
  status?: string;
  format: 'excel' | 'pdf';
  include_details: boolean;
}

export interface ExportTask {
  task_id: string;
  status: string;
  file_url?: string;
  created_at: string;
}

// ============= API Functions =============

/**
 * 요금 미리보기 - 실시간 요금 계산
 */
export const previewCharge = async (
  request: ChargePreviewRequest
): Promise<ChargePreviewResponse> => {
  const response = await apiClient.post<ChargePreviewResponse>(
    `${API_BASE_URL}/preview`,
    request
  );
  return response.data;
};

/**
 * 재무 대시보드 - 요약 정보
 */
export const getFinancialSummary = async (
  startDate?: string,
  endDate?: string
): Promise<FinancialSummary> => {
  const params: Record<string, string> = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;

  const response = await apiClient.get<FinancialSummary>(
    `${API_BASE_URL}/dashboard/financial`,
    { params }
  );
  return response.data;
};

/**
 * 월별 추이 조회
 */
export const getMonthlyTrends = async (
  startDate?: string,
  endDate?: string,
  months: number = 12
): Promise<MonthlyTrend[]> => {
  const params: Record<string, any> = { months };
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;

  const response = await apiClient.get<MonthlyTrend[]>(
    `${API_BASE_URL}/dashboard/trends`,
    { params }
  );
  return response.data;
};

/**
 * 주요 고객 순위
 */
export const getTopClients = async (
  startDate?: string,
  endDate?: string,
  limit: number = 10
): Promise<TopClient[]> => {
  const params: Record<string, any> = { limit };
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;

  const response = await apiClient.get<TopClient[]>(
    `${API_BASE_URL}/dashboard/top-clients`,
    { params }
  );
  return response.data;
};

/**
 * 재무 대시보드 데이터 조회 (getFinancialDashboard alias)
 */
export const getFinancialDashboard = getFinancialSummary;

/**
 * 자동 청구 스케줄 생성
 */
export const createAutoInvoiceSchedule = async (
  request: AutoInvoiceScheduleRequest
): Promise<AutoInvoiceSchedule> => {
  const response = await apiClient.post<AutoInvoiceSchedule>(
    `${API_BASE_URL}/auto-schedule`,
    request
  );
  return response.data;
};

/**
 * 자동 청구 스케줄 목록 조회
 */
export const getAutoInvoiceSchedules = async (
  enabled?: boolean
): Promise<AutoInvoiceSchedule[]> => {
  const params: Record<string, any> = {};
  if (enabled !== undefined) params.enabled = enabled;

  const response = await apiClient.get<AutoInvoiceSchedule[]>(
    `${API_BASE_URL}/auto-schedule`,
    { params }
  );
  return response.data;
};

/**
 * 고객별 자동 청구 스케줄 조회
 */
export const getAutoInvoiceSchedule = async (
  clientId: number
): Promise<AutoInvoiceSchedule> => {
  const response = await apiClient.get<AutoInvoiceSchedule>(
    `${API_BASE_URL}/auto-schedule/${clientId}`
  );
  return response.data;
};

/**
 * 자동 청구 스케줄 생성/수정
 */
export const createOrUpdateAutoInvoiceSchedule = async (
  request: AutoInvoiceScheduleRequest
): Promise<AutoInvoiceSchedule> => {
  const response = await apiClient.post<AutoInvoiceSchedule>(
    `${API_BASE_URL}/auto-schedule`,
    request
  );
  return response.data;
};

/**
 * 정산 승인/반려 처리
 */
export const processSettlementApproval = async (
  request: SettlementApprovalRequest
): Promise<SettlementApproval> => {
  const response = await apiClient.post<SettlementApproval>(
    `${API_BASE_URL}/settlement-approval`,
    request
  );
  return response.data;
};

/**
 * 정산 승인 상태 조회
 */
export const getSettlementApproval = async (
  settlementId: number
): Promise<SettlementApproval> => {
  const response = await apiClient.get<SettlementApproval>(
    `${API_BASE_URL}/settlement-approval/${settlementId}`
  );
  return response.data;
};

/**
 * 정산 승인 이력 조회
 */
export const getSettlementApprovalHistory = async (
  settlementId: number
): Promise<SettlementApprovalHistory[]> => {
  const response = await apiClient.get<{ settlement_id: number; history: SettlementApprovalHistory[] }>(
    `${API_BASE_URL}/settlement-approval/${settlementId}/history`
  );
  return response.data.history;
};

/**
 * 청구 통계
 */
export const getBillingStatistics = async (
  startDate?: string,
  endDate?: string
): Promise<BillingStatistics> => {
  const params: Record<string, string> = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;

  const response = await apiClient.get<BillingStatistics>(
    `${API_BASE_URL}/statistics/billing`,
    { params }
  );
  return response.data;
};

/**
 * 정산 통계
 */
export const getSettlementStatistics = async (
  startDate?: string,
  endDate?: string
): Promise<SettlementStatistics> => {
  const params: Record<string, string> = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;

  const response = await apiClient.get<SettlementStatistics>(
    `${API_BASE_URL}/statistics/settlement`,
    { params }
  );
  return response.data;
};

/**
 * 내보내기 작업 생성
 */
export const createExportTask = async (
  request: ExportRequest
): Promise<ExportTask> => {
  const response = await apiClient.post<ExportTask>(
    `${API_BASE_URL}/export`,
    request
  );
  return response.data;
};

/**
 * 내보내기 작업 상태 조회
 */
export const getExportTask = async (taskId: string): Promise<ExportTask> => {
  const response = await apiClient.get<ExportTask>(
    `${API_BASE_URL}/export/${taskId}`
  );
  return response.data;
};

// ============= Utility Functions =============

/**
 * 금액 포맷팅 (원화)
 */
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
  }).format(amount);
};

/**
 * 퍼센트 포맷팅
 */
export const formatPercent = (value: number): string => {
  return `${value.toFixed(1)}%`;
};

/**
 * 날짜 포맷팅
 */
export const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

/**
 * 기간 텍스트 생성
 */
export const getPeriodText = (startDate: string, endDate: string): string => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  if (start.getFullYear() === end.getFullYear() && start.getMonth() === end.getMonth()) {
    return start.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
    });
  }
  
  return `${formatDate(startDate)} ~ ${formatDate(endDate)}`;
};

/**
 * 이번 달 시작일/종료일
 */
export const getCurrentMonthDates = (): { startDate: string; endDate: string } => {
  const now = new Date();
  const startDate = new Date(now.getFullYear(), now.getMonth(), 1);
  const endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0);
  
  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  };
};

/**
 * 지난 달 시작일/종료일
 */
export const getLastMonthDates = (): { startDate: string; endDate: string } => {
  const now = new Date();
  const startDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
  const endDate = new Date(now.getFullYear(), now.getMonth(), 0);
  
  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  };
};

/**
 * 최근 N개월 시작일/종료일
 */
export const getLastNMonthsDates = (months: number): { startDate: string; endDate: string } => {
  const now = new Date();
  const endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0);
  const startDate = new Date(now.getFullYear(), now.getMonth() - months + 1, 1);
  
  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  };
};

// ============= Additional Helper Functions =============

/**
 * Execute due auto invoices
 */
export const executeAutoInvoices = async (): Promise<{ scheduled: number; executed: number; failed: number }> => {
  const response = await apiClient.post<{ scheduled: number; executed: number; failed: number }>(
    `${API_BASE_URL}/auto-schedule/execute-due`
  );
  return response.data;
};

/**
 * Get settlement approvals list
 */
export const getSettlementApprovals = async (
  status?: string
): Promise<SettlementApproval[]> => {
  const params: Record<string, any> = {};
  if (status) params.status = status;

  const response = await apiClient.get<SettlementApproval[]>(
    `${API_BASE_URL}/settlement-approval`,
    { params }
  );
  return response.data;
};

/**
 * Approve settlement
 */
export const approveSettlement = async (
  settlementId: number, 
  comments: string
): Promise<SettlementApproval> => {
  const response = await apiClient.post<SettlementApproval>(
    `${API_BASE_URL}/settlement-approval/${settlementId}/approve`,
    { comments }
  );
  return response.data;
};

/**
 * Reject settlement
 */
export const rejectSettlement = async (
  settlementId: number, 
  comments: string
): Promise<SettlementApproval> => {
  const response = await apiClient.post<SettlementApproval>(
    `${API_BASE_URL}/settlement-approval/${settlementId}/reject`,
    { comments }
  );
  return response.data;
};

/**
 * Get payment reminders
 */
export const getPaymentReminders = async (
  status?: string
): Promise<any[]> => {
  const params: Record<string, any> = {};
  if (status) params.status = status;

  const response = await apiClient.get<any[]>(
    `${API_BASE_URL}/payment-reminder`,
    { params }
  );
  return response.data;
};

/**
 * Create payment reminder
 */
export const createPaymentReminder = async (data: any): Promise<any> => {
  const response = await apiClient.post(`${API_BASE_URL}/payment-reminder`, data);
  return response.data;
};

/**
 * Send due payment reminders
 */
export const sendDuePaymentReminders = async (): Promise<{ sent: number; failed: number }> => {
  const response = await apiClient.post<{ sent: number; failed: number }>(
    `${API_BASE_URL}/payment-reminder/send-due`
  );
  return response.data;
};

/**
 * Delete payment reminder
 */
export const deletePaymentReminder = async (reminderId: number): Promise<void> => {
  await apiClient.delete(`${API_BASE_URL}/payment-reminder/${reminderId}`);
};

/**
 * Get export tasks list
 */
export const getExportTasks = async (
  status?: string
): Promise<ExportTask[]> => {
  const params: Record<string, any> = {};
  if (status) params.status = status;

  const response = await apiClient.get<ExportTask[]>(
    `${API_BASE_URL}/export`,
    { params }
  );
  return response.data;
};

/**
 * Update or create auto invoice schedule
 */
export const updateAutoInvoiceSchedule = async (
  scheduleId: number, 
  data: Partial<AutoInvoiceScheduleRequest>
): Promise<AutoInvoiceSchedule> => {
  const response = await apiClient.put<AutoInvoiceSchedule>(
    `${API_BASE_URL}/auto-schedule/${scheduleId}`,
    data
  );
  return response.data;
};

/**
 * Delete auto invoice schedule
 */
export const deleteAutoInvoiceSchedule = async (scheduleId: number): Promise<void> => {
  await apiClient.delete(`${API_BASE_URL}/auto-schedule/${scheduleId}`);
};


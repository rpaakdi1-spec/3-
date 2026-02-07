// Dispatch Rules API Client
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface DispatchRule {
  id: number;
  name: string;
  description?: string;
  rule_type: 'assignment' | 'constraint' | 'optimization';
  priority: number;
  is_active: boolean;
  conditions: Record<string, any>;
  actions: Record<string, any>;
  version: number;
  execution_count: number;
  avg_execution_time_ms?: number;
  success_rate?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateRulePayload {
  name: string;
  description?: string;
  rule_type: string;
  priority?: number;
  conditions: Record<string, any>;
  actions: Record<string, any>;
  apply_time_start?: string;
  apply_time_end?: string;
  apply_days?: string;
}

export interface UpdateRulePayload {
  name?: string;
  description?: string;
  priority?: number;
  is_active?: boolean;
  conditions?: Record<string, any>;
  actions?: Record<string, any>;
}

export const DispatchRulesAPI = {
  // 규칙 목록 조회
  list: async (params?: {
    skip?: number;
    limit?: number;
    rule_type?: string;
    is_active?: boolean;
  }): Promise<DispatchRule[]> => {
    const response = await axios.get(`${API_BASE_URL}/dispatch-rules`, { params });
    return response.data;
  },

  // 규칙 조회
  get: async (ruleId: number): Promise<DispatchRule> => {
    const response = await axios.get(`${API_BASE_URL}/dispatch-rules/${ruleId}`);
    return response.data;
  },

  // 규칙 생성
  create: async (payload: CreateRulePayload): Promise<DispatchRule> => {
    const response = await axios.post(`${API_BASE_URL}/dispatch-rules`, payload);
    return response.data;
  },

  // 규칙 수정
  update: async (ruleId: number, payload: UpdateRulePayload): Promise<DispatchRule> => {
    const response = await axios.put(`${API_BASE_URL}/dispatch-rules/${ruleId}`, payload);
    return response.data;
  },

  // 규칙 삭제
  delete: async (ruleId: number): Promise<void> => {
    await axios.delete(`${API_BASE_URL}/dispatch-rules/${ruleId}`);
  },

  // 규칙 활성화
  activate: async (ruleId: number): Promise<void> => {
    await axios.post(`${API_BASE_URL}/dispatch-rules/${ruleId}/activate`);
  },

  // 규칙 비활성화
  deactivate: async (ruleId: number): Promise<void> => {
    await axios.post(`${API_BASE_URL}/dispatch-rules/${ruleId}/deactivate`);
  },

  // 규칙 테스트
  test: async (ruleId: number, testData: Record<string, any>): Promise<any> => {
    const response = await axios.post(`${API_BASE_URL}/dispatch-rules/${ruleId}/test`, {
      test_data: testData
    });
    return response.data;
  },

  // 규칙 로그 조회
  getLogs: async (ruleId: number, params?: { skip?: number; limit?: number }): Promise<any[]> => {
    const response = await axios.get(`${API_BASE_URL}/dispatch-rules/${ruleId}/logs`, { params });
    return response.data;
  },

  // 규칙 성능 조회
  getPerformance: async (ruleId: number): Promise<any> => {
    const response = await axios.get(`${API_BASE_URL}/dispatch-rules/${ruleId}/performance`);
    return response.data;
  },

  // 시뮬레이션
  simulate: async (testData: Record<string, any>): Promise<any> => {
    const response = await axios.post(`${API_BASE_URL}/dispatch-rules/simulate`, testData);
    return response.data;
  },

  // 주문 최적화
  optimizeOrder: async (orderId: number): Promise<any> => {
    const response = await axios.post(`${API_BASE_URL}/dispatch-rules/optimize-order/${orderId}`);
    return response.data;
  },
};

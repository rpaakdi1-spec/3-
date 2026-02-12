import axios from 'axios';
import type { RecurringOrder, RecurringOrderCreate, RecurringOrderListResponse } from '../types';
import { API_CONFIG } from '../config/api';

const api = axios.create({
  baseURL: `${API_CONFIG.BASE_URL}/recurring-orders`,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const recurringOrdersAPI = {
  /**
   * 정기 주문 목록 조회
   */
  getAll: async (params?: {
    skip?: number;
    limit?: number;
    is_active?: boolean;
  }): Promise<RecurringOrderListResponse> => {
    const response = await api.get<RecurringOrderListResponse>('/', { params });
    return response.data;
  },

  /**
   * 정기 주문 단일 조회
   */
  getById: async (id: number): Promise<RecurringOrder> => {
    const response = await api.get<RecurringOrder>(`/${id}`);
    return response.data;
  },

  /**
   * 정기 주문 생성
   */
  create: async (data: RecurringOrderCreate): Promise<RecurringOrder> => {
    const response = await api.post<RecurringOrder>('/', data);
    return response.data;
  },

  /**
   * 정기 주문 수정
   */
  update: async (id: number, data: Partial<RecurringOrderCreate>): Promise<RecurringOrder> => {
    const response = await api.put<RecurringOrder>(`/${id}`, data);
    return response.data;
  },

  /**
   * 정기 주문 삭제
   */
  delete: async (id: number): Promise<void> => {
    await api.delete(`/${id}`);
  },

  /**
   * 활성화/비활성화 토글
   */
  toggle: async (id: number): Promise<RecurringOrder> => {
    const response = await api.post<RecurringOrder>(`/${id}/toggle`);
    return response.data;
  },

  /**
   * 수동 주문 생성 (테스트/즉시 실행)
   */
  generate: async (targetDate?: string): Promise<{
    generated: number;
    failed: number;
    orders: any[];
    errors: string[];
  }> => {
    const response = await api.post('/generate', null, {
      params: { target_date: targetDate },
    });
    return response.data;
  },

  /**
   * 생성 미리보기
   */
  preview: async (targetDate?: string): Promise<{
    target_date: string;
    recurring_orders_to_generate: any[];
    count: number;
  }> => {
    const response = await api.get('/preview', {
      params: { target_date: targetDate },
    });
    return response.data;
  },
};

export default recurringOrdersAPI;

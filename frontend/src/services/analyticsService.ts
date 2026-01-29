/**
 * Analytics API Service
 * 배차 이력 분석 API 호출
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const analyticsApi = axios.create({
  baseURL: `${API_BASE_URL}/analytics`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (JWT 토큰 추가 등)
analyticsApi.interceptors.request.use(
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

// Response interceptor (에러 처리)
analyticsApi.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Analytics API Error:', error);
    return Promise.reject(error);
  }
);

/**
 * 배차 통계 조회
 */
export const getDispatchStatistics = async (
  startDate: string,
  endDate: string,
  period: 'daily' | 'weekly' | 'monthly' = 'daily'
) => {
  const response = await analyticsApi.get('/dispatch-statistics', {
    params: { start_date: startDate, end_date: endDate, period },
  });
  return response.data;
};

/**
 * 차량별 운행 분석
 */
export const getVehicleAnalytics = async (startDate: string, endDate: string) => {
  const response = await analyticsApi.get('/vehicle-analytics', {
    params: { start_date: startDate, end_date: endDate },
  });
  return response.data;
};

/**
 * 거래처별 배송 통계
 */
export const getClientAnalytics = async (startDate: string, endDate: string) => {
  const response = await analyticsApi.get('/client-analytics', {
    params: { start_date: startDate, end_date: endDate },
  });
  return response.data;
};

/**
 * 대시보드 요약 통계
 */
export const getDashboardSummary = async (targetDate?: string) => {
  const response = await analyticsApi.get('/dashboard-summary', {
    params: targetDate ? { target_date: targetDate } : {},
  });
  return response.data;
};

/**
 * 빠른 통계 (최근 7일)
 */
export const getQuickStats = async () => {
  const response = await analyticsApi.get('/quick-stats');
  return response.data;
};

export default analyticsApi;

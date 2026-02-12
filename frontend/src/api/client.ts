import axios, { AxiosInstance, AxiosError } from 'axios';
import toast from 'react-hot-toast';
import { API_CONFIG } from '../config/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
          toast.error('세션이 만료되었습니다. 다시 로그인해주세요.');
        } else if (error.response?.status === 403) {
          toast.error('권한이 없습니다.');
        } else if (error.response?.status === 429) {
          toast.error('요청이 너무 많습니다. 잠시 후 다시 시도해주세요.');
        } else if (error.response?.status >= 500) {
          toast.error('서버 오류가 발생했습니다.');
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth
  async login(username: string, password: string) {
    // FastAPI OAuth2PasswordRequestForm expects form-data, not JSON
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await this.client.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }

  async refreshToken() {
    const response = await this.client.post('/auth/refresh');
    return response.data;
  }

  // Orders
  async getOrders(params?: any) {
    const response = await this.client.get('/orders', { params });
    return response.data;
  }

  async getOrder(id: number) {
    const response = await this.client.get(`/orders/${id}`);
    return response.data;
  }

  async createOrder(data: any) {
    const response = await this.client.post('/orders', data);
    return response.data;
  }

  async updateOrder(id: number, data: any) {
    const response = await this.client.put(`/orders/${id}`, data);
    return response.data;
  }

  async deleteOrder(id: number) {
    const response = await this.client.delete(`/orders/${id}`);
    return response.data;
  }

  // Dispatches
  async getDispatches(params?: any) {
    const response = await this.client.get('/dispatches', { params });
    return response.data;
  }

  async getDispatch(id: number) {
    const response = await this.client.get(`/dispatches/${id}`);
    return response.data;
  }

  async autoDispatch(orderId: number) {
    const response = await this.client.post('/dispatches/auto', { order_id: orderId });
    return response.data;
  }

  async manualDispatch(data: any) {
    const response = await this.client.post('/dispatches/manual', data);
    return response.data;
  }

  async optimizeDispatchCVRPTW(
    orderIds: number[],
    vehicleIds?: number[],
    dispatchDate?: string,
    timeLimit: number = 60,
    useTimeWindows: boolean = true,
    useRealRouting: boolean = true
  ) {
    const response = await this.client.post(
      `/dispatches/optimize-cvrptw?time_limit=${timeLimit}&use_time_windows=${useTimeWindows}&use_real_routing=${useRealRouting}`,
      {
        order_ids: orderIds,
        vehicle_ids: vehicleIds,
        dispatch_date: dispatchDate
      }
    );
    return response.data;
  }

  async updateDispatchStatus(id: number, data: any) {
    const response = await this.client.patch(`/dispatches/${id}/status`, data);
    return response.data;
  }

  async confirmDispatches(dispatchIds: number[]) {
    const response = await this.client.post('/dispatches/confirm', { dispatch_ids: dispatchIds });
    return response.data;
  }

  // Vehicles
  async getVehicles(params?: any) {
    const response = await this.client.get('/vehicles', { params });
    return response.data;
  }

  async getAvailableVehicles(params?: any) {
    const response = await this.client.get('/vehicles/available', { params });
    return response.data;
  }

  async createVehicle(data: any) {
    const response = await this.client.post('/vehicles', data);
    return response.data;
  }

  async updateVehicle(id: number, data: any) {
    const response = await this.client.put(`/vehicles/${id}`, data);
    return response.data;
  }

  // Clients
  async getClients(params?: any) {
    const response = await this.client.get('/clients', { params });
    return response.data;
  }

  async createClient(data: any) {
    const response = await this.client.post('/clients', data);
    return response.data;
  }

  async updateClient(id: number, data: any) {
    const response = await this.client.put(`/clients/${id}`, data);
    return response.data;
  }

  async deleteClient(id: number) {
    const response = await this.client.delete(`/clients/${id}`);
    return response.data;
  }

  async deleteDispatch(id: number) {
    const response = await this.client.delete(`/dispatches/${id}`);
    return response.data;
  }

  // Delivery Tracking (Public)
  async getTrackingInfo(trackingNumber: string) {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/delivery-tracking/${trackingNumber}`);
    return response.data;
  }

  async createTrackingLink(dispatchId: number) {
    const response = await this.client.post('/delivery-tracking', { dispatch_id: dispatchId });
    return response.data;
  }

  // Monitoring
  async getHealthCheck() {
    const response = await this.client.get('/monitoring/health');
    return response.data;
  }

  async getMetrics() {
    const response = await this.client.get('/monitoring/metrics');
    return response.data;
  }

  async getDashboard() {
    try {
      // Try dispatch stats endpoint first (more reliable)
      const statsResponse = await this.client.get('/dispatches/stats/summary');
      const stats = statsResponse.data;
      
      // Transform to DashboardStats format
      return {
        total_orders: stats.total_orders || 0,
        pending_orders: stats.pending_orders || 0,
        active_dispatches: stats.active_dispatches || 0,
        completed_today: stats.completed_today || 0,
        available_vehicles: stats.available_vehicles || 0,
        active_vehicles: stats.active_vehicles || 0,
        revenue_today: 0,
        revenue_month: 0,
      };
    } catch (error) {
      // Fallback: try monitoring dashboard
      try {
        const response = await this.client.get('/monitoring/dashboard');
        return response.data;
      } catch (fallbackError) {
        // If both fail, return zeros
        return {
          total_orders: 0,
          pending_orders: 0,
          active_dispatches: 0,
          completed_today: 0,
          available_vehicles: 0,
          active_vehicles: 0,
          revenue_today: 0,
          revenue_month: 0,
        };
      }
    }
  }

  // Cache
  async getCacheStats() {
    const response = await this.client.get('/cache/stats');
    return response.data;
  }

  async invalidateCache(type: string, id: string) {
    const response = await this.client.post(`/cache/invalidate/${type}/${id}`);
    return response.data;
  }

  // AI Chat
  async processChatMessage(message: string, context?: any, model?: string) {
    const response = await this.client.post('/ai-chat/process', {
      message,
      context: context || {},
      model: model || 'auto'
    });
    return response.data;
  }

  async getChatHistory(params?: { 
    limit?: number; 
    offset?: number; 
    intent?: string;
    session_id?: string;
    start_date?: string;
    end_date?: string;
  }) {
    const response = await this.client.get('/ai-chat/history', { params });
    return response.data;
  }

  async deleteChatHistory(historyId: number) {
    const response = await this.client.delete(`/ai-chat/history/${historyId}`);
    return response.data;
  }

  async getChatHistoryStats(params?: {
    start_date?: string;
    end_date?: string;
  }) {
    const response = await this.client.get('/ai-chat/history/stats', { params });
    return response.data;
  }

  // AI Usage & Cost Monitoring
  async getAIUsageStats(params?: {
    start_date?: string;
    end_date?: string;
    model_name?: string;
  }) {
    const response = await this.client.get('/ai-usage/stats', { params });
    return response.data;
  }

  async getAIUsageLogs(params?: {
    limit?: number;
    offset?: number;
    model_name?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
  }) {
    const response = await this.client.get('/ai-usage/logs', { params });
    return response.data;
  }

  async getAICostSummary(period: string = '7d') {
    const response = await this.client.get('/ai-usage/cost-summary', {
      params: { period }
    });
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;

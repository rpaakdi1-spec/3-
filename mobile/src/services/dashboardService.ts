import apiClient from './apiClient';
import { DashboardMetrics, Alert, AlertFilters, PaginatedResponse } from '@types/index';

class DashboardService {
  async getMetrics(): Promise<DashboardMetrics> {
    return apiClient.get<DashboardMetrics>('/dashboard/metrics');
  }

  async getAlerts(filters?: AlertFilters): Promise<PaginatedResponse<Alert>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    return apiClient.get<PaginatedResponse<Alert>>(`/alerts?${params.toString()}`);
  }

  async getAlert(id: number): Promise<Alert> {
    return apiClient.get<Alert>(`/alerts/${id}`);
  }

  async resolveAlert(id: number): Promise<Alert> {
    return apiClient.patch<Alert>(`/alerts/${id}/resolve`);
  }
}

export default new DashboardService();

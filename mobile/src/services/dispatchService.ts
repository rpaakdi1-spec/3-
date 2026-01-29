import apiClient from './apiClient';
import {
  Dispatch,
  DispatchFilters,
  PaginatedResponse,
} from '@types/index';

class DispatchService {
  async getDispatches(filters?: DispatchFilters): Promise<PaginatedResponse<Dispatch>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    return apiClient.get<PaginatedResponse<Dispatch>>(`/dispatches?${params.toString()}`);
  }

  async getDispatch(id: number): Promise<Dispatch> {
    return apiClient.get<Dispatch>(`/dispatches/${id}`);
  }

  async createDispatch(data: Partial<Dispatch>): Promise<Dispatch> {
    return apiClient.post<Dispatch>('/dispatches', data);
  }

  async updateDispatch(id: number, data: Partial<Dispatch>): Promise<Dispatch> {
    return apiClient.put<Dispatch>(`/dispatches/${id}`, data);
  }

  async updateDispatchStatus(id: number, status: Dispatch['status']): Promise<Dispatch> {
    return apiClient.patch<Dispatch>(`/dispatches/${id}/status`, { status });
  }

  async deleteDispatch(id: number): Promise<void> {
    return apiClient.delete(`/dispatches/${id}`);
  }

  async assignVehicle(dispatchId: number, vehicleId: number): Promise<Dispatch> {
    return apiClient.post<Dispatch>(`/dispatches/${dispatchId}/assign-vehicle`, {
      vehicle_id: vehicleId,
    });
  }

  async assignDriver(dispatchId: number, driverId: number): Promise<Dispatch> {
    return apiClient.post<Dispatch>(`/dispatches/${dispatchId}/assign-driver`, {
      driver_id: driverId,
    });
  }
}

export default new DispatchService();

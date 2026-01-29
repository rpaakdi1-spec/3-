import apiClient from './apiClient';
import {
  Vehicle,
  VehicleFilters,
  PaginatedResponse,
} from '@types/index';

class VehicleService {
  async getVehicles(filters?: VehicleFilters): Promise<PaginatedResponse<Vehicle>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    return apiClient.get<PaginatedResponse<Vehicle>>(`/vehicles?${params.toString()}`);
  }

  async getVehicle(id: number): Promise<Vehicle> {
    return apiClient.get<Vehicle>(`/vehicles/${id}`);
  }

  async getVehicleLocation(id: number): Promise<Vehicle['current_location']> {
    return apiClient.get<Vehicle['current_location']>(`/vehicles/${id}/location`);
  }

  async getVehicleTemperature(id: number): Promise<Vehicle['temperature']> {
    return apiClient.get<Vehicle['temperature']>(`/vehicles/${id}/temperature`);
  }

  async createVehicle(data: Partial<Vehicle>): Promise<Vehicle> {
    return apiClient.post<Vehicle>('/vehicles', data);
  }

  async updateVehicle(id: number, data: Partial<Vehicle>): Promise<Vehicle> {
    return apiClient.put<Vehicle>(`/vehicles/${id}`, data);
  }

  async deleteVehicle(id: number): Promise<void> {
    return apiClient.delete(`/vehicles/${id}`);
  }
}

export default new VehicleService();

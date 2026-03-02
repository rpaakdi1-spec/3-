import { api } from '../services/api';

export interface VehicleSuggestion {
  vehicle_id: number;
  vehicle_number: string;
  driver: {
    id: number;
    name: string;
    phone: string;
  } | null;
  status: 'waiting' | 'nearby_dropoff' | 'in_transit';
  current_location: {
    latitude: number;
    longitude: number;
    address?: string;
  } | null;
  distance_km: number;
  estimated_arrival_min: number;
  score: number; // 0-100
  reasons: string[];
  warnings: string[];
}

export interface SuggestVehiclesResponse {
  success: boolean;
  order: any;
  suggestions: VehicleSuggestion[];
  total_count: number;
}

export interface ManualDispatchRequest {
  vehicle_id: number;
}

export interface ManualDispatchResponse {
  success: boolean;
  dispatch_id: number;
  message: string;
  vehicle_number: string;
  driver_name: string | null;
}

export const semiAutoDispatchAPI = {
  /**
   * 주문에 대한 배차 가능 차량 제안 요청
   */
  suggestVehicles: async (
    orderId: number,
    maxDistanceKm: number = 150,
    timeWindowHours: number = 2
  ): Promise<SuggestVehiclesResponse> => {
    const response = await api.post(
      `/semi-auto-dispatch/orders/${orderId}/suggest-vehicles`,
      null,
      {
        params: {
          max_distance_km: maxDistanceKm,
          time_window_hours: timeWindowHours,
        },
      }
    );
    return response.data;
  },

  /**
   * 사용자가 선택한 차량으로 수동 배차
   */
  manualDispatch: async (
    orderId: number,
    vehicleId: number
  ): Promise<ManualDispatchResponse> => {
    const response = await api.post(
      `/semi-auto-dispatch/orders/${orderId}/manual-dispatch`,
      null,
      {
        params: {
          vehicle_id: vehicleId,
        },
      }
    );
    return response.data;
  },
};

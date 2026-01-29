import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1' 
  : 'https://your-production-api.com/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - Add auth token
    this.client.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor - Handle errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          await AsyncStorage.removeItem('authToken');
          // Navigate to login screen
          // You can use a navigation ref here
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(username: string, password: string) {
    const response = await this.client.post('/auth/login', {
      username,
      password,
    });
    return response.data;
  }

  async getProfile() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Dispatch endpoints
  async getMyDispatches(date?: string) {
    const params = date ? { date } : {};
    const response = await this.client.get('/dispatches/my', { params });
    return response.data;
  }

  async getDispatchById(dispatchId: number) {
    const response = await this.client.get(`/dispatches/${dispatchId}`);
    return response.data;
  }

  async updateDispatchStatus(
    dispatchId: number,
    status: string,
    notes?: string
  ) {
    const response = await this.client.put(`/dispatches/${dispatchId}/status`, {
      status,
      notes,
    });
    return response.data;
  }

  async updateRouteStatus(
    dispatchId: number,
    routeId: number,
    status: string,
    arrivalTime?: string,
    departureTime?: string
  ) {
    const response = await this.client.put(
      `/dispatches/${dispatchId}/routes/${routeId}/status`,
      {
        status,
        arrival_time: arrivalTime,
        departure_time: departureTime,
      }
    );
    return response.data;
  }

  // GPS location
  async updateLocation(latitude: number, longitude: number) {
    const response = await this.client.post('/tracking/location', {
      latitude,
      longitude,
      timestamp: new Date().toISOString(),
    });
    return response.data;
  }

  // Photo upload
  async uploadPhoto(
    dispatchId: number,
    routeId: number,
    photoType: 'pickup' | 'delivery',
    photoUri: string
  ) {
    const formData = new FormData();
    formData.append('photo', {
      uri: photoUri,
      type: 'image/jpeg',
      name: `${photoType}_${Date.now()}.jpg`,
    } as any);
    formData.append('dispatch_id', dispatchId.toString());
    formData.append('route_id', routeId.toString());
    formData.append('photo_type', photoType);

    const response = await this.client.post('/tracking/photos', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Generic request method
  async request<T>(config: AxiosRequestConfig): Promise<T> {
    const response = await this.client.request<T>(config);
    return response.data;
  }
}

export default new ApiService();

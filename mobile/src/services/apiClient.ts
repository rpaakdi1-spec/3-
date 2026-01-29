import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL, API_TIMEOUT, ErrorMessages } from '@utils/constants';
import { StorageKeys } from '@types/index';

class ApiClient {
  private client: AxiosInstance;
  private authToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.loadAuthToken();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      async (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          await this.clearAuth();
          // You might want to navigate to login screen here
        }
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private async loadAuthToken() {
    try {
      const token = await AsyncStorage.getItem(StorageKeys.AUTH_TOKEN);
      if (token) {
        this.authToken = token;
      }
    } catch (error) {
      console.error('Failed to load auth token:', error);
    }
  }

  async setAuthToken(token: string) {
    this.authToken = token;
    try {
      await AsyncStorage.setItem(StorageKeys.AUTH_TOKEN, token);
    } catch (error) {
      console.error('Failed to save auth token:', error);
    }
  }

  async clearAuth() {
    this.authToken = null;
    try {
      await AsyncStorage.removeItem(StorageKeys.AUTH_TOKEN);
      await AsyncStorage.removeItem(StorageKeys.USER_DATA);
    } catch (error) {
      console.error('Failed to clear auth:', error);
    }
  }

  private handleError(error: AxiosError): Error {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data: any = error.response.data;

      switch (status) {
        case 400:
          return new Error(data.message || 'Bad Request');
        case 401:
          return new Error(ErrorMessages.UNAUTHORIZED);
        case 403:
          return new Error(ErrorMessages.FORBIDDEN);
        case 404:
          return new Error(ErrorMessages.NOT_FOUND);
        case 500:
          return new Error(ErrorMessages.SERVER_ERROR);
        default:
          return new Error(data.message || ErrorMessages.UNKNOWN);
      }
    } else if (error.request) {
      // Request was made but no response
      if (error.code === 'ECONNABORTED') {
        return new Error(ErrorMessages.TIMEOUT);
      }
      return new Error(ErrorMessages.NETWORK_ERROR);
    } else {
      // Something else happened
      return new Error(error.message || ErrorMessages.UNKNOWN);
    }
  }

  // Generic HTTP methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export default new ApiClient();

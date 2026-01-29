import AsyncStorage from '@react-native-async-storage/async-storage';
import apiClient from './apiClient';
import { User, LoginRequest, LoginResponse, StorageKeys } from '@types/index';

class AuthService {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // Save token and user data
    await apiClient.setAuthToken(response.access_token);
    await this.saveUser(response.user);

    return response;
  }

  async logout(): Promise<void> {
    try {
      // Call logout endpoint (optional)
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.error('Logout API error:', error);
    } finally {
      // Clear local data
      await apiClient.clearAuth();
    }
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const userJson = await AsyncStorage.getItem(StorageKeys.USER_DATA);
      if (userJson) {
        return JSON.parse(userJson);
      }
    } catch (error) {
      console.error('Failed to get current user:', error);
    }
    return null;
  }

  async saveUser(user: User): Promise<void> {
    try {
      await AsyncStorage.setItem(StorageKeys.USER_DATA, JSON.stringify(user));
    } catch (error) {
      console.error('Failed to save user:', error);
    }
  }

  async refreshToken(): Promise<void> {
    const response = await apiClient.post<LoginResponse>('/auth/refresh');
    await apiClient.setAuthToken(response.access_token);
  }

  async isAuthenticated(): Promise<boolean> {
    try {
      const token = await AsyncStorage.getItem(StorageKeys.AUTH_TOKEN);
      return !!token;
    } catch {
      return false;
    }
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
  }

  async resetPassword(email: string): Promise<void> {
    await apiClient.post('/auth/reset-password', { email });
  }
}

export default new AuthService();

import AsyncStorage from '@react-native-async-storage/async-storage';
import { StorageKeys } from '@types/index';

interface OfflineQueue {
  id: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  url: string;
  data?: any;
  timestamp: number;
}

class OfflineService {
  private queue: OfflineQueue[] = [];
  private isProcessing = false;

  async initialize() {
    await this.loadQueue();
  }

  private async loadQueue() {
    try {
      const data = await AsyncStorage.getItem(StorageKeys.OFFLINE_DATA);
      if (data) {
        this.queue = JSON.parse(data);
      }
    } catch (error) {
      console.error('Failed to load offline queue:', error);
    }
  }

  private async saveQueue() {
    try {
      await AsyncStorage.setItem(StorageKeys.OFFLINE_DATA, JSON.stringify(this.queue));
    } catch (error) {
      console.error('Failed to save offline queue:', error);
    }
  }

  async addToQueue(
    method: OfflineQueue['method'],
    url: string,
    data?: any
  ): Promise<void> {
    const item: OfflineQueue = {
      id: `${Date.now()}_${Math.random()}`,
      method,
      url,
      data,
      timestamp: Date.now(),
    };

    this.queue.push(item);
    await this.saveQueue();
  }

  async processQueue(apiClient: any): Promise<void> {
    if (this.isProcessing || this.queue.length === 0) {
      return;
    }

    this.isProcessing = true;

    const failedItems: OfflineQueue[] = [];

    for (const item of this.queue) {
      try {
        switch (item.method) {
          case 'GET':
            await apiClient.get(item.url);
            break;
          case 'POST':
            await apiClient.post(item.url, item.data);
            break;
          case 'PUT':
            await apiClient.put(item.url, item.data);
            break;
          case 'PATCH':
            await apiClient.patch(item.url, item.data);
            break;
          case 'DELETE':
            await apiClient.delete(item.url);
            break;
        }

        console.log(`Successfully synced: ${item.method} ${item.url}`);
      } catch (error) {
        console.error(`Failed to sync: ${item.method} ${item.url}`, error);
        failedItems.push(item);
      }
    }

    this.queue = failedItems;
    await this.saveQueue();
    this.isProcessing = false;
  }

  getQueueSize(): number {
    return this.queue.length;
  }

  async clearQueue(): Promise<void> {
    this.queue = [];
    await this.saveQueue();
  }

  // Cache management
  async cacheData(key: string, data: any): Promise<void> {
    try {
      await AsyncStorage.setItem(`cache_${key}`, JSON.stringify({
        data,
        timestamp: Date.now(),
      }));
    } catch (error) {
      console.error('Failed to cache data:', error);
    }
  }

  async getCachedData<T>(key: string, maxAge: number = 300000): Promise<T | null> {
    try {
      const cached = await AsyncStorage.getItem(`cache_${key}`);
      if (!cached) return null;

      const { data, timestamp } = JSON.parse(cached);
      
      // Check if cache is still valid
      if (Date.now() - timestamp > maxAge) {
        await AsyncStorage.removeItem(`cache_${key}`);
        return null;
      }

      return data;
    } catch (error) {
      console.error('Failed to get cached data:', error);
      return null;
    }
  }

  async clearCache(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(key => key.startsWith('cache_'));
      await AsyncStorage.multiRemove(cacheKeys);
    } catch (error) {
      console.error('Failed to clear cache:', error);
    }
  }
}

export default new OfflineService();

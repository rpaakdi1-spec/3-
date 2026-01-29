import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import api from './api';

const OFFLINE_QUEUE_KEY = '@offline_queue';
const CACHED_DISPATCHES_KEY = '@cached_dispatches';

interface OfflineAction {
  id: string;
  type: 'update_route_status' | 'upload_photo' | 'send_gps';
  data: any;
  timestamp: number;
}

class OfflineService {
  private isOnline: boolean = true;
  private syncInProgress: boolean = false;

  /**
   * 네트워크 상태 모니터링 초기화
   */
  initialize(): void {
    NetInfo.addEventListener((state) => {
      const wasOffline = !this.isOnline;
      this.isOnline = state.isConnected ?? false;

      console.log('Network status:', this.isOnline ? 'Online' : 'Offline');

      // 오프라인에서 온라인으로 전환 시 동기화
      if (wasOffline && this.isOnline) {
        this.syncOfflineData();
      }
    });
  }

  /**
   * 현재 온라인 상태 확인
   */
  async checkOnlineStatus(): Promise<boolean> {
    const state = await NetInfo.fetch();
    this.isOnline = state.isConnected ?? false;
    return this.isOnline;
  }

  /**
   * 오프라인 액션 큐에 추가
   */
  async addToOfflineQueue(action: Omit<OfflineAction, 'id' | 'timestamp'>): Promise<void> {
    try {
      const queueJson = await AsyncStorage.getItem(OFFLINE_QUEUE_KEY);
      const queue: OfflineAction[] = queueJson ? JSON.parse(queueJson) : [];

      const newAction: OfflineAction = {
        ...action,
        id: `${Date.now()}_${Math.random()}`,
        timestamp: Date.now(),
      };

      queue.push(newAction);
      await AsyncStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue));
      
      console.log('Action added to offline queue:', newAction);
    } catch (error) {
      console.error('Failed to add to offline queue:', error);
    }
  }

  /**
   * 오프라인 큐에서 액션 가져오기
   */
  async getOfflineQueue(): Promise<OfflineAction[]> {
    try {
      const queueJson = await AsyncStorage.getItem(OFFLINE_QUEUE_KEY);
      return queueJson ? JSON.parse(queueJson) : [];
    } catch (error) {
      console.error('Failed to get offline queue:', error);
      return [];
    }
  }

  /**
   * 오프라인 데이터 동기화
   */
  async syncOfflineData(): Promise<void> {
    if (this.syncInProgress) {
      console.log('Sync already in progress');
      return;
    }

    this.syncInProgress = true;

    try {
      const isOnline = await this.checkOnlineStatus();
      if (!isOnline) {
        console.log('Cannot sync: offline');
        return;
      }

      const queue = await this.getOfflineQueue();
      
      if (queue.length === 0) {
        console.log('No offline data to sync');
        return;
      }

      console.log(`Syncing ${queue.length} offline actions...`);

      const failedActions: OfflineAction[] = [];

      for (const action of queue) {
        try {
          await this.executeAction(action);
          console.log('Action synced:', action.type);
        } catch (error) {
          console.error('Failed to sync action:', action.type, error);
          failedActions.push(action);
        }
      }

      // 실패한 액션만 다시 저장
      await AsyncStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(failedActions));
      
      console.log(`Sync completed. ${queue.length - failedActions.length} succeeded, ${failedActions.length} failed`);
    } catch (error) {
      console.error('Sync offline data error:', error);
    } finally {
      this.syncInProgress = false;
    }
  }

  /**
   * 액션 실행
   */
  private async executeAction(action: OfflineAction): Promise<void> {
    switch (action.type) {
      case 'update_route_status':
        await api.updateDispatchRouteStatus(
          action.data.dispatchId,
          action.data.routeId,
          action.data.status,
          action.data.workStartTime,
          action.data.workEndTime
        );
        break;

      case 'upload_photo':
        await api.uploadPhoto(action.data.formData);
        break;

      case 'send_gps':
        await api.sendGPSLocation(action.data.latitude, action.data.longitude);
        break;

      default:
        console.warn('Unknown action type:', action.type);
    }
  }

  /**
   * 배차 목록 캐시 저장
   */
  async cacheDispatches(dispatches: any[]): Promise<void> {
    try {
      await AsyncStorage.setItem(CACHED_DISPATCHES_KEY, JSON.stringify(dispatches));
      console.log('Dispatches cached:', dispatches.length);
    } catch (error) {
      console.error('Failed to cache dispatches:', error);
    }
  }

  /**
   * 캐시된 배차 목록 가져오기
   */
  async getCachedDispatches(): Promise<any[]> {
    try {
      const cachedJson = await AsyncStorage.getItem(CACHED_DISPATCHES_KEY);
      return cachedJson ? JSON.parse(cachedJson) : [];
    } catch (error) {
      console.error('Failed to get cached dispatches:', error);
      return [];
    }
  }

  /**
   * 오프라인 큐 초기화
   */
  async clearOfflineQueue(): Promise<void> {
    try {
      await AsyncStorage.removeItem(OFFLINE_QUEUE_KEY);
      console.log('Offline queue cleared');
    } catch (error) {
      console.error('Failed to clear offline queue:', error);
    }
  }

  /**
   * 캐시 초기화
   */
  async clearCache(): Promise<void> {
    try {
      await AsyncStorage.removeItem(CACHED_DISPATCHES_KEY);
      console.log('Cache cleared');
    } catch (error) {
      console.error('Failed to clear cache:', error);
    }
  }

  /**
   * 오프라인 모드 상태 확인
   */
  isOffline(): boolean {
    return !this.isOnline;
  }
}

export default new OfflineService();

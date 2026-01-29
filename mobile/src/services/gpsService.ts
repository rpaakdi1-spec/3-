import * as Location from 'expo-location';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { StorageKeys } from '../types';

interface GPSLocation {
  latitude: number;
  longitude: number;
  altitude: number | null;
  accuracy: number | null;
  speed: number | null;
  heading: number | null;
  timestamp: string;
}

class GPSService {
  private locationSubscription: Location.LocationSubscription | null = null;
  private isTracking: boolean = false;
  private updateInterval: number = 10000; // 10초마다 업데이트
  private apiBaseUrl: string = '';

  constructor() {
    this.loadSettings();
  }

  private async loadSettings() {
    try {
      const settings = await AsyncStorage.getItem(StorageKeys.SETTINGS);
      if (settings) {
        const parsed = JSON.parse(settings);
        this.apiBaseUrl = parsed.apiBaseUrl || 'http://localhost:8000';
        this.updateInterval = parsed.gpsUpdateInterval || 10000;
      }
    } catch (error) {
      console.error('Failed to load GPS settings:', error);
    }
  }

  /**
   * 위치 권한 요청
   */
  async requestPermissions(): Promise<boolean> {
    try {
      const { status: foregroundStatus } = await Location.requestForegroundPermissionsAsync();
      
      if (foregroundStatus !== 'granted') {
        console.error('Foreground location permission denied');
        return false;
      }

      // 백그라운드 권한도 요청 (선택사항)
      const { status: backgroundStatus } = await Location.requestBackgroundPermissionsAsync();
      
      if (backgroundStatus !== 'granted') {
        console.warn('Background location permission denied');
      }

      return true;
    } catch (error) {
      console.error('Failed to request location permissions:', error);
      return false;
    }
  }

  /**
   * GPS 추적 시작
   */
  async startTracking(vehicleId: number): Promise<void> {
    if (this.isTracking) {
      console.warn('GPS tracking is already active');
      return;
    }

    const hasPermission = await this.requestPermissions();
    if (!hasPermission) {
      throw new Error('Location permission not granted');
    }

    try {
      this.isTracking = true;

      // 위치 업데이트 구독
      this.locationSubscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.High,
          timeInterval: this.updateInterval,
          distanceInterval: 50, // 50미터마다 업데이트
        },
        async (location) => {
          await this.handleLocationUpdate(vehicleId, location);
        }
      );

      console.log('GPS tracking started for vehicle:', vehicleId);
    } catch (error) {
      this.isTracking = false;
      console.error('Failed to start GPS tracking:', error);
      throw error;
    }
  }

  /**
   * GPS 추적 중지
   */
  async stopTracking(): Promise<void> {
    if (this.locationSubscription) {
      this.locationSubscription.remove();
      this.locationSubscription = null;
    }
    this.isTracking = false;
    console.log('GPS tracking stopped');
  }

  /**
   * 위치 업데이트 처리
   */
  private async handleLocationUpdate(
    vehicleId: number,
    location: Location.LocationObject
  ): Promise<void> {
    try {
      const gpsData: GPSLocation = {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        altitude: location.coords.altitude,
        accuracy: location.coords.accuracy,
        speed: location.coords.speed,
        heading: location.coords.heading,
        timestamp: new Date(location.timestamp).toISOString(),
      };

      // 서버로 GPS 데이터 전송
      await this.sendLocationToServer(vehicleId, gpsData);

      // 오프라인 모드를 위해 로컬에 저장
      await this.saveLocationLocally(vehicleId, gpsData);

      console.log('Location updated:', gpsData);
    } catch (error) {
      console.error('Failed to handle location update:', error);
    }
  }

  /**
   * 서버로 위치 데이터 전송
   */
  private async sendLocationToServer(
    vehicleId: number,
    gpsData: GPSLocation
  ): Promise<void> {
    try {
      const token = await AsyncStorage.getItem(StorageKeys.AUTH_TOKEN);
      
      await axios.post(
        `${this.apiBaseUrl}/api/v1/vehicles/${vehicleId}/location`,
        gpsData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          timeout: 5000,
        }
      );
    } catch (error) {
      console.error('Failed to send location to server:', error);
      // 오프라인 큐에 추가
      await this.addToOfflineQueue(vehicleId, gpsData);
    }
  }

  /**
   * 로컬 저장소에 위치 저장
   */
  private async saveLocationLocally(
    vehicleId: number,
    gpsData: GPSLocation
  ): Promise<void> {
    try {
      const key = `@gps_history_${vehicleId}`;
      const existingData = await AsyncStorage.getItem(key);
      const history = existingData ? JSON.parse(existingData) : [];

      // 최근 100개만 유지
      history.unshift(gpsData);
      if (history.length > 100) {
        history.pop();
      }

      await AsyncStorage.setItem(key, JSON.stringify(history));
    } catch (error) {
      console.error('Failed to save location locally:', error);
    }
  }

  /**
   * 오프라인 큐에 추가
   */
  private async addToOfflineQueue(
    vehicleId: number,
    gpsData: GPSLocation
  ): Promise<void> {
    try {
      const key = StorageKeys.OFFLINE_DATA;
      const existingData = await AsyncStorage.getItem(key);
      const offlineData = existingData ? JSON.parse(existingData) : { gpsQueue: [] };

      offlineData.gpsQueue = offlineData.gpsQueue || [];
      offlineData.gpsQueue.push({
        vehicleId,
        data: gpsData,
        timestamp: new Date().toISOString(),
      });

      await AsyncStorage.setItem(key, JSON.stringify(offlineData));
    } catch (error) {
      console.error('Failed to add to offline queue:', error);
    }
  }

  /**
   * 현재 위치 가져오기 (1회성)
   */
  async getCurrentLocation(): Promise<GPSLocation | null> {
    try {
      const hasPermission = await this.requestPermissions();
      if (!hasPermission) {
        return null;
      }

      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });

      return {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        altitude: location.coords.altitude,
        accuracy: location.coords.accuracy,
        speed: location.coords.speed,
        heading: location.coords.heading,
        timestamp: new Date(location.timestamp).toISOString(),
      };
    } catch (error) {
      console.error('Failed to get current location:', error);
      return null;
    }
  }

  /**
   * GPS 추적 상태 확인
   */
  isActive(): boolean {
    return this.isTracking;
  }

  /**
   * 오프라인 큐 동기화
   */
  async syncOfflineQueue(): Promise<void> {
    try {
      const key = StorageKeys.OFFLINE_DATA;
      const existingData = await AsyncStorage.getItem(key);
      if (!existingData) return;

      const offlineData = JSON.parse(existingData);
      const gpsQueue = offlineData.gpsQueue || [];

      if (gpsQueue.length === 0) return;

      console.log(`Syncing ${gpsQueue.length} offline GPS records...`);

      const token = await AsyncStorage.getItem(StorageKeys.AUTH_TOKEN);
      const failedItems: any[] = [];

      for (const item of gpsQueue) {
        try {
          await axios.post(
            `${this.apiBaseUrl}/api/v1/vehicles/${item.vehicleId}/location`,
            item.data,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
              timeout: 5000,
            }
          );
        } catch (error) {
          console.error('Failed to sync GPS record:', error);
          failedItems.push(item);
        }
      }

      // 실패한 항목만 큐에 남김
      offlineData.gpsQueue = failedItems;
      await AsyncStorage.setItem(key, JSON.stringify(offlineData));

      console.log(`Synced ${gpsQueue.length - failedItems.length} records, ${failedItems.length} failed`);
    } catch (error) {
      console.error('Failed to sync offline queue:', error);
    }
  }
}

export default new GPSService();

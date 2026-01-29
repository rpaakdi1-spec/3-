import Geolocation from '@react-native-community/geolocation';
import { Platform, PermissionsAndroid, Alert } from 'react-native';
import BackgroundGeolocation from 'react-native-background-geolocation';
import api from './api';

class GPSService {
  private watchId: number | null = null;
  private backgroundConfigured: boolean = false;

  /**
   * 위치 권한 요청 (Android)
   */
  async requestLocationPermission(): Promise<boolean> {
    if (Platform.OS === 'ios') {
      // iOS는 Info.plist에서 설정
      return true;
    }

    try {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        {
          title: '위치 권한 요청',
          message: '배차 위치 추적을 위해 위치 권한이 필요합니다.',
          buttonPositive: '허용',
          buttonNegative: '거부',
        }
      );

      if (granted === PermissionsAndroid.RESULTS.GRANTED) {
        console.log('Location permission granted');
        return true;
      } else {
        console.log('Location permission denied');
        Alert.alert(
          '권한 필요',
          '배차 위치 추적을 위해 위치 권한이 필요합니다. 설정에서 권한을 허용해주세요.'
        );
        return false;
      }
    } catch (error) {
      console.error('Location permission error:', error);
      return false;
    }
  }

  /**
   * 현재 위치 가져오기
   */
  async getCurrentPosition(): Promise<{ latitude: number; longitude: number } | null> {
    return new Promise((resolve) => {
      Geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (error) => {
          console.error('Get current position error:', error);
          resolve(null);
        },
        {
          enableHighAccuracy: true,
          timeout: 15000,
          maximumAge: 10000,
        }
      );
    });
  }

  /**
   * 포그라운드 위치 추적 시작
   */
  async startForegroundTracking(intervalMs: number = 30000): Promise<void> {
    const hasPermission = await this.requestLocationPermission();
    if (!hasPermission) return;

    this.watchId = Geolocation.watchPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        console.log('Position updated:', latitude, longitude);

        try {
          await api.sendGPSLocation(latitude, longitude);
          console.log('GPS location sent successfully');
        } catch (error) {
          console.error('Failed to send GPS location:', error);
        }
      },
      (error) => {
        console.error('Watch position error:', error);
      },
      {
        enableHighAccuracy: true,
        distanceFilter: 100, // 100m 이동 시 업데이트
        interval: intervalMs,
        fastestInterval: intervalMs / 2,
      }
    );
  }

  /**
   * 포그라운드 위치 추적 중지
   */
  stopForegroundTracking(): void {
    if (this.watchId !== null) {
      Geolocation.clearWatch(this.watchId);
      this.watchId = null;
      console.log('Foreground tracking stopped');
    }
  }

  /**
   * 백그라운드 위치 추적 설정
   */
  async configureBackgroundTracking(): Promise<void> {
    if (this.backgroundConfigured) return;

    try {
      await BackgroundGeolocation.ready({
        // 위치 추적 설정
        desiredAccuracy: BackgroundGeolocation.DESIRED_ACCURACY_HIGH,
        distanceFilter: 100, // 100m 이동 시 업데이트
        stopTimeout: 5, // 5분 정지 시 추적 일시 중지
        
        // 백그라운드 설정
        debug: __DEV__, // 개발 모드에서만 디버그
        logLevel: __DEV__ ? BackgroundGeolocation.LOG_LEVEL_VERBOSE : BackgroundGeolocation.LOG_LEVEL_OFF,
        
        // Android 설정
        foregroundService: true,
        notification: {
          title: '배차 중',
          text: '위치를 추적하고 있습니다.',
        },
        
        // iOS 설정
        activityType: BackgroundGeolocation.ACTIVITY_TYPE_OTHER_NAVIGATION,
        pausesLocationUpdatesAutomatically: false,
      });

      // 위치 업데이트 이벤트 리스너
      BackgroundGeolocation.onLocation(
        async (location) => {
          console.log('[Background] Location:', location.coords);
          
          try {
            await api.sendGPSLocation(location.coords.latitude, location.coords.longitude);
            console.log('[Background] GPS location sent successfully');
          } catch (error) {
            console.error('[Background] Failed to send GPS location:', error);
          }
        },
        (error) => {
          console.error('[Background] Location error:', error);
        }
      );

      // 에러 이벤트 리스너
      BackgroundGeolocation.onProviderChange((event) => {
        console.log('[Background] Provider change:', event);
        
        if (!event.enabled) {
          Alert.alert(
            'GPS 비활성화',
            'GPS가 비활성화되었습니다. 위치 추적을 위해 GPS를 활성화해주세요.'
          );
        }
      });

      this.backgroundConfigured = true;
      console.log('Background tracking configured');
    } catch (error) {
      console.error('Background tracking configuration error:', error);
    }
  }

  /**
   * 백그라운드 위치 추적 시작
   */
  async startBackgroundTracking(): Promise<void> {
    try {
      await this.configureBackgroundTracking();
      await BackgroundGeolocation.start();
      console.log('Background tracking started');
    } catch (error) {
      console.error('Failed to start background tracking:', error);
    }
  }

  /**
   * 백그라운드 위치 추적 중지
   */
  async stopBackgroundTracking(): Promise<void> {
    try {
      await BackgroundGeolocation.stop();
      console.log('Background tracking stopped');
    } catch (error) {
      console.error('Failed to stop background tracking:', error);
    }
  }

  /**
   * 위치 추적 상태 확인
   */
  async isTracking(): Promise<boolean> {
    try {
      const state = await BackgroundGeolocation.getState();
      return state.enabled;
    } catch (error) {
      console.error('Failed to get tracking state:', error);
      return false;
    }
  }

  /**
   * 모든 위치 추적 중지
   */
  async stopAllTracking(): Promise<void> {
    this.stopForegroundTracking();
    await this.stopBackgroundTracking();
    console.log('All tracking stopped');
  }
}

export default new GPSService();

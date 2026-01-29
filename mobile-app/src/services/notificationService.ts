import messaging, { FirebaseMessagingTypes } from '@react-native-firebase/messaging';
import { Platform, PermissionsAndroid, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from './api';

const FCM_TOKEN_KEY = '@fcm_token';

class NotificationService {
  /**
   * 푸시 알림 권한 요청
   */
  async requestPermission(): Promise<boolean> {
    try {
      if (Platform.OS === 'ios') {
        const authStatus = await messaging().requestPermission();
        const enabled =
          authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
          authStatus === messaging.AuthorizationStatus.PROVISIONAL;

        if (enabled) {
          console.log('iOS notification permission granted:', authStatus);
          return true;
        } else {
          console.log('iOS notification permission denied');
          return false;
        }
      } else {
        // Android 13+ requires POST_NOTIFICATIONS permission
        if (Platform.Version >= 33) {
          const granted = await PermissionsAndroid.request(
            PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS
          );
          
          if (granted === PermissionsAndroid.RESULTS.GRANTED) {
            console.log('Android notification permission granted');
            return true;
          } else {
            console.log('Android notification permission denied');
            return false;
          }
        }
        return true; // Android < 13 doesn't need runtime permission
      }
    } catch (error) {
      console.error('Request permission error:', error);
      return false;
    }
  }

  /**
   * FCM 토큰 가져오기 및 서버 등록
   */
  async getFCMToken(): Promise<string | null> {
    try {
      const hasPermission = await this.requestPermission();
      if (!hasPermission) {
        console.log('No permission for notifications');
        return null;
      }

      const token = await messaging().getToken();
      console.log('FCM Token:', token);

      // 로컬에 저장된 토큰과 비교
      const savedToken = await AsyncStorage.getItem(FCM_TOKEN_KEY);
      
      if (token !== savedToken) {
        // 새 토큰이면 서버에 등록
        await this.registerTokenToServer(token);
        await AsyncStorage.setItem(FCM_TOKEN_KEY, token);
      }

      return token;
    } catch (error) {
      console.error('Get FCM token error:', error);
      return null;
    }
  }

  /**
   * 서버에 FCM 토큰 등록
   */
  async registerTokenToServer(token: string): Promise<void> {
    try {
      // TODO: 백엔드 API 엔드포인트 추가 필요
      // await api.post('/users/fcm-token', { token });
      console.log('FCM token registered to server:', token);
    } catch (error) {
      console.error('Register FCM token error:', error);
    }
  }

  /**
   * 푸시 알림 초기화
   */
  async initialize(): Promise<void> {
    try {
      // FCM 토큰 가져오기
      await this.getFCMToken();

      // 토큰 갱신 리스너
      messaging().onTokenRefresh(async (token) => {
        console.log('FCM token refreshed:', token);
        await this.registerTokenToServer(token);
        await AsyncStorage.setItem(FCM_TOKEN_KEY, token);
      });

      // 포그라운드 메시지 수신
      messaging().onMessage(async (remoteMessage) => {
        console.log('Foreground message received:', remoteMessage);
        this.handleNotification(remoteMessage);
      });

      // 백그라운드 메시지 수신 (app.tsx에서 설정)
      messaging().setBackgroundMessageHandler(async (remoteMessage) => {
        console.log('Background message received:', remoteMessage);
      });

      // 알림 탭하여 앱 열기
      messaging().onNotificationOpenedApp((remoteMessage) => {
        console.log('Notification opened app:', remoteMessage);
        this.handleNotificationOpen(remoteMessage);
      });

      // 앱이 종료된 상태에서 알림 탭하여 앱 열기
      const initialNotification = await messaging().getInitialNotification();
      if (initialNotification) {
        console.log('App opened from quit state:', initialNotification);
        this.handleNotificationOpen(initialNotification);
      }

      console.log('Notification service initialized');
    } catch (error) {
      console.error('Initialize notification service error:', error);
    }
  }

  /**
   * 포그라운드 알림 처리
   */
  private handleNotification(remoteMessage: FirebaseMessagingTypes.RemoteMessage): void {
    const { notification, data } = remoteMessage;

    if (notification) {
      Alert.alert(
        notification.title || '알림',
        notification.body || '',
        [
          { text: '닫기', style: 'cancel' },
          {
            text: '보기',
            onPress: () => this.handleNotificationOpen(remoteMessage),
          },
        ]
      );
    }
  }

  /**
   * 알림 열기 처리
   */
  private handleNotificationOpen(remoteMessage: FirebaseMessagingTypes.RemoteMessage): void {
    const { data } = remoteMessage;

    // 알림 타입에 따라 화면 이동
    if (data?.type === 'dispatch_assigned') {
      // 배차 할당 알림 -> 배차 상세 화면으로 이동
      const dispatchId = data.dispatch_id;
      console.log('Navigate to dispatch detail:', dispatchId);
      // TODO: Navigation.navigate('DispatchDetail', { dispatchId });
    } else if (data?.type === 'route_update') {
      // 경로 업데이트 알림
      console.log('Route updated notification');
    }
  }

  /**
   * 로컬 알림 표시 (선택 사항)
   */
  async showLocalNotification(title: string, body: string, data?: any): Promise<void> {
    // React Native Push Notification 라이브러리 사용 가능
    // 여기서는 간단히 Alert로 대체
    Alert.alert(title, body);
  }
}

export default new NotificationService();

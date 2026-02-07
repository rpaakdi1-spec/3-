import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage, Messaging } from 'firebase/messaging';
import { firebaseConfig, vapidKey } from '../config/firebase';
import toast from 'react-hot-toast';

class FCMService {
  private messaging: Messaging | null = null;
  private initialized = false;

  /**
   * Firebase 초기화
   */
  initialize(): boolean {
    try {
      if (this.initialized) {
        return true;
      }

      // Firebase 앱 초기화
      const app = initializeApp(firebaseConfig);
      
      // Messaging 초기화
      if ('serviceWorker' in navigator && 'Notification' in window) {
        this.messaging = getMessaging(app);
        this.initialized = true;
        console.log('✅ Firebase initialized');
        return true;
      } else {
        console.warn('⚠️ Service Worker or Notifications not supported');
        return false;
      }
    } catch (error) {
      console.error('❌ Firebase initialization error:', error);
      return false;
    }
  }

  /**
   * 알림 권한 요청 및 FCM 토큰 발급
   */
  async requestPermissionAndGetToken(): Promise<string | null> {
    try {
      if (!this.messaging) {
        console.error('❌ Messaging not initialized');
        return null;
      }

      // 알림 권한 요청
      const permission = await Notification.requestPermission();
      
      if (permission === 'granted') {
        console.log('✅ Notification permission granted');
        
        // FCM 토큰 발급
        const token = await getToken(this.messaging, {
          vapidKey: vapidKey
        });
        
        if (token) {
          console.log('✅ FCM Token:', token);
          return token;
        } else {
          console.error('❌ No registration token available');
          return null;
        }
      } else if (permission === 'denied') {
        console.error('❌ Notification permission denied');
        toast.error('알림 권한이 거부되었습니다. 브라우저 설정에서 알림을 허용해주세요.');
        return null;
      } else {
        console.warn('⚠️ Notification permission not granted');
        return null;
      }
    } catch (error) {
      console.error('❌ Error getting FCM token:', error);
      return null;
    }
  }

  /**
   * 포그라운드 메시지 수신 리스너 등록
   */
  onMessageListener(callback: (payload: any) => void): void {
    if (!this.messaging) {
      console.error('❌ Messaging not initialized');
      return;
    }

    onMessage(this.messaging, (payload) => {
      console.log('📩 Foreground message received:', payload);
      
      // 콜백 실행
      callback(payload);
      
      // Toast 알림 표시
      if (payload.notification) {
        toast(
          `${payload.notification.title}: ${payload.notification.body}`,
          {
            duration: 5000,
            icon: '🔔'
          }
        );
      }
    });
  }

  /**
   * FCM 토큰을 서버에 저장
   */
  async saveTokenToServer(token: string, userId: number): Promise<boolean> {
    try {
      const response = await fetch('/api/v1/fcm/tokens', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          user_id: userId,
          device_type: 'web',
          browser: navigator.userAgent
        })
      });

      if (response.ok) {
        console.log('✅ Token saved to server');
        return true;
      } else {
        console.error('❌ Failed to save token to server');
        return false;
      }
    } catch (error) {
      console.error('❌ Error saving token:', error);
      return false;
    }
  }

  /**
   * 알림 권한 상태 확인
   */
  getNotificationPermission(): NotificationPermission {
    if ('Notification' in window) {
      return Notification.permission;
    }
    return 'denied';
  }

  /**
   * 알림 지원 여부 확인
   */
  isSupported(): boolean {
    return 'Notification' in window && 'serviceWorker' in navigator;
  }
}

// 싱글톤 인스턴스
export const fcmService = new FCMService();

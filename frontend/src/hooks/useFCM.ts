/**
 * Firebase Cloud Messaging (FCM) 푸시 알림 Hook
 */

import { useEffect, useState, useCallback } from 'react';
import { getToken, onMessage, deleteToken } from 'firebase/messaging';
import { messaging } from '../firebase/config';
import { toast } from 'sonner';

interface UseFCMReturn {
  token: string | null;
  permission: NotificationPermission;
  isSupported: boolean;
  requestPermission: () => Promise<boolean>;
  unregisterToken: () => Promise<boolean>;
}

export const useFCM = (): UseFCMReturn => {
  const [token, setToken] = useState<string | null>(null);
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [isSupported, setIsSupported] = useState(false);

  // 브라우저 지원 확인
  useEffect(() => {
    const supported = 'Notification' in window && 'serviceWorker' in navigator && messaging !== null;
    setIsSupported(supported);
    
    if (supported && 'Notification' in window) {
      setPermission(Notification.permission);
    }
  }, []);

  // 알림 권한 요청 및 FCM 토큰 등록
  const requestPermission = useCallback(async (): Promise<boolean> => {
    if (!isSupported || !messaging) {
      console.warn('FCM is not supported in this browser');
      toast.error('이 브라우저는 푸시 알림을 지원하지 않습니다.');
      return false;
    }

    try {
      // 알림 권한 요청
      const permission = await Notification.requestPermission();
      setPermission(permission);

      if (permission !== 'granted') {
        console.log('Notification permission denied');
        toast.warning('알림 권한이 거부되었습니다.');
        return false;
      }

      console.log('Notification permission granted');

      // Service Worker 등록 확인
      const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
      console.log('Service Worker registered:', registration);

      // FCM 토큰 가져오기
      const vapidKey = import.meta.env.VITE_FIREBASE_VAPID_KEY;
      
      if (!vapidKey) {
        console.error('VAPID key is missing');
        toast.error('Firebase 설정이 올바르지 않습니다.');
        return false;
      }

      const currentToken = await getToken(messaging, {
        vapidKey: vapidKey,
        serviceWorkerRegistration: registration
      });

      if (currentToken) {
        console.log('✅ FCM token obtained:', currentToken.substring(0, 20) + '...');
        setToken(currentToken);

        // 서버에 토큰 등록
        await registerTokenToServer(currentToken);
        
        toast.success('푸시 알림이 활성화되었습니다! 🔔');
        return true;
      } else {
        console.warn('No FCM token available');
        toast.warning('FCM 토큰을 가져올 수 없습니다.');
        return false;
      }
    } catch (error) {
      console.error('Error requesting FCM permission:', error);
      toast.error('푸시 알림 설정 중 오류가 발생했습니다.');
      return false;
    }
  }, [isSupported]);

  // 서버에 FCM 토큰 등록
  const registerTokenToServer = async (fcmToken: string): Promise<void> => {
    try {
      const response = await fetch('/api/v1/notifications/register-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          token: fcmToken,
          device_type: 'web',
          device_id: navigator.userAgent,
          app_version: '1.0.0'
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Token registered to server:', data);
      } else {
        console.error('❌ Failed to register token to server:', response.statusText);
      }
    } catch (error) {
      console.error('❌ Error registering token to server:', error);
    }
  };

  // FCM 토큰 삭제
  const unregisterToken = useCallback(async (): Promise<boolean> => {
    if (!messaging || !token) {
      return false;
    }

    try {
      // Firebase에서 토큰 삭제
      await deleteToken(messaging);
      
      // 서버에 토큰 비활성화 요청
      await fetch(`/api/v1/notifications/unregister-token/${token}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      setToken(null);
      console.log('✅ FCM token unregistered');
      toast.success('푸시 알림이 비활성화되었습니다.');
      return true;
    } catch (error) {
      console.error('❌ Error unregistering token:', error);
      toast.error('푸시 알림 비활성화 중 오류가 발생했습니다.');
      return false;
    }
  }, [token]);

  // 포그라운드 메시지 수신
  useEffect(() => {
    if (!messaging) return;

    const unsubscribe = onMessage(messaging, (payload) => {
      console.log('📩 Foreground message received:', payload);

      const { notification, data } = payload;
      
      if (notification) {
        const { title, body } = notification;
        
        // Toast 알림 표시
        toast.info(title || '새 알림', {
          description: body,
          duration: 5000,
          action: data?.type ? {
            label: '보기',
            onClick: () => {
              // 알림 타입에 따라 페이지 이동
              switch (data.type) {
                case 'order':
                  window.location.href = `/orders/${data.order_id || ''}`;
                  break;
                case 'vehicle_alert':
                  window.location.href = '/vehicles';
                  break;
                case 'dispatch_assigned':
                  window.location.href = '/dispatches';
                  break;
                default:
                  window.location.href = '/';
              }
            }
          } : undefined
        });

        // 브라우저 알림 표시 (백업)
        if (Notification.permission === 'granted' && document.hidden) {
          new Notification(title || '새 알림', {
            body: body,
            icon: '/logo192.png',
            badge: '/badge.png',
            tag: data?.type || 'default'
          });
        }
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  return {
    token,
    permission,
    isSupported,
    requestPermission,
    unregisterToken
  };
};

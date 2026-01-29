// PWA 유틸리티 함수

export const registerServiceWorker = async (): Promise<ServiceWorkerRegistration | null> => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('/service-worker.js', {
        scope: '/'
      });
      
      console.log('Service Worker registered successfully:', registration);

      // 업데이트 체크
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // 새 버전 사용 가능
              console.log('New service worker available. Please refresh.');
              if (confirm('새 버전이 사용 가능합니다. 업데이트하시겠습니까?')) {
                window.location.reload();
              }
            }
          });
        }
      });

      return registration;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
      return null;
    }
  }
  
  console.warn('Service Workers are not supported');
  return null;
};

export const unregisterServiceWorker = async (): Promise<boolean> => {
  if ('serviceWorker' in navigator) {
    const registration = await navigator.serviceWorker.ready;
    return registration.unregister();
  }
  return false;
};

// PWA 설치 프롬프트
let deferredPrompt: any = null;

export const setupInstallPrompt = () => {
  window.addEventListener('beforeinstallprompt', (e) => {
    // 기본 프롬프트 방지
    e.preventDefault();
    deferredPrompt = e;
    console.log('Install prompt available');
  });

  window.addEventListener('appinstalled', () => {
    console.log('PWA installed successfully');
    deferredPrompt = null;
  });
};

export const showInstallPrompt = async (): Promise<boolean> => {
  if (!deferredPrompt) {
    console.warn('Install prompt not available');
    return false;
  }

  // 프롬프트 표시
  deferredPrompt.prompt();

  // 사용자 선택 대기
  const { outcome } = await deferredPrompt.userChoice;
  console.log(`User response to install prompt: ${outcome}`);

  deferredPrompt = null;
  return outcome === 'accepted';
};

export const isInstalled = (): boolean => {
  // 독립 실행형 모드 확인
  return window.matchMedia('(display-mode: standalone)').matches ||
    (window.navigator as any).standalone === true ||
    document.referrer.includes('android-app://');
};

export const canInstall = (): boolean => {
  return deferredPrompt !== null;
};

// 오프라인 감지
export const setupOfflineDetection = (
  onOnline: () => void,
  onOffline: () => void
) => {
  window.addEventListener('online', onOnline);
  window.addEventListener('offline', onOffline);

  // 초기 상태 확인
  if (!navigator.onLine) {
    onOffline();
  }

  return () => {
    window.removeEventListener('online', onOnline);
    window.removeEventListener('offline', onOffline);
  };
};

export const isOnline = (): boolean => {
  return navigator.onLine;
};

// 백그라운드 동기화
export const requestBackgroundSync = async (tag: string): Promise<void> => {
  if ('serviceWorker' in navigator && 'sync' in ServiceWorkerRegistration.prototype) {
    try {
      const registration = await navigator.serviceWorker.ready;
      await (registration as any).sync.register(tag);
      console.log(`Background sync registered: ${tag}`);
    } catch (error) {
      console.error('Background sync registration failed:', error);
    }
  } else {
    console.warn('Background sync not supported');
  }
};

// 푸시 알림 구독
export const subscribeToPushNotifications = async (): Promise<PushSubscription | null> => {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    console.warn('Push notifications not supported');
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    
    // 기존 구독 확인
    let subscription = await registration.pushManager.getSubscription();
    
    if (!subscription) {
      // VAPID 공개 키 (서버에서 제공해야 함)
      const vapidPublicKey = import.meta.env.VITE_VAPID_PUBLIC_KEY;
      
      if (!vapidPublicKey) {
        console.warn('VAPID public key not configured');
        return null;
      }

      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
      });

      console.log('Push subscription created:', subscription);
    }

    return subscription;
  } catch (error) {
    console.error('Push subscription failed:', error);
    return null;
  }
};

export const unsubscribeFromPushNotifications = async (): Promise<boolean> => {
  if (!('serviceWorker' in navigator)) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    
    if (subscription) {
      const result = await subscription.unsubscribe();
      console.log('Push subscription removed');
      return result;
    }
  } catch (error) {
    console.error('Push unsubscription failed:', error);
  }

  return false;
};

// VAPID 키 변환 유틸리티
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

// PWA 업데이트 체크
export const checkForUpdates = async (): Promise<boolean> => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.update();
      return true;
    } catch (error) {
      console.error('Update check failed:', error);
      return false;
    }
  }
  return false;
};

// 알림 권한 요청
export const requestNotificationPermission = async (): Promise<NotificationPermission> => {
  if (!('Notification' in window)) {
    console.warn('Notifications not supported');
    return 'denied';
  }

  // 이미 권한이 있는 경우
  if (Notification.permission === 'granted') {
    return 'granted';
  }

  // 권한 요청
  if (Notification.permission !== 'denied') {
    try {
      const permission = await Notification.requestPermission();
      console.log(`Notification permission: ${permission}`);
      return permission;
    } catch (error) {
      console.error('Notification permission request failed:', error);
      return 'denied';
    }
  }

  return Notification.permission;
};

// Firebase Cloud Messaging Service Worker
// 백그라운드 푸시 알림 수신을 위한 Service Worker

// Firebase scripts import
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// Firebase 설정
// 주의: 환경변수를 Service Worker에서 직접 사용할 수 없으므로 빌드 시 주입 필요
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Firebase 초기화
firebase.initializeApp(firebaseConfig);

// Firebase Messaging 인스턴스 가져오기
const messaging = firebase.messaging();

// 백그라운드 메시지 수신 처리
messaging.onBackgroundMessage((payload) => {
  console.log('[Service Worker] Background message received:', payload);
  
  const notificationTitle = payload.notification?.title || '새 알림';
  const notificationOptions = {
    body: payload.notification?.body || '',
    icon: '/logo192.png',
    badge: '/badge.png',
    tag: payload.data?.type || 'default',
    data: payload.data || {},
    requireInteraction: false,
    vibrate: [200, 100, 200]
  };

  return self.registration.showNotification(notificationTitle, notificationOptions);
});

// 알림 클릭 이벤트 처리
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification clicked:', event.notification);
  
  event.notification.close();
  
  const notificationData = event.notification.data || {};
  let targetUrl = '/';
  
  // 알림 타입에 따라 URL 결정
  switch (notificationData.type) {
    case 'order':
      targetUrl = `/orders/${notificationData.order_id || ''}`;
      break;
    case 'vehicle_alert':
      targetUrl = `/vehicles`;
      break;
    case 'dispatch_assigned':
      targetUrl = `/dispatches`;
      break;
    default:
      targetUrl = '/';
  }
  
  // 앱이 이미 열려있는지 확인
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // 이미 열려있는 탭이 있으면 그 탭으로 포커스
      for (const client of clientList) {
        if (client.url === new URL(targetUrl, self.location.origin).href && 'focus' in client) {
          return client.focus();
        }
      }
      
      // 열려있는 탭이 없으면 새 탭 열기
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});

// Service Worker 설치 이벤트
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  self.skipWaiting();
});

// Service Worker 활성화 이벤트
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(self.clients.claim());
});

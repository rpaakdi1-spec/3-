const CACHE_NAME = 'cold-chain-v3.0.0';

// 설치: 즉시 skipWaiting (캐싱 없음 → 로딩 차단 없음)
self.addEventListener('install', () => {
  self.skipWaiting();
});

// 활성화: 구 캐시 삭제 + clients.claim()
// event.waitUntil 없이 → load 이벤트 차단 안 함
self.addEventListener('activate', (event) => {
  // clients.claim()은 필요 (즉시 새 SW 적용)
  event.waitUntil(self.clients.claim());

  // 구 캐시 삭제는 백그라운드에서 (non-blocking)
  caches.keys().then((cacheNames) => {
    cacheNames.forEach((name) => {
      if (name !== CACHE_NAME) caches.delete(name);
    });
  });
});

// Fetch: API는 SW 통과, /assets/는 캐시 우선, HTML은 네트워크 우선
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API → 그냥 통과 (네트워크)
  if (url.pathname.startsWith('/api/')) return;

  // /assets/ → 캐시 우선 (해시 파일, 영구 캐시)
  if (url.pathname.startsWith('/assets/')) {
    event.respondWith(
      caches.open(CACHE_NAME).then((cache) =>
        cache.match(request).then((cached) => {
          if (cached) return cached;
          return fetch(request).then((res) => {
            if (res.status === 200) cache.put(request, res.clone());
            return res;
          });
        })
      )
    );
    return;
  }

  // HTML 탐색 → 네트워크 우선 (최신 index.html)
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() =>
        caches.match('/index.html').then((r) => r || caches.match('/'))
      )
    );
  }
});

// 푸시 알림
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {};
  event.waitUntil(
    self.registration.showNotification(data.title || 'Cold Chain 알림', {
      body: data.body || '새로운 알림이 있습니다',
      icon: '/icon-192x192.png',
      badge: '/icon-72x72.png',
      tag: data.tag || 'default',
      data: data.url ? { url: data.url } : {},
      requireInteraction: false,
    })
  );
});

// 알림 클릭
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const urlToOpen = event.notification.data?.url || '/';
  event.waitUntil(
    clients
      .matchAll({ type: 'window', includeUncontrolled: true })
      .then((list) => {
        const found = list.find((c) => c.url === urlToOpen && 'focus' in c);
        return found ? found.focus() : clients.openWindow?.(urlToOpen);
      })
  );
});

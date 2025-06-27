// AIRISS v4.0 Service Worker - 오프라인 지원 및 캐싱
const CACHE_NAME = 'airiss-v4-cache-v1';
const urlsToCache = [
  '/',
  '/static/pwa/manifest.json',
  '/docs',
  '/health',
  // CSS 라이브러리들
  'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  // JS 라이브러리들
  'https://cdn.jsdelivr.net/npm/chart.js',
];

// 설치 이벤트
self.addEventListener('install', event => {
  console.log('[SW] AIRISS v4.0 Service Worker 설치 중...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] 캐시 열기 성공');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('[SW] 모든 리소스 캐시 완료');
        self.skipWaiting(); // 즉시 활성화
      })
      .catch(error => {
        console.error('[SW] 캐시 설치 실패:', error);
      })
  );
});

// 활성화 이벤트
self.addEventListener('activate', event => {
  console.log('[SW] AIRISS v4.0 Service Worker 활성화');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] 오래된 캐시 삭제:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[SW] 활성화 완료 - 모든 탭에서 컨트롤 시작');
      self.clients.claim();
    })
  );
});

// 네트워크 요청 인터셉트
self.addEventListener('fetch', event => {
  // WebSocket 요청은 제외
  if (event.request.url.includes('ws://') || event.request.url.includes('wss://')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // 캐시에 있으면 캐시에서 반환
        if (response) {
          console.log('[SW] 캐시에서 제공:', event.request.url);
          return response;
        }

        // 캐시에 없으면 네트워크에서 가져오기
        return fetch(event.request)
          .then(response => {
            // 유효한 응답인지 확인
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // 응답 복사 (스트림은 한번만 읽을 수 있음)
            const responseToCache = response.clone();

            // 중요한 리소스만 캐시에 저장
            if (event.request.url.includes('/api/') || 
                event.request.url.includes('/static/') ||
                event.request.method === 'GET') {
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseToCache);
                  console.log('[SW] 새 리소스 캐시:', event.request.url);
                });
            }

            return response;
          })
          .catch(error => {
            console.log('[SW] 네트워크 오류, 오프라인 페이지 제공:', error);
            
            // HTML 페이지 요청시 오프라인 페이지 제공
            if (event.request.destination === 'document') {
              return new Response(`
                <!DOCTYPE html>
                <html>
                <head>
                  <title>AIRISS v4.0 - 오프라인</title>
                  <meta charset="UTF-8">
                  <meta name="viewport" content="width=device-width, initial-scale=1.0">
                  <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
                    .offline-container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
                    .icon { font-size: 4rem; color: #FF5722; margin-bottom: 20px; }
                    h1 { color: #FF5722; margin-bottom: 20px; }
                    p { color: #666; line-height: 1.6; }
                    button { background: #FF5722; color: white; border: none; padding: 12px 24px; border-radius: 6px; font-size: 1rem; cursor: pointer; margin-top: 20px; }
                    button:hover { background: #E64A19; }
                  </style>
                </head>
                <body>
                  <div class="offline-container">
                    <div class="icon">📡</div>
                    <h1>AIRISS v4.0</h1>
                    <h2>현재 오프라인 상태입니다</h2>
                    <p>인터넷 연결을 확인하고 다시 시도해주세요.<br>
                    일부 기능은 오프라인에서도 사용할 수 있습니다.</p>
                    <button onclick="window.location.reload()">다시 시도</button>
                  </div>
                </body>
                </html>
              `, {
                headers: { 'Content-Type': 'text/html' }
              });
            }
            
            // 기타 요청은 기본 에러 응답
            return new Response('오프라인 상태입니다', { status: 503 });
          });
      })
  );
});

// 백그라운드 동기화 (선택적)
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    console.log('[SW] 백그라운드 동기화 실행');
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  // 백그라운드에서 실행할 작업들
  return Promise.resolve();
}

// 푸시 알림 처리 (선택적)
self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'AIRISS v4.0 알림',
    icon: '/static/pwa/icon-192.png',
    badge: '/static/pwa/icon-192.png',
    vibrate: [100, 50, 100],
    data: { dateOfArrival: Date.now() },
    actions: [
      {
        action: 'explore',
        title: '확인하기',
        icon: '/static/pwa/icon-chart.png'
      },
      {
        action: 'close',
        title: '닫기',
        icon: '/static/pwa/icon-close.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('AIRISS v4.0', options)
  );
});

// 알림 클릭 처리
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

console.log('[SW] AIRISS v4.0 Service Worker 로드 완료');
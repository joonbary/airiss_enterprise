// AIRISS v4.0 Enhanced Service Worker
// PWA 기능 및 오프라인 지원

const CACHE_NAME = 'airiss-v4-cache-v1';
const urlsToCache = [
  '/',
  '/executive',
  '/dashboard',
  '/static/manifest.json',
  // CSS 및 JS는 인라인으로 처리되므로 별도 캐싱 불필요
];

// 설치 이벤트
self.addEventListener('install', (event) => {
  console.log('[SW] Service Worker 설치 중...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] 캐시 오픈 완료');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('[SW] 모든 리소스 캐싱 완료');
        return self.skipWaiting();
      })
  );
});

// 활성화 이벤트
self.addEventListener('activate', (event) => {
  console.log('[SW] Service Worker 활성화');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] 오래된 캐시 삭제:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// 요청 가로채기 및 캐시 전략
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  
  // WebSocket 요청은 제외
  if (url.protocol === 'ws:' || url.protocol === 'wss:') {
    return;
  }
  
  // API 요청은 Network First 전략
  if (url.pathname.startsWith('/api') || 
      url.pathname.startsWith('/analysis') || 
      url.pathname.startsWith('/upload') ||
      url.pathname.startsWith('/health')) {
    
    event.respondWith(
      networkFirstStrategy(request)
    );
    return;
  }
  
  // 정적 리소스는 Cache First 전략
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      cacheFirstStrategy(request)
    );
    return;
  }
  
  // 페이지 요청은 Stale While Revalidate 전략
  if (request.method === 'GET' && 
      (request.headers.get('accept') || '').includes('text/html')) {
    
    event.respondWith(
      staleWhileRevalidateStrategy(request)
    );
    return;
  }
  
  // 기본 전략
  event.respondWith(
    networkFirstStrategy(request)
  );
});

// Network First 전략 (API 요청용)
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    
    // 성공적인 응답을 캐시에 저장
    if (networkResponse.status === 200) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] 네트워크 요청 실패, 캐시에서 찾는 중:', request.url);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // 오프라인 페이지 반환 (옵션)
    if (request.headers.get('accept').includes('text/html')) {
      return new Response(
        generateOfflinePage(),
        {
          headers: { 'Content-Type': 'text/html' }
        }
      );
    }
    
    throw error;
  }
}

// Cache First 전략 (정적 리소스용)
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    console.log('[SW] 정적 리소스 로드 실패:', request.url);
    throw error;
  }
}

// Stale While Revalidate 전략 (페이지 요청용)
async function staleWhileRevalidateStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.status === 200) {
      const cache = caches.open(CACHE_NAME);
      cache.then(c => c.put(request, networkResponse.clone()));
    }
    return networkResponse;
  }).catch(() => {
    // 네트워크 실패 시 캐시된 버전 반환
    return cachedResponse;
  });
  
  // 캐시된 버전이 있으면 즉시 반환, 없으면 네트워크 대기
  return cachedResponse || fetchPromise;
}

// 백그라운드 동기화
self.addEventListener('sync', (event) => {
  console.log('[SW] 백그라운드 동기화:', event.tag);
  
  if (event.tag === 'analysis-sync') {
    event.waitUntil(syncAnalysisData());
  }
});

// 푸시 알림
self.addEventListener('push', (event) => {
  console.log('[SW] 푸시 알림 수신:', event.data?.text());
  
  if (event.data) {
    const data = event.data.json();
    
    const options = {
      body: data.body || 'AIRISS에서 새로운 알림이 있습니다.',
      icon: '/static/icons/icon-192x192.png',
      badge: '/static/icons/badge-72x72.png',
      vibrate: [200, 100, 200],
      data: data.data || {},
      actions: [
        {
          action: 'view',
          title: '확인하기',
          icon: '/static/icons/view-icon.png'
        },
        {
          action: 'dismiss',
          title: '닫기',
          icon: '/static/icons/close-icon.png'
        }
      ],
      tag: data.tag || 'airiss-notification',
      requireInteraction: data.urgent || false
    };
    
    event.waitUntil(
      self.registration.showNotification(
        data.title || 'AIRISS 알림',
        options
      )
    );
  }
});

// 알림 클릭 처리
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] 알림 클릭:', event.notification.tag, event.action);
  
  event.notification.close();
  
  if (event.action === 'view') {
    const urlToOpen = event.notification.data.url || '/';
    
    event.waitUntil(
      clients.matchAll({
        type: 'window',
        includeUncontrolled: true
      }).then((clientList) => {
        // 이미 열린 탭이 있는지 확인
        for (const client of clientList) {
          if (client.url.includes(urlToOpen) && 'focus' in client) {
            return client.focus();
          }
        }
        
        // 새 탭 열기
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
    );
  }
});

// 오프라인 페이지 생성
function generateOfflinePage() {
  return `
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIRISS - 오프라인</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #FF5722 0%, #F89C26 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-align: center;
        }
        .container {
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 500px;
        }
        .icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        .title {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: #FF5722;
        }
        .message {
            font-size: 1.1rem;
            margin-bottom: 25px;
            color: #666;
        }
        .retry-btn {
            background: linear-gradient(135deg, #FF5722, #F89C26);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        .retry-btn:hover {
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">📡</div>
        <div class="title">오프라인 상태</div>
        <div class="message">
            인터넷 연결을 확인하고<br>
            다시 시도해주세요.
        </div>
        <button class="retry-btn" onclick="window.location.reload()">
            🔄 다시 시도
        </button>
    </div>
</body>
</html>
  `;
}

// 분석 데이터 동기화 (백그라운드)
async function syncAnalysisData() {
  try {
    console.log('[SW] 분석 데이터 동기화 시작');
    
    // 여기에 실제 동기화 로직 구현
    // 예: 대기 중인 분석 요청을 서버로 전송
    
    const response = await fetch('/analysis/sync', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        timestamp: Date.now(),
        type: 'background-sync'
      })
    });
    
    if (response.ok) {
      console.log('[SW] 분석 데이터 동기화 완료');
    } else {
      throw new Error('동기화 실패');
    }
  } catch (error) {
    console.error('[SW] 분석 데이터 동기화 오류:', error);
    // 재시도 로직 추가 가능
  }
}

// 메시지 처리 (메인 앱과의 통신)
self.addEventListener('message', (event) => {
  console.log('[SW] 메시지 수신:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({
      version: CACHE_NAME,
      timestamp: Date.now()
    });
  }
});

console.log('[SW] AIRISS v4.0 Enhanced Service Worker 로드 완료');
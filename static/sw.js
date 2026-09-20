// BUILD+ Enterprise Service Worker (PWA Cache & Offline Strategy)
const CACHE_NAME = 'buildplus-v1';
const STATIC_ASSETS = [
  '/',
  '/static/css/admin_theme.css',
  '/static/css/custom.css',
  '/static/js/theme_switcher.js',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png',
  '/static/images/icon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Only cache GET requests
  if (event.request.method !== 'GET') return;
  
  // Network-first strategy for dynamic views, cache fallback for assets
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          if (event.request.mode === 'navigate') {
            return caches.match('/');
          }
        });
      })
  );
});

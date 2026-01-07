const CACHE_NAME = 'command-ai-v3';
const STATIC_ASSETS = [
  '/pwa/manifest.json',
  '/pwa/icon-192.png',
  '/pwa/icon-512.png',
  '/'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - cache static assets, bypass Streamlit and API endpoints
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  const request = event.request;
  
  // Skip non-GET requests and Streamlit endpoints
  if (request.method !== 'GET' || 
      url.pathname.includes('/_stcore/') ||
      url.pathname.includes('/stream') ||
      url.hostname !== 'moj.perasper.com') {
    // Bypass caching for Streamlit real-time endpoints and cross-origin
    event.respondWith(fetch(request));
    return;
  }
  
  // For static PWA assets, cache-first
  if (STATIC_ASSETS.includes(url.pathname)) {
    event.respondWith(
      caches.match(request)
        .then(cached => cached || fetch(request).then(response => {
          // Cache the response for future
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(request, responseClone);
          });
          return response;
        }))
    );
    return;
  }
  
  // For all other requests (HTML, CSS, JS) - network-first with offline fallback
  event.respondWith(
    fetch(request)
      .then(response => {
        // Don't cache API responses, only successful HTML/CSS/JS
        const contentType = response.headers.get('content-type') || '';
        if (response.status === 200 && 
            (contentType.includes('text/html') || 
             contentType.includes('text/css') || 
             contentType.includes('application/javascript'))) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // Offline fallback
        return caches.match(request)
          .then(cached => {
            if (cached) return cached;
            // Return offline page for HTML requests
            if (request.headers.get('accept')?.includes('text/html')) {
              return caches.match('/')
                .then(cachedIndex => cachedIndex || new Response('Offline - Please reconnect to use Command AI'));
            }
            return new Response('Offline', { status: 503 });
          });
      })
  );
});
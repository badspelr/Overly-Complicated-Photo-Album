// Service Worker for Photo Album PWA
const CACHE_NAME = 'photo-album-v2'; // Updated version
const STATIC_CACHE_NAME = 'photo-album-static-v2';
const DYNAMIC_CACHE_NAME = 'photo-album-dynamic-v2';
const IMAGE_CACHE_NAME = 'photo-album-images-v2';
const OFFLINE_QUEUE_NAME = 'photo-album-offline-queue';

// Resources to cache immediately
const STATIC_ASSETS = [
  '/',
  '/offline/',
  '/static/album/css/main.css',
  '/static/album/css/mobile.css',
  '/static/album/js/main.js',
  '/static/album/js/pwa.js',
  '/manifest.json',
  '/favicon.ico',
  '/logo192.png',
  '/logo512.png',
  // Material Icons font
  'https://fonts.googleapis.com/icon?family=Material+Icons',
  // Roboto font
  'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap'
];

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('Service Worker: Installing');
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE_NAME).then(cache => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      }),
      // Pre-cache offline page
      caches.open(DYNAMIC_CACHE_NAME).then(cache => {
        return fetch('/offline/').then(response => {
          return cache.put('/offline/', response);
        }).catch(() => {
          console.log('Could not cache offline page');
        });
      })
    ]).then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches and handle offline queue
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating');
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (!cacheName.includes('photo-album-v2') && cacheName.includes('photo-album')) {
              console.log('Service Worker: Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Process any pending offline queue items
      processOfflineQueue()
    ]).then(() => self.clients.claim())
  );
});

// Enhanced fetch event with better mobile support
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Always go to the network for login and registration pages
  if (url.pathname.startsWith('/accounts/login') || url.pathname.startsWith('/accounts/register')) {
    event.respondWith(fetch(request));
    return;
  }

  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    return;
  }

  // Handle image requests with special caching
  if (request.destination === 'image' || url.pathname.match(/\.(jpg|jpeg|png|gif|webp|svg)$/)) {
    event.respondWith(handleImageRequest(request));
    return;
  }

  // Handle API requests with offline support
  if (url.pathname.startsWith('/api/') || url.pathname.includes('/upload/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // Handle static assets
  if (STATIC_ASSETS.some(asset => url.pathname.endsWith(asset) || url.href.endsWith(asset))) {
    event.respondWith(
      caches.match(request).then(response => {
        return response || fetch(request).then(response => {
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(STATIC_CACHE_NAME).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        });
      })
    );
    return;
  }

  // Default strategy: Network first, then cache
  event.respondWith(
    fetch(request).then(response => {
      // Cache successful GET requests for dynamic content
      if (request.method === 'GET' && response.status === 200 && !url.pathname.includes('/admin/')) {
        const responseClone = response.clone();
        caches.open(DYNAMIC_CACHE_NAME).then(cache => {
          cache.put(request, responseClone);
        });
      }
      return response;
    }).catch(() => {
      // Return cached version if available
      return caches.match(request).then(response => {
        return response || caches.match('/offline/');
      });
    })
  );
});

// Handle image requests with progressive loading
async function handleImageRequest(request) {
  const cache = await caches.open(IMAGE_CACHE_NAME);

  // Try cache first for images
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    // Fetch from network
    const networkResponse = await fetch(request);
    if (networkResponse.status === 200) {
      // Cache the image
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Image fetch failed, returning offline placeholder');
    // Return a small offline placeholder for images
    return new Response(
      `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
        <rect width="200" height="200" fill="#f0f0f0"/>
        <text x="100" y="100" text-anchor="middle" dy=".3em" fill="#666" font-size="14">Offline</text>
      </svg>`,
      {
        headers: { 'Content-Type': 'image/svg+xml' }
      }
    );
  }
}

// Handle API requests with offline queue support
async function handleApiRequest(request) {
  const cache = await caches.open(DYNAMIC_CACHE_NAME);

  // For POST requests (uploads), add to offline queue if offline
  if (request.method === 'POST' && !navigator.onLine) {
    await addToOfflineQueue(request);
    return new Response(JSON.stringify({
      success: false,
      message: 'You are offline. Your upload has been queued.',
      queued: true
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const response = await fetch(request);

    // Cache successful GET requests
    if (request.method === 'GET' && response.status === 200) {
      cache.put(request, response.clone());
    }

    return response;
  } catch (error) {
    // Return cached version for GET requests
    if (request.method === 'GET') {
      const cachedResponse = await cache.match(request);
      if (cachedResponse) {
        return cachedResponse;
      }
    }

    // Return offline response
    return new Response(JSON.stringify({
      success: false,
      message: 'You are offline. Please try again when connected.',
      offline: true
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Offline queue management
async function addToOfflineQueueFromMessage(requestData) {
  try {
    const queue = await getOfflineQueue();
    const queueItem = {
      id: Date.now() + Math.random(),
      url: requestData.url,
      method: requestData.method,
      headers: requestData.headers,
      body: requestData.body,
      timestamp: requestData.timestamp,
      retries: 0
    };

    queue.push(queueItem);
    await saveOfflineQueue(queue);

    // Notify clients about queued item
    self.clients.matchAll().then(clients => {
      clients.forEach(client => {
        client.postMessage({
          type: 'offline-queue-updated',
          queueLength: queue.length
        });
      });
    });

  } catch (error) {
    console.error('Failed to add to offline queue from message:', error);
  }
}

async function processOfflineQueue() {
  const queue = await getOfflineQueue();
  if (queue.length === 0) return;

  console.log(`Processing ${queue.length} offline queue items`);

  for (const item of queue) {
    try {
      const request = new Request(item.url, {
        method: item.method,
        headers: item.headers,
        body: item.body
      });

      const response = await fetch(request);

      if (response.ok) {
        // Remove successful item from queue
        const index = queue.indexOf(item);
        if (index > -1) {
          queue.splice(index, 1);
        }

        // Notify clients
        self.clients.matchAll().then(clients => {
          clients.forEach(client => {
            client.postMessage({
              type: 'offline-queue-processed',
              success: true,
              remaining: queue.length
            });
          });
        });
      } else {
        item.retries = (item.retries || 0) + 1;
        if (item.retries >= 3) {
          // Remove failed item after 3 retries
          const index = queue.indexOf(item);
          if (index > -1) {
            queue.splice(index, 1);
          }
        }
      }
    } catch (error) {
      console.error('Failed to process offline queue item:', error);
      item.retries = (item.retries || 0) + 1;
    }
  }

  await saveOfflineQueue(queue);
}

async function getOfflineQueue() {
  try {
    const cache = await caches.open(OFFLINE_QUEUE_NAME);
    const response = await cache.match('queue');
    if (response) {
      return await response.json();
    }
  } catch (error) {
    console.error('Failed to get offline queue:', error);
  }
  return [];
}

async function saveOfflineQueue(queue) {
  try {
    const cache = await caches.open(OFFLINE_QUEUE_NAME);
    const response = new Response(JSON.stringify(queue));
    await cache.put('queue', response);
  } catch (error) {
    console.error('Failed to save offline queue:', error);
  }
}

// Background sync for offline actions
self.addEventListener('sync', event => {
  console.log('Service Worker: Background sync', event.tag);

  if (event.tag === 'background-sync') {
    event.waitUntil(processOfflineQueue());
  }
});

// Message handler for communication with main thread
self.addEventListener('message', event => {
  const { type, data } = event.data;

  switch (type) {
    case 'skip-waiting':
      self.skipWaiting();
      break;
    case 'process-offline-queue':
      event.waitUntil(processOfflineQueue());
      break;
    case 'get-queue-status':
      getOfflineQueue().then(queue => {
        event.ports[0].postMessage({ queueLength: queue.length });
      });
      break;
    case 'add-to-offline-queue':
      event.waitUntil(addToOfflineQueueFromMessage(data));
      break;
  }
});

// Push notifications
self.addEventListener('push', event => {
  console.log('Service Worker: Push received', event);

  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/static/album/icons/icon-192x192.png',
      badge: '/static/album/icons/icon-72x72.png',
      vibrate: [100, 50, 100],
      data: data.data || {},
      actions: [
        {
          action: 'view',
          title: 'View'
        },
        {
          action: 'dismiss',
          title: 'Dismiss'
        }
      ]
    };

    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  console.log('Service Worker: Notification clicked', event);
  event.notification.close();

  const action = event.action;
  const url = event.notification.data.url || '/';

  if (action === 'view') {
    event.waitUntil(
      clients.openWindow(url)
    );
  }
});
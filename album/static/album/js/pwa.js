// PWA functionality for Photo Album
class PWAHandler {
  constructor() {
    this.deferredPrompt = null;
    this.offlineQueue = [];
    this.touchStartX = null;
    this.touchStartY = null;
    this.init();
  }

  init() {
    // Register service worker
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/album/js/sw.js')
          .then(registration => {
            console.log('SW registered: ', registration);
            this.registration = registration;
          })
          .catch(registrationError => {
            console.log('SW registration failed: ', registrationError);
          });
      });
    }

    // Handle PWA install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
      console.log('PWA install prompt triggered');
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallButton();
    });

    // Handle successful installation
    window.addEventListener('appinstalled', (evt) => {
      console.log('PWA was installed successfully');
      this.hideInstallButton();
    });

    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      console.log('PWA is running in standalone mode');
    }

    // Initialize mobile features
    this.initMobileFeatures();
    this.initOfflineQueue();
    this.initTouchGestures();
  }

  initMobileFeatures() {
    // Add mobile-specific meta tags if not present
    if (!document.querySelector('meta[name="viewport"]')) {
      const viewport = document.createElement('meta');
      viewport.name = 'viewport';
      viewport.content = 'width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes';
      document.head.appendChild(viewport);
    }

    // Add iOS-specific meta tags
    if (!document.querySelector('meta[name="apple-mobile-web-app-capable"]')) {
      const iosMeta = document.createElement('meta');
      iosMeta.name = 'apple-mobile-web-app-capable';
      iosMeta.content = 'yes';
      document.head.appendChild(iosMeta);
    }

    // Detect mobile device
    this.isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    if (this.isMobile) {
      document.body.classList.add('mobile-device');
    }
  }

  initOfflineQueue() {
    // Listen for messages from service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', (event) => {
        this.handleServiceWorkerMessage(event.data);
      });
    }

    // Process queue when coming back online
    window.addEventListener('online', () => {
      this.processOfflineQueue();
    });

    // Show offline notification if needed
    if (!this.isOnline()) {
      this.showOfflineNotification();
    }
  }

  handleServiceWorkerMessage(data) {
    switch (data.type) {
      case 'offline-queue-updated':
        // Don't show notification on upload page - handled by upload page logic
        if (!window.location.pathname.includes('/upload')) {
          this.showNotification(`Offline queue updated. ${data.queueLength} items pending.`, 'info');
        }
        break;
      case 'offline-queue-processed':
        if (data.success) {
          // Don't show notification on upload page - handled by upload page logic
          if (!window.location.pathname.includes('/upload')) {
            this.showNotification('Offline uploads processed successfully!', 'success');
          }
        }
        break;
    }
  }

  // Process offline upload queue using service worker
  async processOfflineQueue() {
    if (!this.isOnline() || !this.registration) return;

    // Trigger background sync if supported
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      try {
        await this.registration.sync.register('background-sync');
        // Don't show notification on upload page - handled by upload page logic
        if (!window.location.pathname.includes('/upload')) {
          this.showNotification('Background sync registered for offline uploads.', 'info');
        }
      } catch (error) {
        console.log('Background sync not supported or failed:', error);
        // Fallback to manual processing
        this.registration.active.postMessage({ type: 'process-offline-queue' });
      }
    } else {
      // Fallback for browsers without background sync
      this.registration.active.postMessage({ type: 'process-offline-queue' });
    }
  }

  initTouchGestures() {
    // Add touch gesture support for image viewing
    document.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        this.touchStartX = e.touches[0].clientX;
        this.touchStartY = e.touches[0].clientY;
      }
    }, { passive: true });

    document.addEventListener('touchend', (e) => {
      if (!this.touchStartX || !this.touchStartY) return;

      const touchEndX = e.changedTouches[0].clientX;
      const touchEndY = e.changedTouches[0].clientY;
      const deltaX = touchEndX - this.touchStartX;
      const deltaY = touchEndY - this.touchStartY;

      // Detect swipe gestures
      if (Math.abs(deltaX) > 50 && Math.abs(deltaY) < 100) {
        if (deltaX > 0) {
          this.handleSwipe('right');
        } else {
          this.handleSwipe('left');
        }
      }

      this.touchStartX = null;
      this.touchStartY = null;
    }, { passive: true });

    // Add pinch-to-zoom support for images
    this.initPinchZoom();
  }

  initPinchZoom() {
    let initialDistance = null;
    let initialScale = 1;

    document.addEventListener('touchstart', (e) => {
      if (e.touches.length === 2) {
        initialDistance = this.getTouchDistance(e.touches[0], e.touches[1]);
        const target = e.target.closest('img');
        if (target) {
          initialScale = parseFloat(target.style.transform?.match(/scale\(([^)]+)\)/)?.[1] || 1);
        }
      }
    }, { passive: true });

    document.addEventListener('touchmove', (e) => {
      if (e.touches.length === 2 && initialDistance) {
        e.preventDefault();
        const currentDistance = this.getTouchDistance(e.touches[0], e.touches[1]);
        const scale = (currentDistance / initialDistance) * initialScale;

        const target = e.target.closest('img');
        if (target && scale > 0.5 && scale < 3) {
          target.style.transform = `scale(${scale})`;
          target.style.transformOrigin = 'center center';
        }
      }
    }, { passive: false });

    document.addEventListener('touchend', (e) => {
      if (e.touches.length < 2) {
        initialDistance = null;
      }
    }, { passive: true });
  }

  getTouchDistance(touch1, touch2) {
    const dx = touch1.clientX - touch2.clientX;
    const dy = touch1.clientY - touch2.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  handleSwipe(direction) {
    // Handle swipe gestures for navigation
    const currentImage = document.querySelector('.media-modal img, .media-detail img');
    if (currentImage) {
      // Find next/previous image in gallery
      const images = Array.from(document.querySelectorAll('.media-card img, .media-thumbnail img'));
      const currentIndex = images.findIndex(img => img.src === currentImage.src);

      if (direction === 'left' && currentIndex < images.length - 1) {
        // Swipe left - next image
        this.navigateToImage(images[currentIndex + 1]);
      } else if (direction === 'right' && currentIndex > 0) {
        // Swipe right - previous image
        this.navigateToImage(images[currentIndex - 1]);
      }
    }
  }

  navigateToImage(imgElement) {
    // Navigate to the image (could trigger modal or page navigation)
    if (imgElement.closest('a')) {
      imgElement.closest('a').click();
    } else {
      // Fallback - could implement custom navigation
      console.log('Navigate to image:', imgElement.src);
    }
  }

  // Camera integration for mobile uploads
  async requestCameraAccess() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' } // Use back camera by default
      });

      // Don't show notification on upload page - handled by upload page logic
      if (!window.location.pathname.includes('/upload')) {
        this.showNotification('Camera access granted! You can now take photos.', 'success');
      }
      return stream;
    } catch (error) {
      console.error('Camera access denied:', error);
      // Don't show notification on upload page - handled by upload page logic
      if (!window.location.pathname.includes('/upload')) {
        this.showNotification('Camera access is required for photo capture.', 'error');
      }
      return null;
    }
  }

  // Capture photo from camera
  async capturePhoto() {
    const stream = await this.requestCameraAccess();
    if (!stream) return null;

    // Create video element to show camera feed
    const video = document.createElement('video');
    video.srcObject = stream;
    video.autoplay = true;
    video.playsInline = true; // Important for iOS

    // Create canvas for capturing the photo
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    return new Promise((resolve) => {
      video.onloadedmetadata = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw current video frame to canvas
        context.drawImage(video, 0, 0);

        // Convert to blob
        canvas.toBlob((blob) => {
          // Stop camera stream
          stream.getTracks().forEach(track => track.stop());

          resolve(blob);
        }, 'image/jpeg', 0.8);
      };
    });
  }

  // Add file to offline upload queue via service worker
  async addToOfflineQueue(file, metadata = {}) {
    if (!this.registration) {
      console.error('Service worker not registered');
      return;
    }

    // Create FormData for the upload
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));

    // Create a Request object that the service worker can handle
    const request = new Request('/upload/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': this.getCSRFToken()
      }
    });

    // Send to service worker for queuing
    this.registration.active.postMessage({
      type: 'add-to-offline-queue',
      request: {
        url: request.url,
        method: request.method,
        headers: Object.fromEntries(request.headers.entries()),
        body: await request.text(),
        timestamp: Date.now()
      }
    });

    if (!this.isOnline()) {
      // Don't show notification on upload page - handled by upload page logic
      if (!window.location.pathname.includes('/upload')) {
        this.showNotification('Photo added to offline queue. Will upload when connection is restored.', 'info');
      }
    } else {
      this.processOfflineQueue();
    }
  }

  // Process offline upload queue
  async processOfflineQueue() {
    if (!this.isOnline() || this.offlineQueue.length === 0) return;

    // Don't show notification on upload page - handled by upload page logic
    if (!window.location.pathname.includes('/upload')) {
      this.showNotification(`Processing ${this.offlineQueue.length} offline uploads...`, 'info');
    }

    for (const item of this.offlineQueue) {
      try {
        item.status = 'uploading';
        this.saveOfflineQueue();

        // Upload the file (you'll need to implement the actual upload logic)
        await this.uploadFile(item.file, item.metadata);

        item.status = 'completed';
        // Don't show notification on upload page - handled by upload page logic
        if (!window.location.pathname.includes('/upload')) {
          this.showNotification('Photo uploaded successfully!', 'success');
        }

      } catch (error) {
        console.error('Upload failed:', error);
        item.status = 'failed';
        item.error = error.message;
        // Don't show notification on upload page - handled by upload page logic
        if (!window.location.pathname.includes('/upload')) {
          this.showNotification('Upload failed. Will retry later.', 'error');
        }
      }
    }

    // Remove completed items
    this.offlineQueue = this.offlineQueue.filter(item => item.status !== 'completed');
    this.saveOfflineQueue();
  }

  // Placeholder for actual upload logic
  async uploadFile(file, metadata) {
    // This should be replaced with your actual upload API call
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));

    const response = await fetch('/upload/', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': this.getCSRFToken()
      }
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  getCSRFToken() {
    // Get CSRF token from cookie or meta tag
    const token = document.querySelector('meta[name="csrf-token"]')?.content ||
                  document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1];
    return token || '';
  }

  saveOfflineQueue() {
    try {
      localStorage.setItem('photoAlbum_offlineQueue', JSON.stringify(this.offlineQueue));
    } catch (e) {
      console.error('Failed to save offline queue:', e);
    }
  }

  showInstallButton() {
    // Create install button if it doesn't exist
    if (!document.getElementById('pwa-install-btn')) {
      const installBtn = document.createElement('button');
      installBtn.id = 'pwa-install-btn';
      installBtn.innerHTML = '<i class="material-icons">get_app</i> Install App';
      installBtn.className = 'btn btn-primary pwa-install-btn';
      installBtn.onclick = () => this.installPWA();

      // Add to page (you can customize where this appears)
      const header = document.querySelector('.app-bar') || document.body;
      header.appendChild(installBtn);

      // Add styles
      const style = document.createElement('style');
      style.textContent = `
        .pwa-install-btn {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 1000;
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
          animation: slideUp 0.3s ease-out;
        }

        @keyframes slideUp {
          from { transform: translateY(100px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }

        @media (max-width: 768px) {
          .pwa-install-btn {
            bottom: 15px;
            right: 15px;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }

  hideInstallButton() {
    const installBtn = document.getElementById('pwa-install-btn');
    if (installBtn) {
      installBtn.style.animation = 'slideUp 0.3s ease-out reverse';
      setTimeout(() => installBtn.remove(), 300);
    }
    this.deferredPrompt = null;
  }

  async installPWA() {
    if (!this.deferredPrompt) {
      console.log('No install prompt available');
      return;
    }

    this.deferredPrompt.prompt();
    const { outcome } = await this.deferredPrompt.userChoice;

    console.log(`User response to install prompt: ${outcome}`);
    this.deferredPrompt = null;
    this.hideInstallButton();
  }

  // Utility method to check online status
  isOnline() {
    return navigator.onLine;
  }

  // Show offline notification
  showOfflineNotification() {
    if (!this.isOnline() && !window.location.pathname.includes('/upload')) {
      this.showNotification('You are currently offline. Some features may not be available.', 'warning');
    }
  }

  // Helper method to get notification title based on type
  getNotificationTitle(type) {
    switch (type) {
      case 'success': return 'Success';
      case 'error': return 'Error';
      case 'warning': return 'Warning';
      case 'info':
      default: return 'Information';
    }
  }

  // Generic notification system
  showNotification(message, type = 'info') {
    console.log('PWA showNotification called:', message, 'on page:', window.location.pathname);

    // Check if we're on the upload page and use the enhanced message system
    if (window.location.pathname.includes('/upload')) {
      console.log('On upload page, checking for showUploadMessage function...');
      // Wait for the upload page JavaScript to load, then use enhanced messages
      if (typeof window.showUploadMessage === 'function') {
        console.log('Using enhanced message system');
        window.showUploadMessage(type, this.getNotificationTitle(type), message);
        return;
      } else {
        console.log('showUploadMessage not available yet, will retry...');
        // If showUploadMessage isn't available yet, try again with longer delays
        let retryCount = 0;
        const maxRetries = 10;
        const retryInterval = 200; // 200ms intervals
        
        const retryCheck = () => {
          retryCount++;
          if (typeof window.showUploadMessage === 'function') {
            console.log('Using enhanced message system (delayed, attempt', retryCount, ')');
            window.showUploadMessage(type, this.getNotificationTitle(type), message);
            return;
          } else if (retryCount < maxRetries) {
            setTimeout(retryCheck, retryInterval);
          } else {
            console.log('showUploadMessage still not available after', maxRetries, 'attempts, falling back to PWA notification');
          }
        };
        
        setTimeout(retryCheck, retryInterval);
      }
    }

    console.log('Using PWA notification system');
    const notification = document.createElement('div');
    notification.className = `pwa-notification pwa-notification-${type}`;
    notification.innerHTML = `
      <div class="pwa-notification-content">
        <span>${message}</span>
        <button class="pwa-notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
    `;

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
      .pwa-notification {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1001;
        min-width: 300px;
        max-width: 500px;
        animation: slideDown 0.3s ease-out;
      }

      .pwa-notification-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      }

      .pwa-notification-info {
        background: var(--primary-main, #90caf9);
        color: #000;
      }

      .pwa-notification-warning {
        background: #ff9800;
        color: #000;
      }

      .pwa-notification-error {
        background: #f44336;
        color: #fff;
      }

      .pwa-notification-success {
        background: #4caf50;
        color: #fff;
      }

      .pwa-notification-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        margin-left: 1rem;
      }

      @keyframes slideDown {
        from { transform: translate(-50%, -100%); opacity: 0; }
        to { transform: translate(-50%, 0); opacity: 1; }
      }

      @media (max-width: 768px) {
        .pwa-notification {
          left: 10px;
          right: 10px;
          transform: none;
          min-width: auto;
        }
      }
    `;
    document.head.appendChild(style);

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds (but not for upload-related messages)
    if (!window.location.pathname.includes('/upload')) {
      setTimeout(() => {
        if (notification.parentElement) {
          notification.style.animation = 'slideDown 0.3s ease-out reverse';
          setTimeout(() => notification.remove(), 300);
        }
      }, 5000);
    }
  }
}

// Initialize PWA handler when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.pwaHandler = new PWAHandler();

  // Show offline notification if needed
  setTimeout(() => {
    window.pwaHandler.showOfflineNotification();
  }, 1000);

  // Listen for online/offline events
  window.addEventListener('online', () => {
    // Don't show notification on upload page - handled by upload page logic
    if (!window.location.pathname.includes('/upload')) {
      window.pwaHandler.showNotification('You are back online!', 'success');
    }
  });

  window.addEventListener('offline', () => {
    // Don't show notification on upload page - handled by upload page logic
    if (!window.location.pathname.includes('/upload')) {
      window.pwaHandler.showNotification('You are offline. Some features may not be available.', 'warning');
    }
  });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PWAHandler;
}
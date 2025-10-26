// Slideshow functionality for photo albums
(function() {
    'use strict';

    const slideshow = {
        modal: null,
        image: null,
        caption: null,
        counter: null,
        progressBar: null,
        playPauseBtn: null,
        speedSelect: null,
        photos: [],
        currentIndex: 0,
        isPlaying: false,
        interval: null,
        speed: 5000,
        progressInterval: null,

        init() {
            this.modal = document.getElementById('slideshow-modal');
            this.image = document.getElementById('slideshow-image');
            this.caption = document.getElementById('slideshow-caption');
            this.counter = document.getElementById('slideshow-counter');
            this.progressBar = document.getElementById('slideshow-progress-bar');
            this.playPauseBtn = document.getElementById('slideshow-play-pause');
            this.speedSelect = document.getElementById('slideshow-speed');

            // Get photos from current page
            this.loadPhotosFromPage();

            // Event listeners
            document.getElementById('slideshow-btn')?.addEventListener('click', () => this.start());
            document.getElementById('slideshow-close')?.addEventListener('click', () => this.close());
            document.getElementById('slideshow-prev')?.addEventListener('click', () => this.previous());
            document.getElementById('slideshow-next')?.addEventListener('click', () => this.next());
            this.playPauseBtn?.addEventListener('click', () => this.togglePlay());
            document.getElementById('slideshow-fullscreen')?.addEventListener('click', () => this.toggleFullscreen());
            this.speedSelect?.addEventListener('change', (e) => this.changeSpeed(parseInt(e.target.value)));

            // Keyboard controls
            document.addEventListener('keydown', (e) => this.handleKeyboard(e));

            // Handle fullscreen change
            document.addEventListener('fullscreenchange', () => this.handleFullscreenChange());
        },

        loadPhotosFromPage() {
            // Get all photo items from the current page (excluding videos)
            const mediaCards = document.querySelectorAll('.media-card[data-media-type="Photo"]');
            this.photos = [];
            
            mediaCards.forEach(card => {
                const link = card.querySelector('.media-link');
                const img = card.querySelector('.media-thumbnail');
                const title = card.querySelector('.media-title');
                const mediaId = card.getAttribute('data-media-id');
                
                if (link && img && mediaId) {
                    this.photos.push({
                        id: mediaId,
                        url: link.href,
                        thumbnailUrl: img.src,
                        title: title ? title.textContent.trim() : 'Untitled'
                    });
                }
            });

            console.log(`Loaded ${this.photos.length} photos for slideshow`);
        },

        async start() {
            if (this.photos.length === 0) {
                alert('No photos available for slideshow. Slideshow only works with photos, not videos.');
                return;
            }

            this.currentIndex = 0;
            this.modal.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
            
            await this.loadAndShowPhoto(this.currentIndex);
            this.play();
        },

        async loadAndShowPhoto(index) {
            const photo = this.photos[index];
            
            // Fetch the photo detail page to get the large image URL
            try {
                const response = await fetch(photo.url);
                const html = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                // Try to find the large image - look for the main photo in detail view
                const largeImg = doc.querySelector('.photo-detail-image img') || 
                               doc.querySelector('.photo-container img') ||
                               doc.querySelector('img[src*="photos/"]');
                
                const imageUrl = largeImg ? largeImg.src : photo.thumbnailUrl;
                
                // Load the image
                this.image.src = imageUrl;
                this.caption.textContent = photo.title;
                this.updateCounter();
                
                // Preload next image
                if (index + 1 < this.photos.length) {
                    const nextPhoto = this.photos[index + 1];
                    const preloadImg = new Image();
                    preloadImg.src = nextPhoto.thumbnailUrl;
                }
                
            } catch (error) {
                console.error('Error loading photo:', error);
                this.image.src = photo.thumbnailUrl;
                this.caption.textContent = photo.title;
                this.updateCounter();
            }
        },

        play() {
            if (this.isPlaying) return;
            
            this.isPlaying = true;
            this.playPauseBtn.querySelector('i').textContent = 'pause';
            this.startProgress();
            
            this.interval = setInterval(() => {
                this.next();
            }, this.speed);
        },

        pause() {
            this.isPlaying = false;
            this.playPauseBtn.querySelector('i').textContent = 'play_arrow';
            this.stopProgress();
            
            if (this.interval) {
                clearInterval(this.interval);
                this.interval = null;
            }
        },

        togglePlay() {
            if (this.isPlaying) {
                this.pause();
            } else {
                this.play();
            }
        },

        next() {
            this.currentIndex = (this.currentIndex + 1) % this.photos.length;
            this.loadAndShowPhoto(this.currentIndex);
            
            // Reset progress if playing
            if (this.isPlaying) {
                this.stopProgress();
                this.startProgress();
            }
        },

        previous() {
            this.currentIndex = (this.currentIndex - 1 + this.photos.length) % this.photos.length;
            this.loadAndShowPhoto(this.currentIndex);
            
            // Reset progress if playing
            if (this.isPlaying) {
                this.stopProgress();
                this.startProgress();
            }
        },

        startProgress() {
            this.progressBar.style.width = '0%';
            const startTime = Date.now();
            
            this.progressInterval = setInterval(() => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min((elapsed / this.speed) * 100, 100);
                this.progressBar.style.width = progress + '%';
            }, 50);
        },

        stopProgress() {
            if (this.progressInterval) {
                clearInterval(this.progressInterval);
                this.progressInterval = null;
            }
            this.progressBar.style.width = '0%';
        },

        changeSpeed(newSpeed) {
            this.speed = newSpeed;
            
            // Restart interval if playing
            if (this.isPlaying) {
                if (this.interval) {
                    clearInterval(this.interval);
                }
                this.stopProgress();
                this.startProgress();
                
                this.interval = setInterval(() => {
                    this.next();
                }, this.speed);
            }
        },

        updateCounter() {
            this.counter.textContent = `${this.currentIndex + 1} / ${this.photos.length}`;
        },

        toggleFullscreen() {
            if (!document.fullscreenElement) {
                this.modal.requestFullscreen().catch(err => {
                    console.error('Error entering fullscreen:', err);
                });
            } else {
                document.exitFullscreen();
            }
        },

        handleFullscreenChange() {
            const icon = document.querySelector('#slideshow-fullscreen i');
            if (document.fullscreenElement) {
                icon.textContent = 'fullscreen_exit';
            } else {
                icon.textContent = 'fullscreen';
            }
        },

        handleKeyboard(e) {
            if (this.modal.style.display !== 'flex') return;

            switch(e.key) {
                case 'Escape':
                    this.close();
                    break;
                case ' ':
                case 'Spacebar':
                    e.preventDefault();
                    this.togglePlay();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.previous();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.next();
                    break;
                case 'f':
                case 'F':
                    e.preventDefault();
                    this.toggleFullscreen();
                    break;
            }
        },

        close() {
            this.pause();
            this.modal.style.display = 'none';
            document.body.style.overflow = '';
            
            // Exit fullscreen if active
            if (document.fullscreenElement) {
                document.exitFullscreen();
            }
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => slideshow.init());
    } else {
        slideshow.init();
    }
})();

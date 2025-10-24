/**
 * Advanced Lazy Loading Module for Photo Album
 * Features:
 * - Intersection Observer API for performance
 * - Progressive loading with blur effects
 * - Loading placeholders
 * - Error handling
 * - Multiple image formats support
 */

class LazyImageLoader {
    constructor(options = {}) {
        this.options = {
            rootMargin: '50px 0px',
            threshold: 0.1,
            placeholderClass: 'lazy-placeholder',
            loadingClass: 'lazy-loading',
            loadedClass: 'lazy-loaded',
            errorClass: 'lazy-error',
            blurEffect: true,
            ...options
        };

        this.observer = null;
        this.init();
    }

    init() {
        // Create Intersection Observer
        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this),
            {
                rootMargin: this.options.rootMargin,
                threshold: this.options.threshold
            }
        );

        // Find all lazy images and observe them
        this.observeImages();
    }

    observeImages() {
        // Find images with data-src attribute (our lazy loading marker)
        const lazyImages = document.querySelectorAll('img[data-src]');

        lazyImages.forEach(img => {
            // Add placeholder class
            img.classList.add(this.options.placeholderClass);

            // Create loading placeholder if blur effect is enabled
            if (this.options.blurEffect) {
                this.createBlurPlaceholder(img);
            }

            // Start observing
            this.observer.observe(img);
        });
    }

    createBlurPlaceholder(img) {
        // Create a small blurred version for progressive loading
        const placeholder = document.createElement('div');
        placeholder.className = 'blur-placeholder';
        placeholder.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, #f0f0f0, #e0e0e0);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-size: 14px;
        `;
        placeholder.innerHTML = '<i class="material-icons" style="font-size: 24px;">image</i>';

        // Wrap image in container if not already wrapped
        if (!img.parentElement.classList.contains('lazy-container')) {
            const container = document.createElement('div');
            container.className = 'lazy-container';
            container.style.cssText = `
                position: relative;
                overflow: hidden;
                background: #f5f5f5;
            `;

            img.parentElement.insertBefore(container, img);
            container.appendChild(placeholder);
            container.appendChild(img);
        }
    }

    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                this.loadImage(img);
                this.observer.unobserve(img);
            }
        });
    }

    loadImage(img) {
        const src = img.dataset.src;
        const srcset = img.dataset.srcset;
        const sizes = img.dataset.sizes;

        if (!src) return;

        // Add loading class
        img.classList.add(this.options.loadingClass);

        // Set up load event
        img.onload = () => {
            this.onImageLoad(img);
        };

        img.onerror = () => {
            this.onImageError(img);
        };

        // Set the actual source
        if (srcset) {
            img.srcset = srcset;
        }
        if (sizes) {
            img.sizes = sizes;
        }
        img.src = src;

        // Remove data attributes
        delete img.dataset.src;
        delete img.dataset.srcset;
        delete img.dataset.sizes;
    }

    onImageLoad(img) {
        // Remove loading class and add loaded class
        img.classList.remove(this.options.loadingClass);
        img.classList.add(this.options.loadedClass);

        // Handle blur effect
        if (this.options.blurEffect) {
            this.handleBlurEffect(img);
        }

        // Remove placeholder
        const container = img.closest('.lazy-container');
        if (container) {
            const placeholder = container.querySelector('.blur-placeholder');
            if (placeholder) {
                placeholder.style.opacity = '0';
                setTimeout(() => {
                    placeholder.remove();
                }, 300);
            }
        }

        // Trigger custom event
        const event = new CustomEvent('lazyImageLoaded', { detail: { img } });
        document.dispatchEvent(event);
    }

    handleBlurEffect(img) {
        // Add initial blur
        img.style.filter = 'blur(10px)';
        img.style.transform = 'scale(1.1)';

        // Remove blur after a short delay
        setTimeout(() => {
            img.style.transition = 'filter 0.3s ease, transform 0.3s ease';
            img.style.filter = 'blur(0px)';
            img.style.transform = 'scale(1)';
        }, 100);
    }

    onImageError(img) {
        // Add error class
        img.classList.add(this.options.errorClass);
        img.classList.remove(this.options.loadingClass);

        // Show error placeholder
        const container = img.closest('.lazy-container');
        if (container) {
            const placeholder = container.querySelector('.blur-placeholder');
            if (placeholder) {
                placeholder.innerHTML = '<i class="material-icons" style="font-size: 24px; color: #f44336;">broken_image</i>';
                placeholder.style.background = 'linear-gradient(45deg, #ffebee, #ffcdd2)';
            }
        }

        // Trigger custom event
        const event = new CustomEvent('lazyImageError', { detail: { img } });
        document.dispatchEvent(event);
    }

    // Method to manually trigger loading of specific images
    loadImageNow(selector) {
        const images = document.querySelectorAll(selector);
        images.forEach(img => {
            if (img.dataset.src) {
                this.loadImage(img);
                this.observer.unobserve(img);
            }
        });
    }

    // Method to refresh observer for dynamically added images
    refresh() {
        this.observeImages();
    }

    // Cleanup method
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check the URL query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const sortOrder = urlParams.get('sort');

    // ** CRITICAL FIX **
    // Do not initialize the lazy loader if custom sorting is active,
    // as it conflicts with the SortableJS library by modifying the DOM.
    if (sortOrder !== 'order') {
        // Initialize lazy loading for the entire page
        window.lazyImageLoader = new LazyImageLoader({
            blurEffect: true,
            rootMargin: '100px 0px' // Load images 100px before they enter viewport
        });
        console.log('Lazy Image Loader initialized');
    } else {
        console.log('Lazy Image Loader disabled for custom sorting.');
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LazyImageLoader;
}
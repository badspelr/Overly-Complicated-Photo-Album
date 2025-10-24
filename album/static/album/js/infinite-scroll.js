// Infinite Scroll for Album Detail Page
(function() {
    'use strict';

    const infiniteScroll = {
        sentinel: null,
        mediaContainer: null,
        loadingIndicator: null,
        observer: null,
        isLoading: false,
        currentPage: 1,
        hasNextPage: true,
        nextPageUrl: null,

        init() {
            // Get DOM elements
            this.sentinel = document.getElementById('sentinel');
            this.mediaContainer = document.getElementById('media-container');
            this.loadingIndicator = document.getElementById('loading-indicator');

            if (!this.sentinel || !this.mediaContainer) {
                console.log('Infinite scroll: Required elements not found');
                return;
            }

            // Get initial pagination state from the page
            this.currentPage = this.getCurrentPageFromUrl();
            this.updatePaginationState();

            // Hide traditional pagination (keep as fallback in HTML for SEO/accessibility)
            this.hidePagination();

            // Set up Intersection Observer
            this.setupObserver();

            console.log('Infinite scroll initialized, starting page:', this.currentPage);
        },

        getCurrentPageFromUrl() {
            const urlParams = new URLSearchParams(window.location.search);
            return parseInt(urlParams.get('page')) || 1;
        },

        updatePaginationState() {
            // Check if there's a next page link in the pagination
            const nextPageLink = document.querySelector('.pagination .page-item:not(.disabled) a[aria-label="Next"]');
            
            if (nextPageLink) {
                this.hasNextPage = true;
                this.nextPageUrl = nextPageLink.href;
                console.log('Next page URL:', this.nextPageUrl);
            } else {
                this.hasNextPage = false;
                this.nextPageUrl = null;
                console.log('No more pages available');
            }
        },

        hidePagination() {
            const paginationNav = document.querySelector('nav[aria-label="Media pagination"]');
            if (paginationNav) {
                paginationNav.style.display = 'none';
            }
        },

        setupObserver() {
            const options = {
                root: null,
                rootMargin: '200px', // Start loading 200px before sentinel is visible
                threshold: 0.1
            };

            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && this.hasNextPage && !this.isLoading) {
                        this.loadNextPage();
                    }
                });
            }, options);

            this.observer.observe(this.sentinel);
        },

        async loadNextPage() {
            if (this.isLoading || !this.hasNextPage || !this.nextPageUrl) {
                return;
            }

            this.isLoading = true;
            this.showLoading();

            try {
                console.log('Loading next page:', this.nextPageUrl);
                
                const response = await fetch(this.nextPageUrl);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const html = await response.text();
                
                // Parse the HTML response
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');

                // Extract new media items
                const newMediaContainer = doc.getElementById('media-container');
                
                if (newMediaContainer) {
                    const newMediaItems = newMediaContainer.innerHTML;
                    
                    // Append new items to existing container
                    this.mediaContainer.insertAdjacentHTML('beforeend', newMediaItems);
                    
                    // Update page counter
                    this.currentPage++;
                    
                    // Update pagination state for next load
                    const nextPageLink = doc.querySelector('.pagination .page-item:not(.disabled) a[aria-label="Next"]');
                    
                    if (nextPageLink) {
                        this.hasNextPage = true;
                        this.nextPageUrl = nextPageLink.href;
                        console.log('Next page URL updated:', this.nextPageUrl);
                    } else {
                        this.hasNextPage = false;
                        this.nextPageUrl = null;
                        console.log('Reached last page');
                        this.showEndMessage();
                    }

                    // Reinitialize any scripts that need to run on new items
                    this.reinitializeScripts();
                    
                    // Update URL without page reload (for better UX and back button)
                    const url = new URL(this.nextPageUrl);
                    window.history.replaceState({}, '', url);
                    
                } else {
                    console.error('Could not find media container in response');
                    this.hasNextPage = false;
                }

            } catch (error) {
                console.error('Error loading next page:', error);
                this.showError();
                this.hasNextPage = false;
            } finally {
                this.isLoading = false;
                this.hideLoading();
            }
        },

        showLoading() {
            if (this.loadingIndicator) {
                this.loadingIndicator.style.display = 'flex';
            }
        },

        hideLoading() {
            if (this.loadingIndicator) {
                this.loadingIndicator.style.display = 'none';
            }
        },

        showEndMessage() {
            // Replace loading indicator with "end of content" message
            if (this.loadingIndicator) {
                this.loadingIndicator.innerHTML = `
                    <div class="end-of-content">
                        <i class="material-icons">check_circle</i>
                        <p>You've reached the end of this album</p>
                    </div>
                `;
                this.loadingIndicator.style.display = 'flex';
            }
        },

        showError() {
            if (this.loadingIndicator) {
                this.loadingIndicator.innerHTML = `
                    <div class="load-error">
                        <i class="material-icons">error_outline</i>
                        <p>Unable to load more photos. Please refresh the page.</p>
                    </div>
                `;
                this.loadingIndicator.style.display = 'flex';
            }
        },

        reinitializeScripts() {
            // Reinitialize lazy loading for new images
            if (window.lazyLoadImages) {
                window.lazyLoadImages();
            }

            // Reinitialize favorite buttons for new items
            if (window.initializeFavorites) {
                window.initializeFavorites();
            }

            // Dispatch custom event for other scripts to hook into
            const event = new CustomEvent('infiniteScrollLoaded', {
                detail: { page: this.currentPage }
            });
            document.dispatchEvent(event);
        },

        destroy() {
            if (this.observer) {
                this.observer.disconnect();
            }
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => infiniteScroll.init());
    } else {
        infiniteScroll.init();
    }

    // Expose to window for other scripts
    window.infiniteScroll = infiniteScroll;

})();

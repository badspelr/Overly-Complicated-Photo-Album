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
        loadedPages: new Set(),
        sessionKey: null,

        async init() {
            // Get DOM elements
            this.sentinel = document.getElementById('sentinel');
            this.mediaContainer = document.getElementById('media-container');
            this.loadingIndicator = document.getElementById('loading-indicator');

            if (!this.sentinel || !this.mediaContainer) {
                console.log('Infinite scroll: Required elements not found');
                return;
            }

            // Create unique session key based on current URL path and filters
            this.sessionKey = 'infiniteScroll_' + window.location.pathname + window.location.search.replace(/[?&]page=\d+/, '');

            // Check if we're restoring from a previous session
            const restored = await this.restoreSession();

            if (!restored) {
                // No restoration - normal initialization
                // Get initial pagination state from the page
                this.currentPage = this.getCurrentPageFromUrl();
                this.loadedPages.add(this.currentPage);
                this.updatePaginationState();
                
                console.log('Infinite scroll initialized, starting page:', this.currentPage);
            } else {
                console.log('Session restored, now on page:', this.currentPage);
            }

            // Hide traditional pagination (keep as fallback in HTML for SEO/accessibility)
            this.hidePagination();

            // Set up Intersection Observer
            this.setupObserver();

            // Save session on scroll
            window.addEventListener('scroll', () => this.saveSession());
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
            if (this.isLoading || !this.hasNextPage) {
                console.log('Cannot load next page:', { isLoading: this.isLoading, hasNextPage: this.hasNextPage });
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
                    this.loadedPages.add(this.currentPage);
                    
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
                    const url = new URL(this.nextPageUrl || window.location.href);
                    if (this.nextPageUrl) {
                        window.history.replaceState({}, '', url);
                    }
                    
                    // Save session after successful load
                    this.saveSession();
                    
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
        },

        reset() {
            // Reset state
            this.isLoading = false;
            this.currentPage = this.getCurrentPageFromUrl();
            this.loadedPages.add(this.currentPage);
            this.updatePaginationState();
            
            // Restart observer
            if (this.observer && this.sentinel) {
                this.observer.observe(this.sentinel);
            }
            
            console.log('Infinite scroll reset, current page:', this.currentPage);
        },

        saveSession() {
            if (!this.sessionKey) return;
            
            const sessionData = {
                scrollPosition: window.scrollY,
                loadedPages: Array.from(this.loadedPages),
                currentPage: this.currentPage,
                timestamp: Date.now()
            };
            
            try {
                sessionStorage.setItem(this.sessionKey, JSON.stringify(sessionData));
            } catch (e) {
                console.warn('Failed to save scroll session:', e);
            }
        },

        async restoreSession() {
            if (!this.sessionKey) return false;
            
            const savedData = sessionStorage.getItem(this.sessionKey);
            if (!savedData) return false;

            try {
                const data = JSON.parse(savedData);
                
                // Check if session is recent (within 10 minutes)
                if (Date.now() - data.timestamp > 600000) {
                    sessionStorage.removeItem(this.sessionKey);
                    return false;
                }

                // Check if we're navigating back (URL has page param but we have saved session)
                const urlPage = this.getCurrentPageFromUrl();
                if (urlPage === 1 || !data.loadedPages || data.loadedPages.length <= 1) {
                    // No need to restore, we're on page 1 or no pages were loaded
                    return false;
                }

                console.log('Restoring infinite scroll session:', data);

                // Clear the URL to page 1 first
                const url = new URL(window.location.href);
                url.searchParams.delete('page');
                window.history.replaceState({}, '', url.toString());

                this.isLoading = true;
                
                // Start from page 1, load pages 2 through the max loaded page
                this.currentPage = 1;
                this.loadedPages.add(1);
                
                // Update pagination state from current page 1 DOM
                this.updatePaginationState();
                
                // Load all previously loaded pages in sequence (starting from page 2)
                const maxPage = Math.max(...data.loadedPages);
                for (let page = 2; page <= maxPage; page++) {
                    try {
                        if (!this.nextPageUrl) {
                            console.warn('No next page URL available at page', this.currentPage);
                            break;
                        }
                        
                        console.log('Restoring page', page);
                        const response = await fetch(this.nextPageUrl);
                        
                        if (!response.ok) {
                            console.error('Failed to fetch page', page);
                            break;
                        }

                        const html = await response.text();
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const newMediaContainer = doc.getElementById('media-container');
                        
                        if (newMediaContainer) {
                            const newMediaItems = newMediaContainer.innerHTML;
                            this.mediaContainer.insertAdjacentHTML('beforeend', newMediaItems);
                            this.loadedPages.add(page);
                            this.currentPage = page;
                            
                            // Update next page URL for the next iteration
                            const nextPageLink = doc.querySelector('.pagination .page-item:not(.disabled) a[aria-label="Next"]');
                            if (nextPageLink) {
                                this.nextPageUrl = nextPageLink.href;
                                this.hasNextPage = true;
                            } else {
                                this.hasNextPage = false;
                                this.nextPageUrl = null;
                                break;
                            }
                        } else {
                            console.error('Could not find media container in restored page', page);
                            break;
                        }
                    } catch (e) {
                        console.error('Failed to restore page', page, e);
                        break;
                    }
                }
                
                this.isLoading = false;
                
                // Reinitialize scripts for all loaded content
                this.reinitializeScripts();
                
                // Restore scroll position after content is loaded
                setTimeout(() => {
                    console.log('Restoring scroll position to', data.scrollPosition);
                    window.scrollTo(0, data.scrollPosition);
                }, 100);
                
                return true;
            } catch (e) {
                console.error('Failed to restore session:', e);
                sessionStorage.removeItem(this.sessionKey);
                return false;
            }
        },

        buildPageUrl(pageNum) {
            const url = new URL(window.location.href);
            url.searchParams.set('page', pageNum);
            return url.toString();
        },
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => infiniteScroll.init());
    } else {
        infiniteScroll.init();
    }

    // Handle browser back/forward navigation
    window.addEventListener('pageshow', (event) => {
        if (event.persisted || performance.navigation.type === 2) {
            // Page was loaded from cache (back/forward navigation)
            console.log('Page restored from cache, resetting infinite scroll');
            if (infiniteScroll.mediaContainer) {
                infiniteScroll.reset();
            }
        }
    });

    // Expose to window for other scripts
    window.infiniteScroll = infiniteScroll;

})();
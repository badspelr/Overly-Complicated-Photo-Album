/**
 * Cookie Consent Management
 * 
 * Handles cookie consent banner display and user preferences
 * Uses localStorage as primary storage with cookie fallback
 */

(function() {
    'use strict';
    
    const CookieConsent = {
        /**
         * Get current consent status
         * @returns {string|null} 'accepted', 'essential_only', or null
         */
        getConsent: function() {
            // Check localStorage first (more reliable than cookies)
            const localConsent = localStorage.getItem('cookie_consent');
            if (localConsent) {
                return localConsent;
            }
            
            // Fallback to cookie check
            const value = `; ${document.cookie}`;
            const parts = value.split(`; cookie_consent=`);
            if (parts.length === 2) {
                return parts.pop().split(';').shift();
            }
            
            return null;
        },
        
        /**
         * Set consent preference
         * @param {string} value - 'accepted' or 'essential_only'
         */
        setConsent: function(value) {
            // Store in localStorage (always works)
            localStorage.setItem('cookie_consent', value);
            
            // Also set cookie for cross-tab consistency
            const expires = new Date();
            expires.setTime(expires.getTime() + 365 * 24 * 60 * 60 * 1000); // 1 year
            
            let cookieString = `cookie_consent=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
            
            // Only add Secure flag if on HTTPS
            if (window.location.protocol === 'https:') {
                cookieString += ';Secure';
            }
            
            document.cookie = cookieString;
        },
        
        /**
         * Accept all cookies
         */
        accept: function() {
            this.setConsent('accepted');
            this.hideBanner();
        },
        
        /**
         * Accept only essential cookies
         */
        decline: function() {
            this.setConsent('essential_only');
            this.hideBanner();
        },
        
        /**
         * Hide the consent banner with animation
         */
        hideBanner: function() {
            const banner = document.getElementById('cookieConsentBanner');
            if (banner) {
                banner.style.animation = 'slideDown 0.3s ease-out';
                setTimeout(function() {
                    banner.style.display = 'none';
                }, 300);
            }
        },
        
        /**
         * Show the consent banner (used for preference changes)
         */
        showBanner: function() {
            const banner = document.getElementById('cookieConsentBanner');
            if (banner) {
                banner.style.display = 'flex';
                // Scroll to bottom to show banner
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            }
        },
        
        /**
         * Initialize consent banner on page load
         */
        init: function() {
            window.addEventListener('load', () => {
                const consent = this.getConsent();
                
                if (!consent) {
                    // Show banner after 1 second if no consent exists
                    setTimeout(() => {
                        const banner = document.getElementById('cookieConsentBanner');
                        if (banner) {
                            banner.style.display = 'flex';
                        }
                    }, 1000);
                }
            });
            
            // Inject slide-down animation CSS
            this.injectAnimationCSS();
        },
        
        /**
         * Inject animation CSS for banner hiding
         */
        injectAnimationCSS: function() {
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideDown {
                    from {
                        transform: translateY(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateY(100%);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    };
    
    // Initialize on load
    CookieConsent.init();
    
    // Expose global functions for backwards compatibility
    window.acceptCookies = function() {
        CookieConsent.accept();
    };
    
    window.declineCookies = function() {
        CookieConsent.decline();
    };
    
    window.showCookieSettings = function() {
        CookieConsent.showBanner();
    };
    
    // Export the object for direct use
    window.CookieConsent = CookieConsent;
})();

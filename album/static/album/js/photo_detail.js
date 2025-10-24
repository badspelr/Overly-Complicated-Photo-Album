document.addEventListener('DOMContentLoaded', function() {
    const mainPhoto = document.getElementById('main-photo');
    const fullscreenOverlay = document.getElementById('fullscreen-overlay');
    const fullscreenImage = document.getElementById('fullscreen-image');
    const closeFullscreen = document.getElementById('close-fullscreen');

    if (mainPhoto && fullscreenOverlay && fullscreenImage && closeFullscreen) {
        mainPhoto.addEventListener('click', function() {
            fullscreenImage.src = mainPhoto.src;
            fullscreenOverlay.classList.add('active');
        });

        closeFullscreen.addEventListener('click', function() {
            fullscreenOverlay.classList.remove('active');
        });

        fullscreenOverlay.addEventListener('click', function(e) {
            if (e.target === fullscreenOverlay) {
                fullscreenOverlay.classList.remove('active');
            }
        });
    }

    // --- Contextual Keyboard Shortcuts ---
    document.addEventListener('keydown', function(e) {
        // Ignore shortcuts if user is typing in an input field
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
            return;
        }

        // Left Arrow for previous photo
        if (e.key === 'ArrowLeft') {
            const prevLink = document.querySelector('.nav-prev');
            if (prevLink) {
                e.preventDefault();
                prevLink.click();
            }
        }

        // Right Arrow for next photo
        if (e.key === 'ArrowRight') {
            const nextLink = document.querySelector('.nav-next');
            if (nextLink) {
                e.preventDefault();
                nextLink.click();
            }
        }

        // 'F' key to toggle favorite
        if (e.key.toLowerCase() === 'f') {
            const favoriteButton = document.querySelector('.favorite-btn');
            if (favoriteButton) {
                e.preventDefault();
                favoriteButton.click();
            }
        }
    });
});

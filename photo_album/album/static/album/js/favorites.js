// Favorite functionality for photo and video cards
document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                      document.querySelector('meta[name="csrf-token"]')?.content;
    
    // Handle favorite button clicks
    document.addEventListener('click', function(e) {
        if (e.target.closest('.favorite-btn')) {
            e.preventDefault();
            e.stopPropagation();
            
            const button = e.target.closest('.favorite-btn');
            const photoId = button.dataset.photoId;
            const videoId = button.dataset.videoId;
            
            if (!csrfToken) {
                console.error('CSRF token not found');
                return;
            }
            
            // Determine the URL based on whether it's a photo or video
            let url;
            if (photoId) {
                url = `/photos/${photoId}/favorite/`;
            } else if (videoId) {
                url = `/videos/${videoId}/favorite/`;
            } else {
                console.error('No photo or video ID found');
                return;
            }
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                const icon = button.querySelector('i');
                
                if (data.is_favorited) {
                    button.classList.add('favorited');
                    icon.textContent = 'favorite';
                    button.title = 'Remove from favorites';
                } else {
                    button.classList.remove('favorited');
                    icon.textContent = 'favorite_border';
                    button.title = 'Add to favorites';
                }
            })
            .catch(error => {
                console.error('Error toggling favorite:', error);
            });
        }
    });
});
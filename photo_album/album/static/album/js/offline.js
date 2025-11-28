document.addEventListener('DOMContentLoaded', function() {
    const retryButton = document.querySelector('.retry-btn');
    if (retryButton) {
        retryButton.addEventListener('click', function() {
            window.location.reload();
        });
    }

    function checkOnlineStatus() {
        if (navigator.onLine) {
            // Small delay to ensure connection is stable
            setTimeout(() => {
                if (navigator.onLine) {
                    window.location.href = '/';
                }
            }, 1000);
        }
    }

    // Check status periodically
    setInterval(checkOnlineStatus, 5000);

    // Listen for online event
    window.addEventListener('online', () => {
        checkOnlineStatus();
    });
});
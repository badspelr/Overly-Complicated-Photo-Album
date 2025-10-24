document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('q');

    if (searchInput) {
        document.addEventListener('keydown', function(e) {
            // Ignore shortcut if user is already typing in an input field
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
                return;
            }

            // '/' key to focus search input
            if (e.key === '/') {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // --- Copy to Clipboard ---
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.dataset.copyText;
            copyToClipboard(textToCopy);
        });
    });

    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(function() {
            // Show success message
            const notification = document.createElement('div');
            notification.textContent = 'Link copied to clipboard!';
            notification.classList.add('clipboard-notification');
            document.body.appendChild(notification);
            setTimeout(() => {
                notification.classList.add('fade-out');
                setTimeout(() => document.body.removeChild(notification), 300);
            }, 2000);
        }).catch(function(err) {
            console.error('Failed to copy: ', err);
            alert('Failed to copy to clipboard. Please copy manually.');
        });
    }

    // --- Delete Confirmation ---
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!confirm('Are you sure you want to delete this share link?')) {
                event.preventDefault();
            }
        });
    });
});
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileDrawer = document.getElementById('mobile-drawer');
    const drawerOverlay = document.getElementById('drawer-overlay');

    if (mobileMenuToggle && mobileDrawer && drawerOverlay) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileDrawer.classList.toggle('open');
            drawerOverlay.classList.toggle('show');
        });

        drawerOverlay.addEventListener('click', function() {
            mobileDrawer.classList.remove('open');
            drawerOverlay.classList.remove('show');
        });
    }

    const alertCloseButtons = document.querySelectorAll('.alert-close');
    alertCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            dismissMessage(this);
        });
    });

    // --- Global Keyboard Shortcuts ---
    document.addEventListener('keydown', function(e) {
        // Ignore shortcuts if user is typing in an input field
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
            return;
        }

        if (e.altKey) {
            const shortcut = e.key.toLowerCase();
            const link = document.querySelector(`.nav-list a[data-shortcut="${shortcut}"]`);
            if (link) {
                e.preventDefault();
                link.click();
            }
        }
    });
});

function dismissMessage(button) {
    const message = button.closest('.alert');
    message.style.transition = 'opacity 0.3s';
    message.style.opacity = '0';
    setTimeout(function() {
        message.remove();
    }, 300);
}
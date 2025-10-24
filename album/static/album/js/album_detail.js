document.addEventListener('DOMContentLoaded', function() {
    // --- Toast Notification Utility ---
    function showToast(message) {
        // Remove any existing toasts
        const existingToast = document.querySelector('.toast-notification');
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.textContent = message;
        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);

        // Animate out and remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 500); // Wait for fade out transition
        }, 3000);
    }

    // --- Bulk Action and Edit Functionality ---
    const form = document.getElementById('bulk-action-form');
    const mediaContainer = document.getElementById('media-container');
    
    if (form && mediaContainer) {
        const bulkDeleteUrl = form.dataset.bulkDeleteUrl;
        const bulkDownloadUrl = form.dataset.bulkDownloadUrl;
        const bulkEditUrl = '/api/bulk-edit/';

        // Get buttons and inputs (top and bottom)
        const downloadBtns = document.querySelectorAll('button[name="action"][value="download"]');
        const deleteBtns = document.querySelectorAll('button[name="action"][value="delete"]');
        const downloadDropdownBtn = document.getElementById('download-dropdown-btn');
        const downloadDropdownBtnBottom = document.getElementById('download-dropdown-btn-bottom');
        const categorySelect = document.getElementById('bulk-category-select');
        const updateCategoryBtn = document.getElementById('bulk-update-category-btn');
        const tagsInput = document.getElementById('bulk-tags-input');
        const addTagsBtn = document.getElementById('bulk-add-tags-btn');
        
        // Bottom bar elements
        const stickyBar = document.getElementById('bulk-action-buttons-bottom');
        const selectionCount = document.getElementById('selection-count-bottom');
        const clearSelectionBtn = document.getElementById('clear-selection-bottom');
        const categorySelectBottom = document.getElementById('bulk-category-select-bottom');
        const updateCategoryBtnBottom = document.getElementById('bulk-update-category-btn-bottom');
        const tagsInputBottom = document.getElementById('bulk-tags-input-bottom');
        const addTagsBtnBottom = document.getElementById('bulk-add-tags-btn-bottom');

        function updateButtonState() {
            const checkedBoxes = mediaContainer.querySelectorAll('input[name="media_ids"]:checked:not(:disabled)');
            const hasSelection = checkedBoxes.length > 0;
            const count = checkedBoxes.length;

            // Update all buttons
            downloadBtns.forEach(btn => btn.disabled = !hasSelection);
            if (downloadDropdownBtn) downloadDropdownBtn.disabled = !hasSelection;
            if (downloadDropdownBtnBottom) downloadDropdownBtnBottom.disabled = !hasSelection;
            deleteBtns.forEach(btn => btn.disabled = !hasSelection);
            if (categorySelect) categorySelect.disabled = !hasSelection;
            if (updateCategoryBtn) updateCategoryBtn.disabled = !hasSelection;
            if (tagsInput) tagsInput.disabled = !hasSelection;
            if (addTagsBtn) addTagsBtn.disabled = !hasSelection;
            
            // Update bottom bar
            if (categorySelectBottom) categorySelectBottom.disabled = !hasSelection;
            if (updateCategoryBtnBottom) updateCategoryBtnBottom.disabled = !hasSelection;
            if (tagsInputBottom) tagsInputBottom.disabled = !hasSelection;
            if (addTagsBtnBottom) addTagsBtnBottom.disabled = !hasSelection;
            
            // Show/hide sticky bar and update count
            if (stickyBar) {
                if (hasSelection) {
                    stickyBar.classList.add('active');
                    if (selectionCount) {
                        selectionCount.textContent = `${count} item${count !== 1 ? 's' : ''} selected`;
                    }
                } else {
                    stickyBar.classList.remove('active');
                }
            }
        }
        
        // Clear selection handler
        if (clearSelectionBtn) {
            clearSelectionBtn.addEventListener('click', function() {
                const checkboxes = mediaContainer.querySelectorAll('input[name="media_ids"]:checked');
                checkboxes.forEach(cb => cb.checked = false);
                updateButtonState();
            });
        }

        mediaContainer.addEventListener('change', function(event) {
            if (event.target.matches('input[name="media_ids"]')) {
                updateButtonState();
            }
        });

        form.addEventListener('submit', function(event) {
            const action = event.submitter ? event.submitter.value : null;

            if (action === 'delete') {
                if (!confirm('Are you sure you want to permanently delete the selected items?')) {
                    event.preventDefault();
                } else {
                    form.action = bulkDeleteUrl;
                }
            } else if (action === 'download') {
                form.action = bulkDownloadUrl;
            } else if (action === 'update_category' || action === 'add_tags') {
                event.preventDefault();
                handleBulkEdit(action);
            }
        });

        function handleBulkEdit(action) {
            const checkedBoxes = mediaContainer.querySelectorAll('input[name="media_ids"]:checked:not(:disabled)');
            const media_ids = Array.from(checkedBoxes).map(cb => cb.value);
            let payload = {
                action: action,
                media_ids: media_ids,
            };

            if (action === 'update_category') {
                // Try bottom bar first, then top
                payload.category_id = categorySelectBottom?.value || categorySelect?.value;
            } else if (action === 'add_tags') {
                // Try bottom bar first, then top
                payload.tags = tagsInputBottom?.value || tagsInput?.value;
            }

            fetch(bulkEditUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Bulk edit result:', data);
                alert('Bulk edit successful! The page will now reload.');
                window.location.reload();
            })
            .catch(error => {
                console.error('Error during bulk edit:', error);
                alert('An error occurred during the bulk edit. Please check the console for details.');
            });
        }
        
        updateButtonState(); // Initial state
    }

    // --- Mobile Filter Modal Functionality ---
    const filterToggle = document.getElementById('mobile-filter-toggle');
    const filterModal = document.getElementById('mobile-filter-modal');
    const filterOverlay = document.getElementById('mobile-filter-overlay');
    const filterClose = document.getElementById('mobile-filter-close');
    const filterCancel = document.getElementById('mobile-filter-cancel');

    if (filterToggle && filterModal) {
        const openModal = (e) => {
            e.preventDefault();
            filterModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        };
        filterToggle.addEventListener('click', openModal);
        filterToggle.addEventListener('touchend', openModal);

        const closeModal = () => {
            filterModal.classList.remove('active');
            document.body.style.overflow = '';
        };
        if (filterClose) filterClose.addEventListener('click', closeModal);
        if (filterCancel) filterCancel.addEventListener('click', closeModal);
        if (filterOverlay) filterOverlay.addEventListener('click', closeModal);
        
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && filterModal.classList.contains('active')) {
                closeModal();
            }
        });
    }

    // --- Search Modal Functionality ---
    const searchToggle = document.getElementById('search-modal-toggle');
    const searchModal = document.getElementById('search-modal');
    const searchOverlay = document.getElementById('search-modal-overlay');
    const searchClose = document.getElementById('search-modal-close');
    const searchCancel = document.getElementById('search-modal-cancel');

    if (searchToggle && searchModal) {
        const openSearchModal = (e) => {
            e.preventDefault();
            searchModal.classList.add('active');
            document.body.style.overflow = 'hidden';
            // Focus on search input for better UX
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                setTimeout(() => searchInput.focus(), 100);
            }
        };
        searchToggle.addEventListener('click', openSearchModal);
        searchToggle.addEventListener('touchend', openSearchModal);

        const closeSearchModal = () => {
            searchModal.classList.remove('active');
            document.body.style.overflow = '';
        };
        if (searchClose) searchClose.addEventListener('click', closeSearchModal);
        if (searchCancel) searchCancel.addEventListener('click', closeSearchModal);
        if (searchOverlay) searchOverlay.addEventListener('click', closeSearchModal);
        
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && searchModal.classList.contains('active')) {
                closeSearchModal();
            }
        });
    }

    // --- Dropdown Toggle Functionality ---
    document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Find the dropdown menu - it should be the next sibling
            const dropdownMenu = this.nextElementSibling;
            console.log('Dropdown toggle clicked', dropdownMenu);
            
            if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
                // Close other dropdowns and reset their aria-expanded
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    if (menu !== dropdownMenu) {
                        menu.classList.remove('show');
                        menu.classList.remove('dropdown-menu-up');
                        const otherToggle = menu.previousElementSibling;
                        if (otherToggle) {
                            otherToggle.setAttribute('aria-expanded', 'false');
                        }
                    }
                });
                
                // Toggle current dropdown
                const isShowing = dropdownMenu.classList.toggle('show');
                this.setAttribute('aria-expanded', isShowing ? 'true' : 'false');
                
                if (isShowing) {
                    // Check if dropdown would go off screen
                    const rect = dropdownMenu.getBoundingClientRect();
                    const spaceBelow = window.innerHeight - rect.bottom;
                    const spaceAbove = rect.top;
                    
                    // If not enough space below but more space above, show dropdown upward
                    if (spaceBelow < 0 && spaceAbove > Math.abs(spaceBelow)) {
                        dropdownMenu.classList.add('dropdown-menu-up');
                        console.log('Dropdown positioned upward');
                    } else {
                        dropdownMenu.classList.remove('dropdown-menu-up');
                    }
                }
                
                console.log('Dropdown toggled, showing:', isShowing);
            } else {
                console.warn('Dropdown menu not found or invalid');
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.btn-group')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
                const toggle = menu.previousElementSibling;
                if (toggle && toggle.classList.contains('dropdown-toggle')) {
                    toggle.setAttribute('aria-expanded', 'false');
                }
            });
        }
    });

    // --- Individual Download Functionality ---
    document.querySelectorAll('.download-individual-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Close the dropdown menu
            const dropdownMenu = this.closest('.dropdown-menu');
            if (dropdownMenu) {
                dropdownMenu.classList.remove('show');
                const toggle = dropdownMenu.previousElementSibling;
                if (toggle) {
                    toggle.setAttribute('aria-expanded', 'false');
                }
            }

            const checkedBoxes = document.querySelectorAll('input[name="media_ids"]:checked:not(:disabled)');
            if (checkedBoxes.length === 0) {
                showToast('Please select at least one item to download.');
                return;
            }

            const count = checkedBoxes.length;

            checkedBoxes.forEach((checkbox, index) => {
                const mediaIdWithPrefix = checkbox.value; // e.g., "photo-123"
                const [itemType, mediaId] = mediaIdWithPrefix.split('-');

                if (!itemType || !mediaId) {
                    console.error('Invalid media ID format:', mediaIdWithPrefix);
                    return; // Skip this item
                }

                const url = `/download/${itemType}/${mediaId}/`;

                // Use a timeout to space out the download triggers, making it more reliable
                setTimeout(() => {
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', ''); // The 'download' attribute is key
                    link.style.display = 'none';

                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }, index * 500); // 500ms delay between each download
            });

            // Show a single, non-blocking toast notification
            showToast(`${count} download${count !== 1 ? 's' : ''} started.`);

            // Uncheck boxes and reset UI after downloads are initiated
            setTimeout(() => {
                checkedBoxes.forEach(cb => cb.checked = false);
                updateButtonState();
            }, count * 500 + 200); // Delay slightly longer than the last download
        });
    });

    // --- Utility and Global Listeners ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

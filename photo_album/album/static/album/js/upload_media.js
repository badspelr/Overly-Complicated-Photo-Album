// Scripts extracted from upload_media.html

// Global error handler to prevent page crashes
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    showMessage('An error occurred. Please refresh the page and try again.', 'error');
    
    // Prevent the error from propagating and crashing the page
    e.preventDefault();
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled Promise Rejection:', e.reason);
    showMessage('An unexpected error occurred. Please try again.', 'error');
    
    // Prevent the rejection from propagating
    e.preventDefault();
});

// Wait for DOM to be ready before executing main script
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeUploadScript);
} else {
    // DOM is already ready
    initializeUploadScript();
}

function initializeUploadScript() {
    let selectedFiles = [];

    const uploadForm = document.getElementById("upload-form");
    const submitBtn = document.getElementById("submit-btn");
    
    const dropZone = document.getElementById("drop-zone");
    const dragDropInput = document.getElementById("drag-drop-input");
    
    const selectFilesCard = document.getElementById('select-files-card');
    const individualFilesInput = document.getElementById('individual-files-input');
    
    const selectFolderCard = document.getElementById('select-folder-card');
    const folderInput = document.getElementById('folder-input');
    
    const filePreview = document.getElementById("file-preview");
    const selectedFilesList = document.getElementById("selected-files-list");

    // --- Event Listeners for File Selection ---

    // 1. Main Drop Zone
    if (dropZone) {
        dropZone.addEventListener('click', () => dragDropInput.click());
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            handleFiles(e.dataTransfer.files, true); // Append files on drop
        });
        dragDropInput.addEventListener('change', (e) => handleFiles(e.target.files));
    }

    // 2. Individual Files Card
    if (selectFilesCard) {
        selectFilesCard.addEventListener('click', () => individualFilesInput.click());
        individualFilesInput.addEventListener('change', (e) => handleFiles(e.target.files));
    }

    // 3. Folder Card
    if (selectFolderCard) {
        selectFolderCard.addEventListener('click', () => folderInput.click());
        folderInput.addEventListener('change', (e) => handleFiles(e.target.files));
    }

    // --- Core File Handling Logic ---

    function handleFiles(newFiles, isDragDrop = false) {
        if (!isDragDrop) {
            selectedFiles = []; // Clear previous selection if not appending via drag/drop
        }
        
        Array.from(newFiles).forEach(file => {
            // Prevent duplicates
            if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
                selectedFiles.push(file);
            }
        });
        
        updateFilePreview();
    }

    function updateFilePreview() {
        selectedFilesList.innerHTML = '';
        if (selectedFiles.length > 0) {
            filePreview.style.display = 'block';
            document.getElementById('file-count').textContent = selectedFiles.length;
        } else {
            filePreview.style.display = 'none';
        }

        selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <span class="file-name">${file.name}</span>
                <button type="button" class="remove-btn" data-index="${index}">&times;</button>
            `;
            selectedFilesList.appendChild(fileItem);
        });
    }

    selectedFilesList.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-btn')) {
            const index = parseInt(e.target.dataset.index, 10);
            selectedFiles.splice(index, 1);
            updateFilePreview();
        }
    });

    // --- Form Submission using Fetch ---

    uploadForm.addEventListener("submit", function(e) {
        e.preventDefault(); // Always prevent default submission

        if (selectedFiles.length === 0) {
            showMessage("Please select at least one file.", 'warning');
            return;
        }

        const formData = new FormData();
        
        // Append standard form fields
        formData.append('csrfmiddlewaretoken', uploadForm.querySelector('[name="csrfmiddlewaretoken"]').value);
        formData.append('album', uploadForm.querySelector('[name="album"]').value);
        formData.append('category', uploadForm.querySelector('[name="category"]').value);
        formData.append('title', uploadForm.querySelector('[name="title"]').value);
        formData.append('description', uploadForm.querySelector('[name="description"]').value);

        // Separate files into appropriate fields
        selectedFiles.forEach(file => {
            if (file.webkitRelativePath) {
                formData.append('media_dir', file, file.name);
            } else {
                formData.append('media_files', file, file.name);
            }
        });

        // Visual feedback
        submitBtn.disabled = true;
        submitBtn.textContent = 'Uploading...';
        showMessage(`Uploading ${selectedFiles.length} files...`, 'info');

        // Perform the fetch request
        fetch(uploadForm.action, {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': formData.get('csrfmiddlewaretoken') }
        })
        .then(response => {
            if (response.ok && response.redirected) {
                window.location.href = response.url; // Follow redirect on success
            } else {
                // Handle errors, maybe show a server message
                throw new Error('Upload failed. Please try again.');
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
            showMessage(error.message, 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Upload';
        });
    });

    function showMessage(message, type = 'info') {
        // (Your existing showMessage function)
        console.log(`[${type}] ${message}`);
    }
}

function clearAllMessages() {
    const messages = document.querySelectorAll('.alert, .message, [class*="message"], [class*="alert"]');
    messages.forEach(function(msg) {
        msg.style.display = 'none';
    });
}

// Add error display to page
const errorDisplay = document.createElement('div');
errorDisplay.id = 'js-error-display';
errorDisplay.style.cssText = 'position: fixed; bottom: 10px; left: 10px; background: #f44336; color: white; padding: 10px; border-radius: 4px; z-index: 9999; font-size: 12px; max-width: 400px; display: none;';
document.body.appendChild(errorDisplay);

// Enhanced error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    errorDisplay.style.display = 'block';
    errorDisplay.innerHTML = '<strong>JS Error:</strong><br>' + e.message + '<br><small>' + e.filename + ':' + e.lineno + '</small>';
    showMessage('JavaScript error occurred. Check bottom-left for details.', 'error');

    // Prevent the error from propagating and crashing the page
    e.preventDefault();
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled Promise Rejection:', e.reason);
    errorDisplay.style.display = 'block';
    errorDisplay.innerHTML = '<strong>Promise Error:</strong><br>' + e.reason.message;
    showMessage('Promise error occurred. Check bottom-left for details.', 'error');

    // Prevent the rejection from propagating
    e.preventDefault();
});

// Cache busting and reload logic
(function() {
    if (window.cacheVersion && window.cacheVersion !== 'v{{ "now"|date:"YmdHis" }}') {
        location.reload(true);
    }
    window.cacheVersion = 'v{{ "now"|date:"YmdHis" }}';
})();

// Prevent Django messages from disappearing
setTimeout(function() {
    var messages = document.querySelectorAll('.alert, .message, [class*="message"], [class*="alert"]');
    messages.forEach(function(msg) {
        msg.style.display = 'block !important';
        msg.style.opacity = '1 !important';
        msg.style.visibility = 'visible !important';

        // Remove any auto-hide classes or timeouts
        msg.classList.remove('fade', 'in');
        msg.style.animation = 'none';
        msg.style.transition = 'none';
    });

    // Also check for any message containers
    var containers = document.querySelectorAll('.messages, .django-messages');
    containers.forEach(function(container) {
        container.style.display = 'block !important';
    });
}, 1000); // Wait 1 second for messages to load
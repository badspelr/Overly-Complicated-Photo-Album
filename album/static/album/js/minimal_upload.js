document.addEventListener('DOMContentLoaded', function() {
    // --- File Input Management ---
    const fileInput = document.querySelector('input[name="files"]');
    const fileDisplay = document.getElementById('files-display');
    const dirInput = document.querySelector('input[name="dirfiles"]');
    const dirDisplay = document.getElementById('dirfiles-display');
    const fileCountDisplay = document.getElementById('file-count-display');
    const fileCountText = document.getElementById('file-count-text');
    const uploadSubmitBtn = document.getElementById('upload-submit-btn');

    function updateTotalFileCount() {
        const filesCount = fileInput.files ? fileInput.files.length : 0;
        const dirFilesCount = dirInput.files ? dirInput.files.length : 0;
        const totalFiles = filesCount + dirFilesCount;

        if (totalFiles > 0) {
            fileCountText.textContent = `${totalFiles} file(s) selected`;
            fileCountDisplay.style.display = 'inline-block';
            uploadSubmitBtn.disabled = false;
        } else {
            fileCountDisplay.style.display = 'none';
        }
    }

    if (fileInput && fileDisplay) {
        fileInput.addEventListener('change', function() {
            fileDisplay.value = Array.from(this.files).map(f => f.name).join(', ');
            updateTotalFileCount();
        });
        // Add click listener to the button
        const fileButton = fileInput.previousElementSibling;
        if (fileButton && fileButton.tagName === 'BUTTON') {
            fileButton.addEventListener('click', () => fileInput.click());
        }
    }

    if (dirInput && dirDisplay) {
        dirInput.addEventListener('change', function() {
            dirDisplay.value = Array.from(this.files).map(f => f.webkitRelativePath || f.name).join(', ');
            updateTotalFileCount();
        });
        // Add click listener to the button
        const dirButton = dirInput.previousElementSibling;
        if (dirButton && dirButton.tagName === 'BUTTON') {
            dirButton.addEventListener('click', () => dirInput.click());
        }
    }

    // --- Expand/Collapse for Upload Results ---
    const resultsSections = document.querySelectorAll('.results-section');
    resultsSections.forEach(section => {
        const title = section.querySelector('.section-title');
        const fileList = section.querySelector('.file-list');
        const icon = title.querySelector('.expand-icon');

        if (title && fileList && icon) {
            title.addEventListener('click', () => {
                const isCollapsed = fileList.style.display === 'none';
                fileList.style.display = isCollapsed ? 'block' : 'none';
                icon.textContent = isCollapsed ? 'expand_less' : 'expand_more';
            });
        }
    });
});

// Confirmation dialog for uploads
function confirmUpload(event) {
    const fileInput = document.querySelector('input[name="files"]');
    const dirInput = document.querySelector('input[name="dirfiles"]');
    const albumSelect = document.querySelector('select[name="album"]');
    
    // Check if album is selected
    if (!albumSelect || !albumSelect.value) {
        alert('Please select an album before uploading.');
        event.preventDefault();
        return false;
    }
    
    const filesCount = fileInput && fileInput.files ? fileInput.files.length : 0;
    const dirFilesCount = dirInput && dirInput.files ? dirInput.files.length : 0;
    const totalFiles = filesCount + dirFilesCount;
    
    if (totalFiles === 0) {
        alert('Please select files or a directory to upload.');
        event.preventDefault();
        return false;
    }
    
    let message = `You are about to upload ${totalFiles} file(s):\n\n`;
    
    if (filesCount > 0) {
        message += `• ${filesCount} individual file(s)\n`;
    }
    if (dirFilesCount > 0) {
        message += `• ${dirFilesCount} file(s) from directory\n`;
    }
    
    if (totalFiles > 100) {
        message += `\n⚠️  This is a large upload and may take several minutes.\n`;
    }
    
    message += `\nDo you want to continue?`;
    
    const confirmed = confirm(message);
    
    if (confirmed) {
        // Show progress overlay
        showUploadProgress(totalFiles);
    }
    
    return confirmed;
}

// Show upload progress overlay
function showUploadProgress(fileCount) {
    const overlay = document.getElementById('upload-progress-overlay');
    const fileCountElement = document.getElementById('progress-file-count');
    const messageElement = document.getElementById('progress-message');
    
    if (overlay && fileCountElement) {
        fileCountElement.textContent = fileCount;
        
        // Update message based on file count
        if (fileCount > 1000) {
            messageElement.textContent = 'Uploading a large number of files. This will take several minutes. Please be patient.';
        } else if (fileCount > 100) {
            messageElement.textContent = 'Uploading files. This may take a few minutes depending on file sizes.';
        } else {
            messageElement.textContent = 'Please wait while your files are being uploaded.';
        }
        
        overlay.style.display = 'flex';
    }
}

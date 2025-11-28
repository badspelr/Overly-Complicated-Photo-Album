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

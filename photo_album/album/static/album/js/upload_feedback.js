/**
 * Upload feedback and progress handling for minimal upload form
 */

class UploadFeedback {
    constructor() {
        this.form = document.querySelector('.form-container');
        this.uploadButton = document.querySelector('button[type="submit"]');
        this.fileInput = document.querySelector('input[name="files"]');
        this.dirInput = document.querySelector('input[name="dirfiles"]');
        this.filesDisplay = document.getElementById('files-display');
        this.dirFilesDisplay = document.getElementById('dirfiles-display');
        this.fileCountDisplay = document.getElementById('file-count-display');
        this.fileCountText = document.getElementById('file-count-text');

        this.init();
    }

    init() {
        // Listen for file selections
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => this.handleFileSelection(e, 'files'));
        }

        if (this.dirInput) {
            this.dirInput.addEventListener('change', (e) => this.handleFileSelection(e, 'directory'));
        }

        // Listen for form submission
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Listen for page load (in case of form errors)
        window.addEventListener('load', () => this.resetUploadState());
    }

    handleFileSelection(event, type) {
        const files = event.target.files;
        if (files.length > 0) {
            this.showFileSelected(type, files.length);
            this.updateFileCount();

            // Update the display input
            const displayInput = type === 'directory' ? this.dirFilesDisplay : this.filesDisplay;
            if (displayInput) {
                const fileNames = Array.from(files).map(f =>
                    type === 'directory' ? (f.webkitRelativePath || f.name) : f.name
                );
                displayInput.value = fileNames.join(', ');
            }
        }
    }

    showFileSelected(type, count) {
        // Update button text to show readiness
        if (this.uploadButton) {
            const originalText = this.uploadButton.innerHTML;
            if (!this.uploadButton.dataset.originalText) {
                this.uploadButton.dataset.originalText = originalText;
            }

            if (type === 'directory') {
                this.uploadButton.innerHTML = `<i class="material-icons">folder</i> Upload ${count} Files from Directory`;
                this.uploadButton.classList.add('btn-success');
                this.uploadButton.classList.remove('btn-primary');
            } else {
                this.uploadButton.innerHTML = `<i class="material-icons">attach_file</i> Upload ${count} Files`;
                this.uploadButton.classList.add('btn-info');
                this.uploadButton.classList.remove('btn-primary');
            }
        }
    }

    updateFileCount() {
        const filesCount = this.fileInput?.files?.length || 0;
        const dirFilesCount = this.dirInput?.files?.length || 0;
        const totalCount = filesCount + dirFilesCount;

        if (totalCount > 0 && this.fileCountDisplay && this.fileCountText) {
            this.fileCountDisplay.style.display = 'block';
            this.fileCountText.textContent = `${totalCount} file${totalCount > 1 ? 's' : ''} selected for upload`;
        } else if (this.fileCountDisplay) {
            this.fileCountDisplay.style.display = 'none';
        }
    }

    handleFormSubmit(event) {
        const files = this.fileInput?.files || [];
        const dirFiles = this.dirInput?.files || [];
        const totalFiles = files.length + dirFiles.length;

        if (totalFiles > 0) {
            this.showUploadingState(totalFiles);
            this.updateFileCount();
        }
    }

    showUploadingState(fileCount) {
        if (this.uploadButton) {
            // Disable the button to prevent double submission
            this.uploadButton.disabled = true;

            // Change appearance to show uploading state
            this.uploadButton.innerHTML = `
                <i class="material-icons spinning">cloud_upload</i>
                Uploading ${fileCount} file${fileCount > 1 ? 's' : ''}...
            `;

            this.uploadButton.classList.remove('btn-primary', 'btn-success', 'btn-info');
            this.uploadButton.classList.add('btn-warning');

            // Add a progress indicator
            this.addProgressIndicator();
        }
    }

    addProgressIndicator() {
        // Remove existing progress indicator if any
        const existingProgress = document.querySelector('.upload-progress');
        if (existingProgress) {
            existingProgress.remove();
        }

        // Create progress indicator
        const progressContainer = document.createElement('div');
        progressContainer.className = 'upload-progress';
        progressContainer.innerHTML = `
            <div class="progress-bar-container">
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
                <div class="progress-text">Preparing files...</div>
            </div>
        `;

        // Insert after the form
        if (this.form) {
            this.form.appendChild(progressContainer);
        }
    }

    resetUploadState() {
        if (this.uploadButton) {
            // Re-enable button
            this.uploadButton.disabled = false;

            // Reset to original state
            const originalText = this.uploadButton.dataset.originalText || '<i class="material-icons">cloud_upload</i> Upload Files';
            this.uploadButton.innerHTML = originalText;

            // Reset classes
            this.uploadButton.classList.remove('btn-warning', 'btn-success', 'btn-info');
            this.uploadButton.classList.add('btn-primary');
        }

        // Remove progress indicator
        const progress = document.querySelector('.upload-progress');
        if (progress) {
            progress.remove();
        }

        // Hide file count display
        if (this.fileCountDisplay) {
            this.fileCountDisplay.style.display = 'none';
        }

        // Clear file displays
        if (this.filesDisplay) {
            this.filesDisplay.value = '';
        }
        if (this.dirFilesDisplay) {
            this.dirFilesDisplay.value = '';
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    new UploadFeedback();

    // Add collapsible functionality to results sections
    const sectionTitles = document.querySelectorAll('.section-title');
    sectionTitles.forEach(title => {
        title.style.cursor = 'pointer';
        title.addEventListener('click', function() {
            const fileList = this.nextElementSibling;
            const expandIcon = this.querySelector('.expand-icon');

            if (fileList.style.display === 'none') {
                fileList.style.display = 'flex';
                expandIcon.textContent = 'expand_less';
                this.classList.remove('collapsed');
            } else {
                fileList.style.display = 'none';
                expandIcon.textContent = 'expand_more';
                this.classList.add('collapsed');
            }
        });
    });
});

// Add CSS for upload results animations
const resultsStyle = document.createElement('style');
resultsStyle.textContent = `
    .upload-results-summary {
        animation: slideIn 0.5s ease-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .file-item {
        animation: fadeInUp 0.3s ease-out;
        animation-fill-mode: both;
    }

    .file-item:nth-child(1) { animation-delay: 0.1s; }
    .file-item:nth-child(2) { animation-delay: 0.2s; }
    .file-item:nth-child(3) { animation-delay: 0.3s; }
    .file-item:nth-child(4) { animation-delay: 0.4s; }
    .file-item:nth-child(5) { animation-delay: 0.5s; }
    .file-item:nth-child(n+6) { animation-delay: 0.6s; }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .results-section {
        animation: slideInLeft 0.4s ease-out;
    }

    .success-section { animation-delay: 0.2s; }
    .error-section { animation-delay: 0.4s; }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(resultsStyle);
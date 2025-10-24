/**
 * AI Processing Progress Modal Handler
 * 
 * Generic handler for AI processing workflows (photos, videos, etc.)
 * Shows a modal with progress bar and time estimates during processing
 * 
 * Usage:
 *   const processor = new AIProcessingHandler({
 *       formSelector: '#aiProcessingForm',
 *       modalId: 'processingModal',
 *       storagePrefix: 'aiProcessing',
 *       itemType: 'photo',
 *       itemTypePlural: 'photos',
 *       processingTimePerItem: 0.6, // seconds
 *       getTotalItems: function() { return 100; },
 *       getUnprocessedItems: function() { return 50; }
 *   });
 */

class AIProcessingHandler {
    constructor(config) {
        this.config = {
            formSelector: config.formSelector || '#aiProcessingForm',
            modalId: config.modalId || 'processingModal',
            storagePrefix: config.storagePrefix || 'aiProcessing',
            itemType: config.itemType || 'item',
            itemTypePlural: config.itemTypePlural || 'items',
            processingTimePerItem: config.processingTimePerItem || 1.0,
            getTotalItems: config.getTotalItems || (() => 0),
            getUnprocessedItems: config.getUnprocessedItems || (() => 0),
            submitButtonSelector: config.submitButtonSelector || 'button[type="submit"]',
            submitButtonProcessingHTML: config.submitButtonProcessingHTML || '<span class="icon">⏳</span> Processing...',
            forceCheckboxSelector: config.forceCheckboxSelector || '#force',
            albumSelectSelector: config.albumSelectSelector || '#album',
            limitInputSelector: config.limitInputSelector || '#limit'
        };
        
        this.processingStartTime = null;
        this.estimatedItemCount = 0;
        this.processingWarningActive = false;
        this.progressInterval = null;
        
        this.init();
    }
    
    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.form = document.querySelector(this.config.formSelector);
            if (!this.form) {
                console.error(`AI Processing form not found: ${this.config.formSelector}`);
                return;
            }
            
            this.submitButton = this.form.querySelector(this.config.submitButtonSelector);
            this.modal = document.getElementById(this.config.modalId);
            this.statusText = document.getElementById('processingStatus');
            this.progressBar = document.getElementById('progressBar');
            this.detailsText = document.getElementById('processingDetails');
            
            this.checkForCompletedProcessing();
            this.restoreProcessingState();
            this.attachEventHandlers();
        });
    }
    
    checkForCompletedProcessing() {
        const successMessages = document.querySelectorAll('.alert-success, .messages .success');
        if (successMessages.length > 0) {
            for (let msg of successMessages) {
                if (msg.textContent.includes('Successfully processed')) {
                    this.clearProcessingState();
                    this.processingWarningActive = false;
                    break;
                }
            }
        }
    }
    
    restoreProcessingState() {
        if (sessionStorage.getItem(`${this.config.storagePrefix}InProgress`) === 'true') {
            const savedStartTime = sessionStorage.getItem(`${this.config.storagePrefix}StartTime`);
            const savedItemCount = sessionStorage.getItem(`${this.config.storagePrefix}ItemCount`);
            
            if (savedStartTime && savedItemCount) {
                this.processingStartTime = parseInt(savedStartTime);
                this.estimatedItemCount = parseInt(savedItemCount);
                this.showProcessingModal();
                this.startProgressSimulation();
                this.processingWarningActive = true;
                
                if (this.submitButton) {
                    this.submitButton.disabled = true;
                    this.submitButton.innerHTML = this.config.submitButtonProcessingHTML;
                }
            }
        }
    }
    
    attachEventHandlers() {
        this.form.addEventListener('submit', (e) => {
            this.calculateEstimatedItems();
            
            if (this.estimatedItemCount === 0) {
                return; // Let form submit normally
            }
            
            this.saveProcessingState();
            this.showProcessingModal();
            this.startProgressSimulation();
            
            setTimeout(() => {
                this.processingWarningActive = true;
            }, 3000);
            
            if (this.submitButton) {
                this.submitButton.disabled = true;
                this.submitButton.innerHTML = this.config.submitButtonProcessingHTML;
            }
        });
        
        window.addEventListener('beforeunload', (e) => {
            if (this.processingWarningActive && !this.modal.classList.contains('hidden')) {
                e.preventDefault();
                e.returnValue = 'AI processing is in progress. Leaving this page may interrupt the process.';
                return e.returnValue;
            }
        });
    }
    
    calculateEstimatedItems() {
        const forceReprocess = document.querySelector(this.config.forceCheckboxSelector)?.checked || false;
        const albumSelect = document.querySelector(this.config.albumSelectSelector);
        const limitInput = document.querySelector(this.config.limitInputSelector);
        
        // Start with total or unprocessed items
        if (forceReprocess) {
            this.estimatedItemCount = this.config.getTotalItems();
        } else {
            this.estimatedItemCount = this.config.getUnprocessedItems();
        }
        
        // Apply album filter if selected
        if (albumSelect && albumSelect.value) {
            const selectedOption = albumSelect.options[albumSelect.selectedIndex];
            const albumItemCount = this.extractItemCountFromOption(selectedOption.text);
            
            if (!forceReprocess) {
                // Estimate unprocessed items in selected album
                const totalItems = this.config.getTotalItems();
                const unprocessedItems = this.config.getUnprocessedItems();
                this.estimatedItemCount = Math.max(1, Math.round(albumItemCount * (unprocessedItems / totalItems)));
            } else {
                this.estimatedItemCount = albumItemCount;
            }
        }
        
        // Apply limit if specified
        const limit = parseInt(limitInput?.value);
        if (limit && limit > 0) {
            this.estimatedItemCount = Math.min(this.estimatedItemCount, limit);
        }
    }
    
    extractItemCountFromOption(text) {
        const match = text.match(/\((\d+) (?:photo|video)s?\)/i);
        return match ? parseInt(match[1]) : 0;
    }
    
    saveProcessingState() {
        this.processingStartTime = Date.now();
        sessionStorage.setItem(`${this.config.storagePrefix}InProgress`, 'true');
        sessionStorage.setItem(`${this.config.storagePrefix}StartTime`, this.processingStartTime.toString());
        sessionStorage.setItem(`${this.config.storagePrefix}ItemCount`, this.estimatedItemCount.toString());
    }
    
    clearProcessingState() {
        sessionStorage.removeItem(`${this.config.storagePrefix}InProgress`);
        sessionStorage.removeItem(`${this.config.storagePrefix}StartTime`);
        sessionStorage.removeItem(`${this.config.storagePrefix}ItemCount`);
    }
    
    showProcessingModal() {
        if (!this.modal) return;
        
        this.modal.classList.remove('hidden');
        
        const itemWord = this.estimatedItemCount === 1 ? this.config.itemType : this.config.itemTypePlural;
        this.statusText.textContent = `Analyzing ${this.estimatedItemCount} ${itemWord} with AI...`;
        this.progressBar.style.width = '5%';
        
        if (this.estimatedItemCount > 0) {
            const estimatedTime = Math.round(this.estimatedItemCount * this.config.processingTimePerItem);
            this.detailsText.textContent = `Estimated time: ${this.formatTime(estimatedTime)}. Please keep this page open.`;
        }
    }
    
    startProgressSimulation() {
        const estimatedTotalTime = this.estimatedItemCount * this.config.processingTimePerItem * 1000; // Convert to ms
        const updateInterval = Math.max(100, estimatedTotalTime / 100);
        
        let currentProgress = 5;
        
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        this.progressInterval = setInterval(() => {
            const elapsed = Date.now() - this.processingStartTime;
            const estimatedProgress = Math.min(90, (elapsed / estimatedTotalTime) * 100);
            
            if (estimatedProgress > currentProgress) {
                currentProgress = Math.min(currentProgress + 2, estimatedProgress);
            }
            
            this.progressBar.style.width = currentProgress + '%';
            
            const elapsedSeconds = Math.floor(elapsed / 1000);
            this.statusText.textContent = `Processing... (${elapsedSeconds}s elapsed)`;
            
            if (currentProgress >= 90) {
                clearInterval(this.progressInterval);
                this.statusText.textContent = 'Finalizing analysis...';
                this.progressBar.style.width = '95%';
            }
        }, updateInterval);
    }
    
    formatTime(seconds) {
        if (seconds < 60) {
            return `${seconds} seconds`;
        } else {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            if (remainingSeconds === 0) {
                return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
            } else {
                return `${minutes}m ${remainingSeconds}s`;
            }
        }
    }
}

// Export for use in templates
window.AIProcessingHandler = AIProcessingHandler;

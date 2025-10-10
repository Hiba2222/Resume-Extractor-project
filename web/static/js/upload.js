// Upload functionality module
class UploadManager {
    constructor() {
        this.dropZone = document.getElementById('dropZone');
        this.fileInput = document.getElementById('pdf_file');
        this.browseButton = document.getElementById('browseButton');
        this.fileInfo = document.getElementById('fileInfo');
        this.fileName = document.getElementById('fileName');
        this.submitBtn = document.getElementById('submitBtn');
        this.modelCards = document.querySelectorAll('.model-card');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupModelSelection();
    }
    
    setupEventListeners() {
        // Browse button click
        if (this.browseButton) {
            this.browseButton.addEventListener('click', () => {
                this.fileInput.click();
            });
        }
        
        // File selection
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => {
                this.handleFileSelection(e);
            });
        }
        
        // Drag and drop
        if (this.dropZone) {
            this.setupDragAndDrop();
        }
    }
    
    setupDragAndDrop() {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // Highlight drop zone when file is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => this.highlight(), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => this.unhighlight(), false);
        });
        
        // Handle dropped files
        this.dropZone.addEventListener('drop', (e) => this.handleDrop(e), false);
    }
    
    setupModelSelection() {
        if (this.modelCards.length > 0) {
            this.modelCards.forEach(card => {
                card.addEventListener('click', () => {
                    this.selectModel(card);
                });
            });
            
            // Set first model as selected by default
            this.modelCards[0].classList.add('selected');
        }
    }
    
    handleFileSelection(event) {
        const files = event.target.files;
        if (files.length > 0) {
            this.displayFileInfo(files[0]);
            this.enableSubmitButton();
        } else {
            this.hideFileInfo();
            this.disableSubmitButton();
        }
    }
    
    handleDrop(e) {
        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (file.type === 'application/pdf') {
                // Create a DataTransfer object to update the FileList
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                this.fileInput.files = dataTransfer.files;
                
                this.displayFileInfo(file);
                this.enableSubmitButton();
            } else {
                this.showAlert('Please upload a PDF file', 'danger');
            }
        }
    }
    
    selectModel(selectedCard) {
        // Remove selected class from all cards
        this.modelCards.forEach(card => card.classList.remove('selected'));
        
        // Add selected class to clicked card
        selectedCard.classList.add('selected');
        
        // Select the radio button
        const model = selectedCard.getAttribute('data-model');
        const radioButton = document.querySelector(`input[value="${model}"]`);
        if (radioButton) {
            radioButton.checked = true;
        }
    }
    
    displayFileInfo(file) {
        if (this.fileInfo && this.fileName) {
            this.fileInfo.classList.remove('d-none');
            this.fileName.textContent = file.name;
            
            // Add animation
            this.fileInfo.classList.add('slide-in-up');
        }
    }
    
    hideFileInfo() {
        if (this.fileInfo) {
            this.fileInfo.classList.add('d-none');
            this.fileInfo.classList.remove('slide-in-up');
        }
    }
    
    enableSubmitButton() {
        if (this.submitBtn) {
            this.submitBtn.classList.remove('disabled');
            this.submitBtn.disabled = false;
        }
    }
    
    disableSubmitButton() {
        if (this.submitBtn) {
            this.submitBtn.classList.add('disabled');
            this.submitBtn.disabled = true;
        }
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    highlight() {
        this.dropZone.classList.add('highlight');
    }
    
    unhighlight() {
        this.dropZone.classList.remove('highlight');
    }
    
    showAlert(message, type = 'warning') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show flash-message shadow-sm`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'danger' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'} me-2 alert-icon"></i>
            <strong class="alert-title">${type === 'danger' ? 'Error!' : type === 'success' ? 'Success!' : 'Info:'}</strong> 
            <span class="alert-message">${message}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
        
        // Add animation
        alertDiv.classList.add('slide-in-down');
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 500);
        }, 5000);
    }
}

// Export for use in other modules
window.UploadManager = UploadManager;

// Common functionality module
class CommonUtils {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupSmoothScrolling();
        this.setupCardAnimations();
        this.setupButtonAnimations();
        this.setupFormSubmissionHandling();
    }
    
    // Smooth scrolling for anchor links
    setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
    
    // Card hover animations
    setupCardAnimations() {
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }
    
    // Button hover animations
    setupButtonAnimations() {
        const importantBtns = document.querySelectorAll('.btn-primary, .btn-success');
        importantBtns.forEach(btn => {
            btn.addEventListener('mouseenter', function() {
                this.style.animation = 'pulse 1s infinite';
            });
            
            btn.addEventListener('mouseleave', function() {
                this.style.animation = 'none';
            });
        });
    }
    
    // Form submission handling
    setupFormSubmissionHandling() {
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => {
                this.handleFormSubmission(e);
            });
        }
    }
    
    handleFormSubmission(event) {
        const btn = document.getElementById('submitBtn');
        const btnText = document.getElementById('btnText');
        const btnLoading = document.getElementById('btnLoading');
        
        if (btn && btnText && btnLoading) {
            btn.disabled = true;
            btnText.classList.add('d-none');
            btnLoading.classList.remove('d-none');
            
            // Add loading animation to the button
            btn.classList.add('loading');
        }
    }
    
    // Utility method to show notifications
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show flash-message shadow-sm`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 500px;
        `;
        
        notification.innerHTML = `
            <i class="fas fa-${type === 'danger' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'} me-2 alert-icon"></i>
            <strong class="alert-title">${type === 'danger' ? 'Error!' : type === 'success' ? 'Success!' : 'Info:'}</strong> 
            <span class="alert-message">${message}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Add slide-in animation
        notification.classList.add('slide-in-down');
        
        // Auto dismiss
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 500);
        }, duration);
        
        return notification;
    }
    
    // Utility method to validate forms
    validateForm(formElement) {
        const requiredFields = formElement.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.highlightError(field);
                isValid = false;
            } else {
                this.clearError(field);
            }
        });
        
        return isValid;
    }
    
    highlightError(field) {
        field.classList.add('is-invalid');
        field.classList.add('shake');
        
        // Remove shake animation after it completes
        setTimeout(() => {
            field.classList.remove('shake');
        }, 820);
    }
    
    clearError(field) {
        field.classList.remove('is-invalid');
    }
    
    // Utility method to format file sizes
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Utility method to debounce function calls
    debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }
    
    // Utility method to throttle function calls
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Export for use in other modules
window.CommonUtils = CommonUtils;

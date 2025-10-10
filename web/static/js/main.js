// Main JavaScript file - initializes all modules
document.addEventListener('DOMContentLoaded', function() {
    // Initialize common utilities
    const commonUtils = new CommonUtils();
    
    // Initialize upload manager if on upload page
    if (document.getElementById('uploadForm')) {
        const uploadManager = new UploadManager();
        
        // Store reference globally for potential external access
        window.uploadManager = uploadManager;
    }
    
    // Initialize results manager if on results page
    if (document.querySelectorAll('input[name="model-selector"]').length > 0) {
        const resultsManager = new ResultsManager();
        
        // Store reference globally for potential external access
        window.resultsManager = resultsManager;
    }
    
    // Setup global error handling
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        
        // Show user-friendly error message
        if (window.commonUtils) {
            commonUtils.showNotification(
                'An unexpected error occurred. Please try again.',
                'danger'
            );
        }
    });
    
    // Setup global unhandled promise rejection handling
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        
        // Show user-friendly error message
        if (window.commonUtils) {
            commonUtils.showNotification(
                'A network or processing error occurred. Please try again.',
                'danger'
            );
        }
    });
    
    // Store common utils globally
    window.commonUtils = commonUtils;
    
    // Initialize page-specific functionality
    initializePageSpecific();
    
    // Setup performance monitoring
    setupPerformanceMonitoring();
});

function initializePageSpecific() {
    const currentPath = window.location.pathname;
    
    // Home page specific initialization
    if (currentPath === '/' || currentPath.includes('home')) {
        initializeHomePage();
    }
    
    // Upload page specific initialization
    if (currentPath.includes('upload')) {
        initializeUploadPage();
    }
    
    // Results page specific initialization
    if (currentPath.includes('results')) {
        initializeResultsPage();
    }
    
    // About page specific initialization
    if (currentPath.includes('about')) {
        initializeAboutPage();
    }
}

function initializeHomePage() {
    // Add any home page specific functionality
    console.log('Home page initialized');
    
    // Setup hero animation
    const heroElements = document.querySelectorAll('.hero-section .floating-element');
    heroElements.forEach(element => {
        element.classList.add('floating');
    });
}

function initializeUploadPage() {
    console.log('Upload page initialized');
    
    // Add upload page specific enhancements
    const dropZone = document.getElementById('dropZone');
    if (dropZone) {
        // Add visual feedback for drag operations
        dropZone.addEventListener('dragenter', function() {
            this.style.borderColor = 'var(--accent-color)';
            this.style.backgroundColor = 'rgba(49, 130, 206, 0.1)';
        });
        
        dropZone.addEventListener('dragleave', function() {
            this.style.borderColor = '#ccc';
            this.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
        });
    }
}

function initializeResultsPage() {
    console.log('Results page initialized');
    
    // Add export functionality to results
    const exportButtons = document.querySelectorAll('.export-btn');
    exportButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const modelName = this.dataset.model;
            if (window.resultsManager) {
                window.resultsManager.exportResults(modelName);
            }
        });
    });
}

function initializeAboutPage() {
    console.log('About page initialized');
    
    // Add any about page specific functionality
    const techBadges = document.querySelectorAll('.tech-badge');
    techBadges.forEach((badge, index) => {
        badge.style.animationDelay = `${index * 0.1}s`;
        badge.classList.add('fade-in');
    });
}

function setupPerformanceMonitoring() {
    // Monitor page load performance
    window.addEventListener('load', function() {
        if ('performance' in window) {
            const perfData = performance.getEntriesByType('navigation')[0];
            const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
            
            console.log(`Page load time: ${loadTime}ms`);
            
            // Log slow page loads
            if (loadTime > 3000) {
                console.warn('Slow page load detected:', loadTime + 'ms');
            }
        }
    });
    
    // Monitor resource loading
    if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
            list.getEntries().forEach((entry) => {
                if (entry.duration > 1000) {
                    console.warn('Slow resource load:', entry.name, entry.duration + 'ms');
                }
            });
        });
        
        observer.observe({ entryTypes: ['resource'] });
    }
}

// Utility function to check if user prefers reduced motion
function prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// Disable animations if user prefers reduced motion
if (prefersReducedMotion()) {
    document.documentElement.style.setProperty('--transition', 'none');
    
    // Disable specific animations
    const animatedElements = document.querySelectorAll('.floating, .bounce, .pulse');
    animatedElements.forEach(element => {
        element.style.animation = 'none';
    });
}

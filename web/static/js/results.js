// Results page functionality module
class ResultsManager {
    constructor() {
        this.modelSelectors = document.querySelectorAll('input[name="model-selector"]');
        this.init();
    }
    
    init() {
        this.setupModelSelectors();
        this.setupAnimations();
    }
    
    setupModelSelectors() {
        if (this.modelSelectors.length > 0) {
            this.modelSelectors.forEach(selector => {
                selector.addEventListener('change', (e) => {
                    this.switchModelResults(e.target);
                });
            });
        }
    }
    
    switchModelResults(selector) {
        // Hide all result divs with fade out
        const resultDivs = document.querySelectorAll('.model-result');
        resultDivs.forEach(div => {
            div.style.opacity = '0';
            div.style.transform = 'translateY(20px)';
            setTimeout(() => {
                div.style.display = 'none';
            }, 300);
        });
        
        // Show the selected model's results with fade in
        const modelName = selector.id.replace('-btn', '');
        const targetDiv = document.getElementById(modelName + '-results');
        
        if (targetDiv) {
            setTimeout(() => {
                targetDiv.style.display = 'block';
                targetDiv.style.opacity = '0';
                targetDiv.style.transform = 'translateY(20px)';
                
                // Trigger reflow
                targetDiv.offsetHeight;
                
                targetDiv.style.transition = 'all 0.3s ease';
                targetDiv.style.opacity = '1';
                targetDiv.style.transform = 'translateY(0)';
            }, 300);
        }
    }
    
    setupAnimations() {
        // Add stagger animation to result items
        const resultItems = document.querySelectorAll('.edu-item, .exp-item, .cert-item');
        resultItems.forEach((item, index) => {
            item.classList.add('stagger-item');
            item.style.animationDelay = `${index * 0.1}s`;
        });
        
        // Setup scroll animations
        this.setupScrollAnimations();
    }
    
    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);
        
        // Observe all animatable elements
        const animatableElements = document.querySelectorAll('.card, .feature-card');
        animatableElements.forEach(el => {
            el.classList.add('animate-on-scroll');
            observer.observe(el);
        });
    }
    
    // Method to export results as JSON
    exportResults(modelName) {
        const resultsDiv = document.getElementById(modelName + '-results');
        if (!resultsDiv) return;
        
        const results = this.extractResultsData(resultsDiv);
        const dataStr = JSON.stringify(results, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `cv_extraction_${modelName}_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    }
    
    extractResultsData(resultsDiv) {
        const data = {
            timestamp: new Date().toISOString(),
            personal_info: {},
            education: [],
            experience: [],
            skills: [],
            certifications: []
        };
        
        // Extract personal info
        const personalInfo = resultsDiv.querySelector('.personal-info');
        if (personalInfo) {
            const infoItems = personalInfo.querySelectorAll('.info-item');
            infoItems.forEach(item => {
                const label = item.querySelector('strong')?.textContent?.replace(':', '').trim();
                const value = item.textContent.replace(item.querySelector('strong')?.textContent || '', '').trim();
                if (label && value) {
                    data.personal_info[label.toLowerCase().replace(/\s+/g, '_')] = value;
                }
            });
        }
        
        // Extract education
        const eduItems = resultsDiv.querySelectorAll('.edu-item');
        eduItems.forEach(item => {
            const title = item.querySelector('h5')?.textContent?.trim();
            const details = item.querySelector('p')?.textContent?.trim();
            if (title) {
                data.education.push({
                    title: title,
                    details: details || ''
                });
            }
        });
        
        // Extract experience
        const expItems = resultsDiv.querySelectorAll('.exp-item');
        expItems.forEach(item => {
            const title = item.querySelector('h5')?.textContent?.trim();
            const details = item.querySelector('p')?.textContent?.trim();
            const responsibilities = [];
            const respList = item.querySelector('.responsibilities ul');
            if (respList) {
                const listItems = respList.querySelectorAll('li');
                listItems.forEach(li => responsibilities.push(li.textContent.trim()));
            }
            
            if (title) {
                data.experience.push({
                    title: title,
                    details: details || '',
                    responsibilities: responsibilities
                });
            }
        });
        
        // Extract skills
        const skillsList = resultsDiv.querySelector('.skill-list');
        if (skillsList) {
            const skillItems = skillsList.querySelectorAll('li');
            skillItems.forEach(item => {
                data.skills.push(item.textContent.trim());
            });
        }
        
        return data;
    }
}

// Export for use in other modules
window.ResultsManager = ResultsManager;

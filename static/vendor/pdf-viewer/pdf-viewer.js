class PDFViewer {
    constructor(options = {}) {
        this.container = options.container || '#pdf-viewer-container';
        this.viewer = options.viewer || '#pdf-viewer';
        this.pdfUrl = options.pdfUrl;
        this.currentPage = 1;
        this.totalPages = options.totalPages || 1;
        this.zoom = 100;
        this.isLoading = false;
        this.cache = new Map();
        
        // Initialize viewer
        this.init();
    }
    
    async init() {
        // Initialize PDF.js if not already loaded
        if (typeof pdfjsLib === 'undefined') {
            await this.loadPDFJS();
        }
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load initial page
        this.loadPage(this.currentPage);
        
        // Initialize gestures for touch devices
        this.initGestures();
    }
    
    async loadPDFJS() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.12.313/pdf.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    setupEventListeners() {
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowRight':
                    this.nextPage();
                    break;
                case 'ArrowLeft':
                    this.previousPage();
                    break;
                case '+':
                    this.zoomIn();
                    break;
                case '-':
                    this.zoomOut();
                    break;
            }
        });
        
        // Mouse wheel zoom with Ctrl key
        document.addEventListener('wheel', (e) => {
            if (e.ctrlKey) {
                e.preventDefault();
                if (e.deltaY < 0) {
                    this.zoomIn();
                } else {
                    this.zoomOut();
                }
            }
        }, { passive: false });
    }
    
    initGestures() {
        let touchStartX = 0;
        let touchStartY = 0;
        let initialPinchDistance = 0;
        
        const container = document.querySelector(this.container);
        
        container.addEventListener('touchstart', (e) => {
            if (e.touches.length === 2) {
                // Pinch gesture start
                initialPinchDistance = Math.hypot(
                    e.touches[0].pageX - e.touches[1].pageX,
                    e.touches[0].pageY - e.touches[1].pageY
                );
            } else if (e.touches.length === 1) {
                // Single touch for swipe
                touchStartX = e.touches[0].pageX;
                touchStartY = e.touches[0].pageY;
            }
        });
        
        container.addEventListener('touchmove', (e) => {
            if (e.touches.length === 2) {
                // Pinch gesture for zoom
                e.preventDefault();
                const currentDistance = Math.hypot(
                    e.touches[0].pageX - e.touches[1].pageX,
                    e.touches[0].pageY - e.touches[1].pageY
                );
                
                if (currentDistance > initialPinchDistance) {
                    this.zoomIn();
                } else {
                    this.zoomOut();
                }
                
                initialPinchDistance = currentDistance;
            }
        }, { passive: false });
        
        container.addEventListener('touchend', (e) => {
            if (e.touches.length === 0) {
                // Handle swipe
                const touchEndX = e.changedTouches[0].pageX;
                const touchEndY = e.changedTouches[0].pageY;
                
                const deltaX = touchEndX - touchStartX;
                const deltaY = touchEndY - touchStartY;
                
                // Ensure it's a horizontal swipe
                if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                    if (deltaX > 0) {
                        this.previousPage();
                    } else {
                        this.nextPage();
                    }
                }
            }
        });
    }
    
    async loadPage(pageNumber) {
        if (this.isLoading || pageNumber < 1 || pageNumber > this.totalPages) {
            return;
        }
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            // Check cache first
            if (this.cache.has(pageNumber)) {
                this.displayPage(this.cache.get(pageNumber));
                return;
            }
            
            // Fetch page data
            const response = await fetch(`/api/magazines/pages/${pageNumber}/`);
            if (!response.ok) throw new Error('Failed to load page');
            
            const data = await response.json();
            
            // Cache the result
            this.cache.set(pageNumber, data);
            
            // Display the page
            this.displayPage(data);
            
            // Update current page
            this.currentPage = pageNumber;
            
            // Update URL if needed
            this.updateURL();
            
            // Preload adjacent pages
            this.preloadAdjacentPages();
        } catch (error) {
            console.error('Error loading page:', error);
            this.showError('Failed to load page. Please try again.');
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    displayPage(pageData) {
        const viewer = document.querySelector(this.viewer);
        viewer.src = pageData.imageUrl;
        
        // Update page number display
        this.updatePageDisplay();
        
        // Dispatch custom event
        viewer.dispatchEvent(new CustomEvent('pagechange', {
            detail: {
                pageNumber: this.currentPage,
                totalPages: this.totalPages
            }
        }));
    }
    
    updatePageDisplay() {
        const display = document.querySelector('.pdf-page-number');
        if (display) {
            display.value = this.currentPage;
        }
    }
    
    updateURL() {
        const url = new URL(window.location);
        url.searchParams.set('page', this.currentPage);
        window.history.replaceState({}, '', url);
    }
    
    async preloadAdjacentPages() {
        const pagesToPreload = [
            this.currentPage - 1,
            this.currentPage + 1
        ].filter(page => page > 0 && page <= this.totalPages);
        
        for (const page of pagesToPreload) {
            if (!this.cache.has(page)) {
                try {
                    const response = await fetch(`/api/magazines/pages/${page}/`);
                    const data = await response.json();
                    this.cache.set(page, data);
                } catch (error) {
                    console.error(`Error preloading page ${page}:`, error);
                }
            }
        }
    }
    
    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.loadPage(this.currentPage + 1);
        }
    }
    
    previousPage() {
        if (this.currentPage > 1) {
            this.loadPage(this.currentPage - 1);
        }
    }
    
    zoomIn() {
        if (this.zoom < 200) {
            this.zoom += 25;
            this.applyZoom();
        }
    }
    
    zoomOut() {
        if (this.zoom > 50) {
            this.zoom -= 25;
            this.applyZoom();
        }
    }
    
    applyZoom() {
        const viewer = document.querySelector(this.viewer);
        viewer.style.transform = `scale(${this.zoom / 100})`;
        
        // Dispatch custom event
        viewer.dispatchEvent(new CustomEvent('zoomchange', {
            detail: { zoom: this.zoom }
        }));
    }
    
    showLoading() {
        const container = document.querySelector(this.container);
        const loading = document.createElement('div');
        loading.className = 'pdf-loading';
        loading.innerHTML = '<div class="pdf-loading-spinner"></div>';
        container.appendChild(loading);
    }
    
    hideLoading() {
        const loading = document.querySelector('.pdf-loading');
        if (loading) {
            loading.remove();
        }
    }
    
    showError(message) {
        // Implement error display logic
        console.error(message);
    }
    
    destroy() {
        // Clean up event listeners and cache
        this.cache.clear();
        // Additional cleanup as needed
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PDFViewer;
}

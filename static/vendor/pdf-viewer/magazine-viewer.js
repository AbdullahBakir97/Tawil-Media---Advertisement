class MagazineViewer {
    constructor(options = {}) {
        this.container = options.container || '#magazine-container';
        this.pages = options.pages || [];
        this.currentSpread = 0;
        this.totalPages = this.pages.length;
        this.isAnimating = false;
        this.zoom = 100;
        this.mode = 'double'; // 'single' or 'double' spread
        this.isFirstLoad = true;
        
        // Initialize the viewer
        this.init();
    }
    
    async init() {
        this.createStructure();
        this.setupEventListeners();
        await this.loadInitialSpread();
        this.initializeGestures();
        
        // Remove loading state after initial load
        setTimeout(() => {
            document.querySelector(this.container).classList.remove('loading');
            this.isFirstLoad = false;
        }, 1000);
    }
    
    createStructure() {
        const container = document.querySelector(this.container);
        container.classList.add('magazine-viewer', 'loading');
        
        // Create book structure
        container.innerHTML = `
            <div class="magazine-wrapper">
                <div class="magazine">
                    <div class="page-left"></div>
                    <div class="page-right"></div>
                    <div class="page-turning"></div>
                </div>
                
                <!-- Navigation Controls -->
                <button class="nav-prev" aria-label="Previous page">
                    <svg viewBox="0 0 24 24" width="24" height="24">
                        <path d="M15 18l-6-6 6-6" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
                <button class="nav-next" aria-label="Next page">
                    <svg viewBox="0 0 24 24" width="24" height="24">
                        <path d="M9 18l6-6-6-6" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
            
            <!-- Page Navigation -->
            <div class="page-navigation">
                <div class="current-pages"></div>
                <div class="page-slider">
                    <input type="range" min="0" max="${Math.ceil(this.totalPages / 2) - 1}" value="0">
                </div>
            </div>
            
            <!-- Thumbnails -->
            <div class="thumbnails-wrapper">
                <div class="thumbnails-scroll">
                    ${this.pages.map((page, index) => `
                        <div class="thumbnail" data-page="${index}">
                            <img src="${page.thumbnail}" alt="Page ${index + 1}">
                            <span class="page-number">${index + 1}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    setupEventListeners() {
        const container = document.querySelector(this.container);
        
        // Navigation buttons
        container.querySelector('.nav-prev').addEventListener('click', () => this.previousSpread());
        container.querySelector('.nav-next').addEventListener('click', () => this.nextSpread());
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') this.previousSpread();
            if (e.key === 'ArrowRight') this.nextSpread();
        });
        
        // Page slider
        const slider = container.querySelector('.page-slider input');
        slider.addEventListener('input', (e) => {
            this.goToSpread(parseInt(e.target.value));
        });
        
        // Thumbnails
        container.querySelectorAll('.thumbnail').forEach(thumb => {
            thumb.addEventListener('click', () => {
                const page = parseInt(thumb.dataset.page);
                this.goToSpread(Math.floor(page / 2));
            });
        });
        
        // Window resize
        window.addEventListener('resize', this.debounce(() => {
            this.updateLayout();
        }, 250));
    }
    
    initializeGestures() {
        const hammer = new Hammer(document.querySelector(this.container));
        
        // Swipe navigation
        hammer.on('swipeleft', () => this.nextSpread());
        hammer.on('swiperight', () => this.previousSpread());
        
        // Pinch zoom
        hammer.get('pinch').set({ enable: true });
        hammer.on('pinchin', () => this.zoomOut());
        hammer.on('pinchout', () => this.zoomIn());
        
        // Double tap to zoom
        hammer.on('doubletap', (e) => {
            if (this.zoom === 100) {
                this.zoomToPoint(200, e.center);
            } else {
                this.resetZoom();
            }
        });
    }
    
    async loadInitialSpread() {
        const leftPage = this.pages[this.currentSpread * 2];
        const rightPage = this.pages[this.currentSpread * 2 + 1];
        
        await Promise.all([
            this.loadPage('left', leftPage),
            this.loadPage('right', rightPage)
        ]);
        
        this.updatePageNavigation();
    }
    
    async loadPage(side, pageData) {
        if (!pageData) return;
        
        const pageElement = document.querySelector(`${this.container} .page-${side}`);
        
        // Create and load high-resolution image
        const img = new Image();
        img.src = pageData.url;
        
        await new Promise((resolve, reject) => {
            img.onload = resolve;
            img.onerror = reject;
        });
        
        pageElement.style.backgroundImage = `url(${pageData.url})`;
        pageElement.setAttribute('data-page', pageData.number);
    }
    
    async turnPage(direction) {
        if (this.isAnimating) return;
        this.isAnimating = true;
        
        const magazine = document.querySelector(`${this.container} .magazine`);
        const turningPage = document.querySelector(`${this.container} .page-turning`);
        
        // Set up the turning page
        if (direction === 'forward') {
            turningPage.style.backgroundImage = `url(${this.pages[this.currentSpread * 2 + 2].url})`;
            magazine.classList.add('turning-forward');
        } else {
            turningPage.style.backgroundImage = `url(${this.pages[this.currentSpread * 2 - 1].url})`;
            magazine.classList.add('turning-backward');
        }
        
        // Wait for animation
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Update spread
        this.currentSpread += direction === 'forward' ? 1 : -1;
        await this.loadInitialSpread();
        
        // Clean up
        magazine.classList.remove('turning-forward', 'turning-backward');
        this.isAnimating = false;
    }
    
    async nextSpread() {
        if (this.currentSpread < Math.ceil(this.totalPages / 2) - 1) {
            await this.turnPage('forward');
            this.updatePageNavigation();
        }
    }
    
    async previousSpread() {
        if (this.currentSpread > 0) {
            await this.turnPage('backward');
            this.updatePageNavigation();
        }
    }
    
    async goToSpread(spread) {
        if (spread === this.currentSpread) return;
        
        const direction = spread > this.currentSpread ? 'forward' : 'backward';
        this.currentSpread = spread;
        
        await this.loadInitialSpread();
        this.updatePageNavigation();
    }
    
    updatePageNavigation() {
        const container = document.querySelector(this.container);
        const currentPages = container.querySelector('.current-pages');
        const slider = container.querySelector('.page-slider input');
        
        const leftPage = this.currentSpread * 2 + 1;
        const rightPage = this.currentSpread * 2 + 2;
        
        currentPages.textContent = `${leftPage}-${Math.min(rightPage, this.totalPages)} of ${this.totalPages}`;
        slider.value = this.currentSpread;
        
        // Update thumbnails
        container.querySelectorAll('.thumbnail').forEach(thumb => {
            const page = parseInt(thumb.dataset.page);
            thumb.classList.toggle('active', 
                page === this.currentSpread * 2 || page === this.currentSpread * 2 + 1);
        });
    }
    
    updateLayout() {
        const container = document.querySelector(this.container);
        const magazine = container.querySelector('.magazine');
        
        // Calculate optimal size based on container
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;
        const aspectRatio = 1.4; // Standard magazine aspect ratio
        
        let width, height;
        
        if (containerWidth / containerHeight > aspectRatio * 2) {
            // Container is too wide
            height = containerHeight * 0.9;
            width = height * aspectRatio;
        } else {
            // Container is too tall
            width = containerWidth * 0.45;
            height = width / aspectRatio;
        }
        
        magazine.style.width = `${width * 2}px`;
        magazine.style.height = `${height}px`;
    }
    
    zoomToPoint(scale, point) {
        const magazine = document.querySelector(`${this.container} .magazine`);
        const rect = magazine.getBoundingClientRect();
        
        const x = (point.x - rect.left) / rect.width;
        const y = (point.y - rect.top) / rect.height;
        
        magazine.style.transformOrigin = `${x * 100}% ${y * 100}%`;
        magazine.style.transform = `scale(${scale / 100})`;
        
        this.zoom = scale;
    }
    
    resetZoom() {
        const magazine = document.querySelector(`${this.container} .magazine`);
        magazine.style.transform = '';
        magazine.style.transformOrigin = 'center center';
        this.zoom = 100;
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MagazineViewer;
}

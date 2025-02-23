import Utils from '../core/utils.js';

class LazyLoad {
    constructor(options = {}) {
        this.options = {
            selector: '[data-lazy]',
            rootMargin: '50px 0px',
            threshold: 0.01,
            loadingClass: 'lazy-loading',
            loadedClass: 'lazy-loaded',
            errorClass: 'lazy-error',
            retryLimit: 2,
            retryDelay: 2000,
            ...options
        };

        this.loadedImages = new WeakSet();
        this.retryCount = new WeakMap();
        this.init();
    }

    init() {
        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver(
                this.handleIntersection.bind(this),
                {
                    root: null,
                    rootMargin: this.options.rootMargin,
                    threshold: this.options.threshold
                }
            );

            this.observeElements();
        } else {
            this.loadAllImages();
        }

        // Observe DOM changes for dynamically added elements
        this.setupMutationObserver();
    }

    observeElements() {
        const elements = document.querySelectorAll(this.options.selector);
        elements.forEach(element => {
            if (!this.loadedImages.has(element)) {
                this.observer.observe(element);
            }
        });
    }

    setupMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) { // Element node
                        if (node.matches?.(this.options.selector)) {
                            this.observer.observe(node);
                        }
                        const children = node.querySelectorAll?.(this.options.selector);
                        if (children) {
                            children.forEach(child => this.observer.observe(child));
                        }
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    handleIntersection(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                this.loadElement(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }

    async loadElement(element) {
        if (this.loadedImages.has(element)) return;

        const type = this.getElementType(element);
        if (!type) return;

        element.classList.add(this.options.loadingClass);

        try {
            await this.loadResource(element, type);
            this.handleSuccess(element);
        } catch (error) {
            await this.handleError(element, error);
        }
    }

    getElementType(element) {
        if (element.tagName === 'IMG') return 'image';
        if (element.tagName === 'VIDEO') return 'video';
        if (element.tagName === 'IFRAME') return 'iframe';
        if (element.dataset.background) return 'background';
        return null;
    }

    async loadResource(element, type) {
        return new Promise((resolve, reject) => {
            const src = type === 'background' ? 
                element.dataset.background : 
                element.dataset.src;

            if (!src) {
                reject(new Error('Source not specified'));
                return;
            }

            switch (type) {
                case 'image':
                    this.loadImage(element, src, resolve, reject);
                    break;
                case 'video':
                    this.loadVideo(element, src, resolve, reject);
                    break;
                case 'iframe':
                    this.loadIframe(element, src, resolve, reject);
                    break;
                case 'background':
                    this.loadBackground(element, src, resolve, reject);
                    break;
            }
        });
    }

    loadImage(element, src, resolve, reject) {
        const img = new Image();
        
        img.onload = () => {
            element.src = src;
            if (element.srcset) {
                element.srcset = element.dataset.srcset;
            }
            if (element.sizes) {
                element.sizes = element.dataset.sizes;
            }
            resolve();
        };

        img.onerror = () => reject(new Error('Failed to load image'));
        img.src = src;
    }

    loadVideo(element, src, resolve, reject) {
        element.src = src;

        // Load poster if specified
        if (element.dataset.poster) {
            element.poster = element.dataset.poster;
        }

        // Load sources if specified
        const sources = element.querySelectorAll('source[data-src]');
        sources.forEach(source => {
            source.src = source.dataset.src;
        });

        element.load();

        element.onloadeddata = () => resolve();
        element.onerror = () => reject(new Error('Failed to load video'));
    }

    loadIframe(element, src, resolve, reject) {
        element.onload = () => resolve();
        element.onerror = () => reject(new Error('Failed to load iframe'));
        element.src = src;
    }

    loadBackground(element, src, resolve, reject) {
        const img = new Image();
        
        img.onload = () => {
            element.style.backgroundImage = `url('${src}')`;
            resolve();
        };

        img.onerror = () => reject(new Error('Failed to load background image'));
        img.src = src;
    }

    handleSuccess(element) {
        element.classList.remove(this.options.loadingClass);
        element.classList.add(this.options.loadedClass);
        this.loadedImages.add(element);

        // Remove data attributes
        ['src', 'srcset', 'sizes', 'background'].forEach(attr => {
            if (element.dataset[attr]) {
                delete element.dataset[attr];
            }
        });

        // Dispatch success event
        element.dispatchEvent(new CustomEvent('lazyloaded', {
            bubbles: true,
            detail: { element }
        }));
    }

    async handleError(element, error) {
        const retryCount = this.retryCount.get(element) || 0;

        if (retryCount < this.options.retryLimit) {
            // Retry loading after delay
            await Utils.events.delay(this.options.retryDelay);
            this.retryCount.set(element, retryCount + 1);
            return this.loadElement(element);
        }

        // Max retries reached, show error state
        element.classList.remove(this.options.loadingClass);
        element.classList.add(this.options.errorClass);

        // Add error indicator
        const errorElement = Utils.dom.create('div', {
            class: 'lazy-error-indicator',
            role: 'alert'
        }, ['Failed to load resource']);

        element.parentNode.insertBefore(errorElement, element.nextSibling);

        // Dispatch error event
        element.dispatchEvent(new CustomEvent('lazyloaderror', {
            bubbles: true,
            detail: { element, error }
        }));

        console.error('LazyLoad error:', error);
    }

    loadAllImages() {
        const elements = document.querySelectorAll(this.options.selector);
        elements.forEach(element => this.loadElement(element));
    }

    refresh() {
        this.observeElements();
    }

    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
    }
}

export default LazyLoad;

// Example usage:
/*
import LazyLoad from './components/lazy-load.js';

document.addEventListener('DOMContentLoaded', () => {
    const lazyLoad = new LazyLoad({
        selector: '[data-lazy]',
        rootMargin: '50px 0px',
        threshold: 0.01,
        loadingClass: 'lazy-loading',
        loadedClass: 'lazy-loaded',
        errorClass: 'lazy-error',
        retryLimit: 2,
        retryDelay: 2000
    });

    // Listen for lazy load events
    document.addEventListener('lazyloaded', (e) => {
        console.log('Element loaded:', e.detail.element);
    });

    document.addEventListener('lazyloaderror', (e) => {
        console.error('Load error:', e.detail.error);
    });
});

// HTML Usage:
<img data-lazy data-src="image.jpg" data-srcset="image-1x.jpg 1x, image-2x.jpg 2x" alt="Lazy loaded image">
<video data-lazy data-src="video.mp4" data-poster="poster.jpg">
    <source data-src="video.webm" type="video/webm">
    <source data-src="video.mp4" type="video/mp4">
</video>
<div data-lazy data-background="background.jpg"></div>
*/

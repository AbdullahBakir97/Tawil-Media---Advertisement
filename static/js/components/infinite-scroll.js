import Utils from '../core/utils.js';
import state from '../core/state.js';

class InfiniteScroll {
    constructor(options = {}) {
        this.options = {
            containerSelector: '[data-infinite-scroll]',
            itemSelector: '[data-scroll-item]',
            loadingSelector: '[data-scroll-loading]',
            endMessageSelector: '[data-scroll-end]',
            loadMoreSelector: '[data-load-more]',
            threshold: 100,
            pageSize: 10,
            maxPages: null,
            autoLoad: true,
            useIntersectionObserver: true,
            ...options
        };

        this.state = {
            loading: false,
            currentPage: 1,
            hasMore: true,
            error: null,
            items: []
        };

        this.init();
    }

    init() {
        // Initialize state
        state.set('infiniteScroll', this.state);

        // Cache DOM elements
        this.container = document.querySelector(this.options.containerSelector);
        this.loadingElement = document.querySelector(this.options.loadingSelector);
        this.endMessage = document.querySelector(this.options.endMessageSelector);
        this.loadMoreButton = document.querySelector(this.options.loadMoreSelector);

        if (!this.container) {
            console.error('Infinite scroll container not found');
            return;
        }

        // Set up observers and event listeners
        this.setupObservers();
        this.bindEvents();

        // Subscribe to state changes
        state.subscribe('infiniteScroll', this.handleStateChange.bind(this));

        // Initial load
        if (this.options.autoLoad) {
            this.loadItems();
        }
    }

    setupObservers() {
        if (this.options.useIntersectionObserver && 'IntersectionObserver' in window) {
            // Create sentinel element
            this.sentinel = document.createElement('div');
            this.sentinel.className = 'scroll-sentinel';
            this.container.appendChild(this.sentinel);

            // Set up intersection observer
            this.observer = new IntersectionObserver(
                this.handleIntersection.bind(this),
                {
                    root: null,
                    rootMargin: `${this.options.threshold}px`,
                    threshold: 0
                }
            );

            this.observer.observe(this.sentinel);
        } else {
            // Fallback to scroll event
            this.scrollHandler = Utils.events.throttle(
                this.handleScroll.bind(this),
                100
            );
            window.addEventListener('scroll', this.scrollHandler);
        }
    }

    bindEvents() {
        // Handle load more button clicks
        if (this.loadMoreButton) {
            this.loadMoreButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadItems();
            });
        }

        // Handle window resize
        window.addEventListener('resize', Utils.events.debounce(() => {
            this.updateSentinelPosition();
        }, 150));
    }

    handleIntersection(entries) {
        const entry = entries[0];
        if (entry.isIntersecting && !this.state.loading && this.state.hasMore) {
            this.loadItems();
        }
    }

    handleScroll() {
        if (this.state.loading || !this.state.hasMore) return;

        const containerBottom = this.container.getBoundingClientRect().bottom;
        const windowHeight = window.innerHeight;

        if (containerBottom - windowHeight <= this.options.threshold) {
            this.loadItems();
        }
    }

    async loadItems() {
        const { currentPage, loading, hasMore } = this.state;

        if (loading || !hasMore) return;

        // Check max pages
        if (this.options.maxPages && currentPage >= this.options.maxPages) {
            this.updateState({ hasMore: false });
            return;
        }

        this.updateState({ loading: true });

        try {
            const newItems = await this.fetchItems(currentPage);
            
            // Update state with new items
            this.updateState({
                items: [...this.state.items, ...newItems],
                currentPage: currentPage + 1,
                hasMore: newItems.length === this.options.pageSize,
                loading: false,
                error: null
            });

            // Render new items
            this.renderItems(newItems);

            // Update sentinel position
            this.updateSentinelPosition();

        } catch (error) {
            this.updateState({
                loading: false,
                error: 'Failed to load items'
            });
        }
    }

    async fetchItems(page) {
        // Replace with your API endpoint
        const response = await fetch(`/api/items?page=${page}&pageSize=${this.options.pageSize}`);
        if (!response.ok) throw new Error('Failed to fetch items');
        return response.json();
    }

    renderItems(items) {
        const fragment = document.createDocumentFragment();

        items.forEach(item => {
            const element = this.createItemElement(item);
            fragment.appendChild(element);
        });

        // Insert before sentinel if it exists
        if (this.sentinel) {
            this.container.insertBefore(fragment, this.sentinel);
        } else {
            this.container.appendChild(fragment);
        }
    }

    createItemElement(item) {
        // Replace with your item template
        return Utils.dom.create('article', {
            class: 'scroll-item',
            'data-scroll-item': ''
        }, [
            Utils.dom.create('h3', { class: 'item-title' }, [item.title]),
            Utils.dom.create('p', { class: 'item-excerpt' }, [item.excerpt]),
            Utils.dom.create('div', { class: 'item-metadata' }, [
                Utils.dom.create('span', { class: 'item-date' }, [
                    Utils.date.relative(item.date)
                ])
            ])
        ]);
    }

    updateSentinelPosition() {
        if (!this.sentinel) return;

        // Ensure sentinel is at the bottom of the container
        this.sentinel.style.bottom = '0';
    }

    updateState(newState) {
        state.set('infiniteScroll', {
            ...state.get('infiniteScroll'),
            ...newState
        });
    }

    handleStateChange(scrollState) {
        // Update loading state
        this.loadingElement?.classList.toggle('hidden', !scrollState.loading);

        // Update load more button
        if (this.loadMoreButton) {
            this.loadMoreButton.classList.toggle('hidden', 
                !scrollState.hasMore || scrollState.loading
            );
        }

        // Show end message
        if (this.endMessage) {
            this.endMessage.classList.toggle('hidden', 
                scrollState.hasMore || scrollState.loading
            );
        }

        // Handle errors
        if (scrollState.error) {
            this.showError(scrollState.error);
        }
    }

    showError(message) {
        const errorElement = Utils.dom.create('div', {
            class: 'scroll-error',
            role: 'alert'
        }, [message]);

        this.container.appendChild(errorElement);
        
        setTimeout(() => {
            errorElement.remove();
        }, 5000);
    }

    destroy() {
        // Clean up observers and event listeners
        if (this.observer) {
            this.observer.disconnect();
        }

        if (this.scrollHandler) {
            window.removeEventListener('scroll', this.scrollHandler);
        }

        if (this.sentinel) {
            this.sentinel.remove();
        }

        // Remove state subscription
        state.reset('infiniteScroll');
    }

    reset() {
        // Reset state
        this.updateState({
            loading: false,
            currentPage: 1,
            hasMore: true,
            error: null,
            items: []
        });

        // Clear container
        while (this.container.firstChild) {
            this.container.removeChild(this.container.firstChild);
        }

        // Re-append sentinel
        if (this.sentinel) {
            this.container.appendChild(this.sentinel);
        }

        // Initial load
        if (this.options.autoLoad) {
            this.loadItems();
        }
    }
}

export default InfiniteScroll;

// Example usage:
/*
import InfiniteScroll from './components/infinite-scroll.js';

document.addEventListener('DOMContentLoaded', () => {
    const infiniteScroll = new InfiniteScroll({
        containerSelector: '#infinite-scroll-container',
        itemSelector: '.scroll-item',
        loadingSelector: '#scroll-loading',
        endMessageSelector: '#scroll-end',
        loadMoreSelector: '#load-more',
        threshold: 100,
        pageSize: 10,
        maxPages: null,
        autoLoad: true,
        useIntersectionObserver: true
    });
});
*/

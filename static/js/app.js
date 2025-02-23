// Import core modules
import Utils from './core/utils.js';
import state from './core/state.js';

// Import components
import SearchComponent from './components/search.js';
import InfiniteScroll from './components/infinite-scroll.js';
import LazyLoad from './components/lazy-load.js';

// Import analytics
import Analytics from './analytics/tracking.js';
import PerformanceMonitor from './analytics/performance.js';

class App {
    constructor() {
        this.init();
    }

    init() {
        // Initialize state with default values
        state.init({
            theme: localStorage.getItem('theme') || 'light',
            user: {
                isAuthenticated: document.body.hasAttribute('data-user-authenticated'),
                preferences: {}
            },
            ui: {
                sidebarOpen: false,
                currentModal: null,
                searchOpen: false
            }
        });

        // Initialize components
        this.initializeComponents();

        // Initialize analytics in production
        if (!document.body.hasAttribute('data-debug')) {
            this.initializeAnalytics();
        }

        // Bind global event listeners
        this.bindEvents();
    }

    initializeComponents() {
        // Initialize search
        if (document.querySelector('[data-search-input]')) {
            this.search = new SearchComponent({
                searchInputSelector: '[data-search-input]',
                resultsContainerSelector: '[data-search-results]',
                suggestionsContainerSelector: '[data-search-suggestions]',
                loadingIndicatorSelector: '[data-search-loading]'
            });
        }

        // Initialize infinite scroll for article lists
        if (document.querySelector('[data-infinite-scroll]')) {
            this.infiniteScroll = new InfiniteScroll({
                containerSelector: '[data-infinite-scroll]',
                itemSelector: '[data-scroll-item]',
                loadingSelector: '[data-scroll-loading]',
                endMessageSelector: '[data-scroll-end]'
            });
        }

        // Initialize lazy loading for images
        this.lazyLoad = new LazyLoad({
            selector: '[data-lazy]',
            rootMargin: '50px 0px',
            threshold: 0.01
        });

        // Initialize theme handling
        this.initializeTheme();
    }

    initializeAnalytics() {
        // Initialize analytics tracking
        this.analytics = new Analytics({
            enablePageViews: true,
            enableEvents: true,
            enableUserTracking: true,
            excludePaths: ['/admin/', '/api/']
        });

        // Initialize performance monitoring
        this.performanceMonitor = new PerformanceMonitor({
            enableResourceTiming: true,
            enableUserTiming: true,
            enableLongTaskMonitoring: true
        });
    }

    initializeTheme() {
        // Subscribe to theme changes
        state.subscribe('theme', theme => {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        });

        // Handle theme toggle clicks
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = state.get('theme');
                state.set('theme', currentTheme === 'light' ? 'dark' : 'light');
            });
        }

        // Handle system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (!localStorage.getItem('theme')) {
                state.set('theme', e.matches ? 'dark' : 'light');
            }
        });
    }

    bindEvents() {
        // Handle mobile menu
        const mobileMenuButton = document.querySelector('[data-mobile-menu-button]');
        const mobileMenu = document.querySelector('[data-mobile-menu]');

        if (mobileMenuButton && mobileMenu) {
            mobileMenuButton.addEventListener('click', () => {
                const isOpen = state.get('ui.sidebarOpen');
                state.set('ui.sidebarOpen', !isOpen);
                mobileMenu.classList.toggle('hidden', isOpen);
                document.body.classList.toggle('overflow-hidden', !isOpen);
            });
        }

        // Handle modals
        document.addEventListener('click', e => {
            const modalTrigger = e.target.closest('[data-modal-trigger]');
            if (modalTrigger) {
                const modalId = modalTrigger.dataset.modalTrigger;
                const modal = document.getElementById(modalId);
                if (modal) {
                    state.set('ui.currentModal', modalId);
                    modal.classList.remove('hidden');
                    modal.setAttribute('aria-hidden', 'false');
                }
            }
        });

        // Handle form submissions
        document.addEventListener('submit', e => {
            const form = e.target;
            if (form.hasAttribute('data-form')) {
                e.preventDefault();
                this.handleFormSubmit(form);
            }
        });
    }

    async handleFormSubmit(form) {
        try {
            const formData = Utils.forms.serialize(form);
            const response = await fetch(form.action, {
                method: form.method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': Utils.dom.get('[name=csrfmiddlewaretoken]')?.value
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) throw new Error('Form submission failed');

            const data = await response.json();
            this.handleFormSuccess(form, data);
        } catch (error) {
            this.handleFormError(form, error);
        }
    }

    handleFormSuccess(form, data) {
        // Show success message
        const message = data.message || 'Form submitted successfully';
        this.showNotification('success', message);

        // Reset form
        form.reset();

        // Trigger success event
        form.dispatchEvent(new CustomEvent('form:success', { detail: data }));
    }

    handleFormError(form, error) {
        // Show error message
        this.showNotification('error', error.message);

        // Trigger error event
        form.dispatchEvent(new CustomEvent('form:error', { detail: error }));
    }

    showNotification(type, message) {
        const notification = Utils.dom.create('div', {
            class: `notification notification-${type}`,
            role: 'alert'
        }, [message]);

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

// Export for use in other modules
export default App;

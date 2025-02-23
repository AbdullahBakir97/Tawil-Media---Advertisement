import Utils from '../core/utils.js';
import state from '../core/state.js';

class Analytics {
    constructor(options = {}) {
        this.options = {
            trackingId: null,
            enablePageViews: true,
            enableEvents: true,
            enablePerformance: true,
            enableErrors: true,
            enableUserTracking: true,
            sampleRate: 100, // Percentage of users to track
            excludePaths: [],
            localStorage: true,
            ...options
        };

        this.state = {
            initialized: false,
            pageViewsSent: 0,
            eventsSent: 0,
            errors: [],
            sessionId: null,
            userId: null
        };

        this.queue = [];
        this.init();
    }

    init() {
        // Initialize state
        state.set('analytics', this.state);

        // Check if tracking should be enabled for this user
        if (!this.shouldTrack()) {
            console.log('Analytics tracking disabled for this user');
            return;
        }

        // Initialize session
        this.initializeSession();

        // Set up event listeners
        if (this.options.enablePageViews) {
            this.setupPageViewTracking();
        }

        if (this.options.enableEvents) {
            this.setupEventTracking();
        }

        if (this.options.enableErrors) {
            this.setupErrorTracking();
        }

        if (this.options.enablePerformance) {
            this.setupPerformanceTracking();
        }

        // Process any queued events
        this.processQueue();

        // Mark as initialized
        this.updateState({ initialized: true });
    }

    shouldTrack() {
        // Check if path is excluded
        const currentPath = window.location.pathname;
        if (this.options.excludePaths.some(path => 
            currentPath.startsWith(path) || 
            new RegExp(path).test(currentPath)
        )) {
            return false;
        }

        // Check sampling rate
        const userSample = this.getUserSample();
        return userSample <= this.options.sampleRate;
    }

    getUserSample() {
        let sample = this.storage.get('analytics_sample');
        if (sample === null) {
            sample = Math.floor(Math.random() * 100) + 1;
            this.storage.set('analytics_sample', sample);
        }
        return sample;
    }

    initializeSession() {
        // Generate or retrieve session ID
        this.state.sessionId = this.storage.get('session_id');
        if (!this.state.sessionId) {
            this.state.sessionId = this.generateId();
            this.storage.set('session_id', this.state.sessionId, 30 * 60 * 1000); // 30 minutes
        }

        // Get or generate user ID
        if (this.options.enableUserTracking) {
            this.state.userId = this.storage.get('user_id');
            if (!this.state.userId) {
                this.state.userId = this.generateId();
                this.storage.set('user_id', this.state.userId);
            }
        }
    }

    setupPageViewTracking() {
        // Track initial page view
        this.trackPageView();

        // Track subsequent navigation
        window.addEventListener('popstate', () => this.trackPageView());
        
        // Track programmatic navigation
        const originalPushState = history.pushState;
        history.pushState = (...args) => {
            originalPushState.apply(history, args);
            this.trackPageView();
        };
    }

    setupEventTracking() {
        // Track clicks
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-track]');
            if (target) {
                const eventData = this.parseDataAttributes(target);
                this.trackEvent(eventData.event || 'click', eventData);
            }
        });

        // Track form submissions
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.hasAttribute('data-track')) {
                const eventData = this.parseDataAttributes(form);
                this.trackEvent('form_submit', {
                    form_id: form.id || undefined,
                    ...eventData
                });
            }
        });
    }

    setupErrorTracking() {
        window.addEventListener('error', (e) => {
            this.trackError({
                type: 'error',
                message: e.message,
                filename: e.filename,
                lineno: e.lineno,
                colno: e.colno,
                stack: e.error?.stack
            });
        });

        window.addEventListener('unhandledrejection', (e) => {
            this.trackError({
                type: 'promise_rejection',
                message: e.reason?.message || 'Unhandled Promise Rejection',
                stack: e.reason?.stack
            });
        });
    }

    setupPerformanceTracking() {
        // Track performance metrics when available
        if ('performance' in window) {
            window.addEventListener('load', () => {
                requestAnimationFrame(() => {
                    setTimeout(() => {
                        const metrics = this.collectPerformanceMetrics();
                        this.trackEvent('performance', metrics);
                    }, 0);
                });
            });
        }
    }

    // Tracking Methods

    trackPageView(path = window.location.pathname) {
        if (!this.shouldTrackPath(path)) return;

        const data = {
            path,
            title: document.title,
            referrer: document.referrer,
            timestamp: new Date().toISOString()
        };

        this.send('pageview', data);
        this.updateState({ pageViewsSent: this.state.pageViewsSent + 1 });
    }

    trackEvent(eventName, eventData = {}) {
        const data = {
            event: eventName,
            ...eventData,
            timestamp: new Date().toISOString()
        };

        this.send('event', data);
        this.updateState({ eventsSent: this.state.eventsSent + 1 });
    }

    trackError(errorData) {
        const data = {
            ...errorData,
            timestamp: new Date().toISOString()
        };

        this.send('error', data);
        this.updateState({ 
            errors: [...this.state.errors, data]
        });
    }

    // Helper Methods

    shouldTrackPath(path) {
        return !this.options.excludePaths.some(excluded => 
            path.startsWith(excluded) || new RegExp(excluded).test(path)
        );
    }

    parseDataAttributes(element) {
        const data = {};
        for (const key in element.dataset) {
            if (key.startsWith('track')) {
                const dataKey = key.replace('track', '').toLowerCase();
                data[dataKey] = element.dataset[key];
            }
        }
        return data;
    }

    collectPerformanceMetrics() {
        const navigation = performance.getEntriesByType('navigation')[0];
        const paint = performance.getEntriesByType('paint');
        
        return {
            navigationTiming: {
                dnsLookup: navigation.domainLookupEnd - navigation.domainLookupStart,
                tcpConnection: navigation.connectEnd - navigation.connectStart,
                serverResponse: navigation.responseEnd - navigation.requestStart,
                domComplete: navigation.domComplete,
                loadEvent: navigation.loadEventEnd - navigation.loadEventStart
            },
            paintTiming: {
                firstPaint: paint.find(p => p.name === 'first-paint')?.startTime,
                firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime
            },
            memory: performance.memory ? {
                usedJSHeapSize: performance.memory.usedJSHeapSize,
                totalJSHeapSize: performance.memory.totalJSHeapSize
            } : undefined
        };
    }

    generateId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
            const r = (Math.random() * 16) | 0;
            const v = c === 'x' ? r : (r & 0x3) | 0x8;
            return v.toString(16);
        });
    }

    // Data Management

    send(type, data) {
        const payload = {
            type,
            data,
            metadata: this.getMetadata()
        };

        if (!this.state.initialized) {
            this.queue.push(payload);
            return;
        }

        this.sendToServer(payload);
    }

    async sendToServer(payload) {
        try {
            const response = await fetch('/api/analytics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload),
                keepalive: true
            });

            if (!response.ok) {
                throw new Error(`Analytics request failed: ${response.status}`);
            }
        } catch (error) {
            console.error('Failed to send analytics:', error);
            this.queue.push(payload);
        }
    }

    processQueue() {
        while (this.queue.length > 0) {
            const payload = this.queue.shift();
            this.sendToServer(payload);
        }
    }

    getMetadata() {
        return {
            sessionId: this.state.sessionId,
            userId: this.state.userId,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            language: navigator.language,
            screenResolution: `${window.screen.width}x${window.screen.height}`,
            viewport: `${window.innerWidth}x${window.innerHeight}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };
    }

    // State Management

    updateState(newState) {
        state.set('analytics', {
            ...state.get('analytics'),
            ...newState
        });
    }

    // Storage Utilities

    storage = {
        get(key) {
            if (!this.options.localStorage) return null;
            try {
                const item = localStorage.getItem(`analytics_${key}`);
                return item ? JSON.parse(item) : null;
            } catch {
                return null;
            }
        },

        set(key, value, ttl = null) {
            if (!this.options.localStorage) return;
            try {
                const item = {
                    value,
                    expires: ttl ? Date.now() + ttl : null
                };
                localStorage.setItem(`analytics_${key}`, JSON.stringify(item));
            } catch {
                // Storage might be full or disabled
            }
        }
    }
}

export default Analytics;

// Example usage:
/*
import Analytics from './analytics/tracking.js';

const analytics = new Analytics({
    trackingId: 'UA-XXXXX-Y',
    enablePageViews: true,
    enableEvents: true,
    enablePerformance: true,
    enableErrors: true,
    enableUserTracking: true,
    sampleRate: 100,
    excludePaths: ['/admin/', '/api/'],
    localStorage: true
});

// Track custom events
analytics.trackEvent('button_click', {
    buttonId: 'signup',
    location: 'header'
});

// HTML Usage:
<button data-track 
        data-track-event="signup_click" 
        data-track-location="header" 
        data-track-variant="blue">
    Sign Up
</button>

<form data-track 
      data-track-form="contact" 
      data-track-source="homepage">
    ...
</form>
*/

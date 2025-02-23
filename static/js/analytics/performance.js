import Utils from '../core/utils.js';
import state from '../core/state.js';

class PerformanceMonitor {
    constructor(options = {}) {
        this.options = {
            enableResourceTiming: true,
            enableUserTiming: true,
            enableLongTaskMonitoring: true,
            enableMemoryMonitoring: true,
            enableLayoutShiftMonitoring: true,
            sampleRate: 100,
            reportingEndpoint: '/api/performance',
            reportingInterval: 10000, // 10 seconds
            longTaskThreshold: 50, // milliseconds
            maxBufferSize: 100,
            ...options
        };

        this.state = {
            initialized: false,
            metrics: {
                navigation: null,
                resources: [],
                marks: [],
                measures: [],
                longTasks: [],
                layoutShifts: [],
                memory: []
            },
            buffer: []
        };

        this.init();
    }

    init() {
        // Initialize state
        state.set('performance', this.state);

        // Check browser support
        if (!this.checkSupport()) {
            console.warn('Performance API not fully supported');
            return;
        }

        // Initialize observers and listeners
        this.setupObservers();

        // Start periodic reporting
        this.startReporting();

        // Mark as initialized
        this.updateState({ initialized: true });

        // Record initial page load
        this.recordPageLoad();
    }

    checkSupport() {
        const support = {
            performance: 'performance' in window,
            performanceObserver: 'PerformanceObserver' in window,
            resourceTiming: 'resource' in performance.getEntriesByType('resource'),
            userTiming: 'mark' in performance && 'measure' in performance,
            longTasks: 'TaskAttributionTiming' in window,
            layoutShift: 'LayoutShift' in window
        };

        return Object.values(support).some(supported => supported);
    }

    setupObservers() {
        // Resource Timing
        if (this.options.enableResourceTiming) {
            this.observeEntries('resource', entry => {
                this.addMetric('resources', this.processResourceEntry(entry));
            });
        }

        // User Timing
        if (this.options.enableUserTiming) {
            this.observeEntries(['mark', 'measure'], entry => {
                const type = entry.entryType === 'mark' ? 'marks' : 'measures';
                this.addMetric(type, this.processUserTimingEntry(entry));
            });
        }

        // Long Tasks
        if (this.options.enableLongTaskMonitoring) {
            this.observeEntries('longtask', entry => {
                if (entry.duration >= this.options.longTaskThreshold) {
                    this.addMetric('longTasks', this.processLongTaskEntry(entry));
                }
            });
        }

        // Layout Shifts
        if (this.options.enableLayoutShiftMonitoring) {
            this.observeEntries('layout-shift', entry => {
                this.addMetric('layoutShifts', this.processLayoutShiftEntry(entry));
            });
        }

        // Memory
        if (this.options.enableMemoryMonitoring && performance.memory) {
            setInterval(() => {
                this.addMetric('memory', this.collectMemoryMetrics());
            }, 5000);
        }
    }

    observeEntries(entryTypes, callback) {
        try {
            const observer = new PerformanceObserver(list => {
                list.getEntries().forEach(callback);
            });

            observer.observe({ 
                entryTypes: Array.isArray(entryTypes) ? entryTypes : [entryTypes]
            });
        } catch (error) {
            console.warn(`Failed to observe ${entryTypes}:`, error);
        }
    }

    // Metric Processing

    processResourceEntry(entry) {
        return {
            name: entry.name,
            initiatorType: entry.initiatorType,
            duration: entry.duration,
            transferSize: entry.transferSize,
            encodedBodySize: entry.encodedBodySize,
            decodedBodySize: entry.decodedBodySize,
            timing: {
                dns: entry.domainLookupEnd - entry.domainLookupStart,
                tcp: entry.connectEnd - entry.connectStart,
                ssl: entry.secureConnectionStart > 0 ? 
                    entry.connectEnd - entry.secureConnectionStart : 0,
                ttfb: entry.responseStart - entry.requestStart,
                download: entry.responseEnd - entry.responseStart
            },
            timestamp: entry.startTime
        };
    }

    processUserTimingEntry(entry) {
        return {
            name: entry.name,
            type: entry.entryType,
            duration: entry.duration,
            startTime: entry.startTime,
            detail: entry.detail
        };
    }

    processLongTaskEntry(entry) {
        return {
            duration: entry.duration,
            startTime: entry.startTime,
            attribution: entry.attribution.map(attr => ({
                name: attr.name,
                containerType: attr.containerType,
                containerName: attr.containerName,
                containerId: attr.containerId
            }))
        };
    }

    processLayoutShiftEntry(entry) {
        return {
            value: entry.value,
            startTime: entry.startTime,
            hadRecentInput: entry.hadRecentInput,
            sources: entry.sources.map(source => ({
                node: this.getNodePath(source.node),
                currentRect: source.currentRect,
                previousRect: source.previousRect
            }))
        };
    }

    collectMemoryMetrics() {
        if (!performance.memory) return null;

        return {
            usedJSHeapSize: performance.memory.usedJSHeapSize,
            totalJSHeapSize: performance.memory.totalJSHeapSize,
            jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
            timestamp: Date.now()
        };
    }

    // Page Load Metrics

    recordPageLoad() {
        window.addEventListener('load', () => {
            requestAnimationFrame(() => {
                setTimeout(() => {
                    const navigationEntry = performance.getEntriesByType('navigation')[0];
                    if (navigationEntry) {
                        this.updateState({
                            metrics: {
                                ...this.state.metrics,
                                navigation: this.processNavigationEntry(navigationEntry)
                            }
                        });
                    }
                }, 0);
            });
        });
    }

    processNavigationEntry(entry) {
        return {
            type: entry.type,
            timing: {
                dns: entry.domainLookupEnd - entry.domainLookupStart,
                tcp: entry.connectEnd - entry.connectStart,
                ssl: entry.secureConnectionStart > 0 ? 
                    entry.connectEnd - entry.secureConnectionStart : 0,
                ttfb: entry.responseStart - entry.requestStart,
                download: entry.responseEnd - entry.responseStart,
                domInteractive: entry.domInteractive,
                domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
                domComplete: entry.domComplete,
                loadEvent: entry.loadEventEnd - entry.loadEventStart
            },
            size: {
                transferSize: entry.transferSize,
                encodedBodySize: entry.encodedBodySize,
                decodedBodySize: entry.decodedBodySize
            },
            cache: {
                type: entry.transferSize === 0 ? 'memory' : 
                      entry.transferSize < entry.encodedBodySize ? 'disk' : 'none'
            }
        };
    }

    // Utility Methods

    mark(name, detail = null) {
        if (!this.options.enableUserTiming) return;
        
        try {
            performance.mark(name, { detail });
        } catch (error) {
            console.warn('Failed to create performance mark:', error);
        }
    }

    measure(name, startMark, endMark, detail = null) {
        if (!this.options.enableUserTiming) return;
        
        try {
            performance.measure(name, startMark, endMark, { detail });
        } catch (error) {
            console.warn('Failed to create performance measure:', error);
        }
    }

    getNodePath(node) {
        if (!node) return null;

        const path = [];
        let current = node;

        while (current && current !== document.documentElement) {
            let identifier = current.id ? `#${current.id}` : current.tagName.toLowerCase();
            
            if (!current.id) {
                const siblings = Array.from(current.parentNode?.children || []);
                const index = siblings.indexOf(current) + 1;
                if (siblings.length > 1) {
                    identifier += `:nth-child(${index})`;
                }
            }

            path.unshift(identifier);
            current = current.parentNode;
        }

        return path.join(' > ');
    }

    // Data Management

    addMetric(type, data) {
        if (!data) return;

        this.updateState({
            metrics: {
                ...this.state.metrics,
                [type]: [...this.state.metrics[type], data]
            }
        });

        this.buffer.push({
            type,
            data,
            timestamp: Date.now()
        });

        if (this.buffer.length >= this.options.maxBufferSize) {
            this.flushMetrics();
        }
    }

    async flushMetrics() {
        if (!this.buffer.length) return;

        const metrics = [...this.buffer];
        this.buffer = [];

        try {
            await this.sendMetrics(metrics);
        } catch (error) {
            console.error('Failed to send metrics:', error);
            // Restore metrics to buffer if send fails
            this.buffer.unshift(...metrics);
        }
    }

    async sendMetrics(metrics) {
        const payload = {
            metrics,
            metadata: this.getMetadata()
        };

        const response = await fetch(this.options.reportingEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
            keepalive: true
        });

        if (!response.ok) {
            throw new Error(`Failed to send metrics: ${response.status}`);
        }
    }

    getMetadata() {
        return {
            url: window.location.href,
            userAgent: navigator.userAgent,
            timestamp: Date.now(),
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            connection: navigator.connection ? {
                type: navigator.connection.effectiveType,
                rtt: navigator.connection.rtt,
                downlink: navigator.connection.downlink
            } : null
        };
    }

    // Lifecycle Management

    startReporting() {
        this.reportingInterval = setInterval(() => {
            this.flushMetrics();
        }, this.options.reportingInterval);
    }

    stopReporting() {
        clearInterval(this.reportingInterval);
    }

    updateState(newState) {
        state.set('performance', {
            ...state.get('performance'),
            ...newState
        });
    }

    destroy() {
        this.stopReporting();
        this.flushMetrics();
    }
}

export default PerformanceMonitor;

// Example usage:
/*
import PerformanceMonitor from './analytics/performance.js';

const monitor = new PerformanceMonitor({
    enableResourceTiming: true,
    enableUserTiming: true,
    enableLongTaskMonitoring: true,
    enableMemoryMonitoring: true,
    enableLayoutShiftMonitoring: true,
    sampleRate: 100,
    reportingEndpoint: '/api/performance',
    reportingInterval: 10000,
    longTaskThreshold: 50,
    maxBufferSize: 100
});

// Create performance marks
monitor.mark('feature-render-start');
// ... some code ...
monitor.mark('feature-render-end');

// Create performance measure
monitor.measure(
    'feature-render-time',
    'feature-render-start',
    'feature-render-end',
    { component: 'FeatureX' }
);
*/

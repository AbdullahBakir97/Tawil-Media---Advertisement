// State Management System
class StateManager {
    constructor() {
        this.state = {};
        this.subscribers = new Map();
        this.history = [];
        this.historyLimit = 50;
        this.version = 1;
    }

    /**
     * Initialize state with default values
     * @param {Object} initialState - Initial state object
     */
    init(initialState = {}) {
        this.state = this.deepClone(initialState);
        this.notifySubscribers('*', this.state);
    }

    /**
     * Get current state or specific path
     * @param {string} [path] - Optional dot notation path
     * @returns {*}
     */
    get(path) {
        if (!path) return this.deepClone(this.state);
        return this.getNestedValue(this.state, path);
    }

    /**
     * Set state value at path
     * @param {string} path - Dot notation path
     * @param {*} value - New value
     * @param {Object} [options={ silent: false }] - Options
     */
    set(path, value, options = { silent: false }) {
        const oldState = this.deepClone(this.state);
        
        if (path === '*') {
            this.state = this.deepClone(value);
        } else {
            this.setNestedValue(this.state, path, this.deepClone(value));
        }

        if (!options.silent) {
            this.addToHistory(oldState);
            this.notifySubscribers(path, this.get(path));
        }
    }

    /**
     * Subscribe to state changes
     * @param {string} path - Dot notation path
     * @param {Function} callback - Callback function
     * @returns {Function} Unsubscribe function
     */
    subscribe(path, callback) {
        if (!this.subscribers.has(path)) {
            this.subscribers.set(path, new Set());
        }
        
        this.subscribers.get(path).add(callback);
        
        // Initial callback with current value
        callback(this.get(path));
        
        // Return unsubscribe function
        return () => {
            const subs = this.subscribers.get(path);
            if (subs) {
                subs.delete(callback);
                if (subs.size === 0) {
                    this.subscribers.delete(path);
                }
            }
        };
    }

    /**
     * Batch multiple state updates
     * @param {Function} updateFn - Function containing multiple updates
     */
    batch(updateFn) {
        const oldState = this.deepClone(this.state);
        const affected = new Set();

        const batchSet = (path, value) => {
            this.setNestedValue(this.state, path, this.deepClone(value));
            affected.add(path);
        };

        updateFn(batchSet);

        this.addToHistory(oldState);
        affected.forEach(path => {
            this.notifySubscribers(path, this.get(path));
        });
    }

    /**
     * Undo last state change
     * @returns {boolean} Success
     */
    undo() {
        if (this.history.length === 0) return false;
        
        const previousState = this.history.pop();
        const oldState = this.deepClone(this.state);
        this.state = this.deepClone(previousState);
        
        this.notifySubscribers('*', this.state);
        return true;
    }

    /**
     * Reset state to initial values
     * @param {Object} [initialState={}] - Initial state
     */
    reset(initialState = {}) {
        this.history = [];
        this.init(initialState);
    }

    /**
     * Persist state to storage
     * @param {string} [key='app_state'] - Storage key
     */
    persist(key = 'app_state') {
        try {
            localStorage.setItem(key, JSON.stringify({
                state: this.state,
                version: this.version,
                timestamp: Date.now()
            }));
        } catch (error) {
            console.error('Failed to persist state:', error);
        }
    }

    /**
     * Hydrate state from storage
     * @param {string} [key='app_state'] - Storage key
     * @returns {boolean} Success
     */
    hydrate(key = 'app_state') {
        try {
            const stored = localStorage.getItem(key);
            if (!stored) return false;

            const { state, version, timestamp } = JSON.parse(stored);
            
            // Version check
            if (version !== this.version) {
                console.warn('State version mismatch, skipping hydration');
                return false;
            }

            this.state = this.deepClone(state);
            this.notifySubscribers('*', this.state);
            return true;
        } catch (error) {
            console.error('Failed to hydrate state:', error);
            return false;
        }
    }

    // Private Methods

    /**
     * Notify subscribers of state change
     * @private
     * @param {string} path - Changed path
     * @param {*} value - New value
     */
    notifySubscribers(path, value) {
        // Notify exact path subscribers
        const subs = this.subscribers.get(path);
        if (subs) {
            subs.forEach(callback => callback(value));
        }

        // Notify wildcard subscribers
        const wildcardSubs = this.subscribers.get('*');
        if (wildcardSubs) {
            wildcardSubs.forEach(callback => callback(this.state));
        }
    }

    /**
     * Add state to history
     * @private
     * @param {Object} state - State to add
     */
    addToHistory(state) {
        this.history.push(state);
        if (this.history.length > this.historyLimit) {
            this.history.shift();
        }
    }

    /**
     * Get nested object value by path
     * @private
     * @param {Object} obj - Object to traverse
     * @param {string} path - Dot notation path
     * @returns {*}
     */
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => 
            current && current[key] !== undefined ? current[key] : undefined, obj);
    }

    /**
     * Set nested object value by path
     * @private
     * @param {Object} obj - Object to traverse
     * @param {string} path - Dot notation path
     * @param {*} value - Value to set
     */
    setNestedValue(obj, path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        const target = keys.reduce((current, key) => {
            if (!(key in current)) {
                current[key] = {};
            }
            return current[key];
        }, obj);
        target[lastKey] = value;
    }

    /**
     * Deep clone object
     * @private
     * @param {*} obj - Object to clone
     * @returns {*}
     */
    deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj);
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (obj instanceof Object) {
            return Object.fromEntries(
                Object.entries(obj).map(([key, value]) => [key, this.deepClone(value)])
            );
        }
        return obj;
    }
}

// Create and export state manager instance
const stateManager = new StateManager();
export default stateManager;

// Example usage:
/*
import state from './state.js';

// Initialize state
state.init({
    user: {
        isLoggedIn: false,
        preferences: {
            theme: 'light'
        }
    },
    content: {
        articles: [],
        loading: false
    }
});

// Subscribe to changes
state.subscribe('user.preferences.theme', theme => {
    document.documentElement.setAttribute('data-theme', theme);
});

// Update state
state.set('user.preferences.theme', 'dark');

// Batch updates
state.batch(set => {
    set('content.loading', true);
    set('content.articles', []);
});

// Persist state
state.persist();

// Hydrate state on page load
document.addEventListener('DOMContentLoaded', () => {
    state.hydrate();
});
*/

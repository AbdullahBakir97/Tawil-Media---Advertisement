// Utility Functions and Helpers
const Utils = {
    // DOM Manipulation
    dom: {
        /**
         * Get element by selector with type checking
         * @param {string} selector - CSS selector
         * @param {Element} [context=document] - Context to search within
         * @returns {Element|null}
         */
        get(selector, context = document) {
            return context.querySelector(selector);
        },

        /**
         * Get all elements by selector with type checking
         * @param {string} selector - CSS selector
         * @param {Element} [context=document] - Context to search within
         * @returns {Element[]}
         */
        getAll(selector, context = document) {
            return Array.from(context.querySelectorAll(selector));
        },

        /**
         * Create element with attributes and children
         * @param {string} tag - HTML tag name
         * @param {Object} [attrs={}] - Attributes to set
         * @param {Array} [children=[]] - Child elements or text
         * @returns {Element}
         */
        create(tag, attrs = {}, children = []) {
            const element = document.createElement(tag);
            
            Object.entries(attrs).forEach(([key, value]) => {
                if (key === 'class') {
                    element.className = value;
                } else if (key === 'style' && typeof value === 'object') {
                    Object.assign(element.style, value);
                } else {
                    element.setAttribute(key, value);
                }
            });

            children.forEach(child => {
                if (typeof child === 'string') {
                    element.appendChild(document.createTextNode(child));
                } else {
                    element.appendChild(child);
                }
            });

            return element;
        }
    },

    // Event Handling
    events: {
        /**
         * Debounce function calls
         * @param {Function} fn - Function to debounce
         * @param {number} delay - Delay in milliseconds
         * @returns {Function}
         */
        debounce(fn, delay) {
            let timeoutId;
            return function (...args) {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => fn.apply(this, args), delay);
            };
        },

        /**
         * Throttle function calls
         * @param {Function} fn - Function to throttle
         * @param {number} limit - Limit in milliseconds
         * @returns {Function}
         */
        throttle(fn, limit) {
            let inThrottle;
            return function (...args) {
                if (!inThrottle) {
                    fn.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }
    },

    // Form Handling
    forms: {
        /**
         * Serialize form data to object
         * @param {HTMLFormElement} form - Form element
         * @returns {Object}
         */
        serialize(form) {
            const formData = new FormData(form);
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                if (data[key]) {
                    if (!Array.isArray(data[key])) {
                        data[key] = [data[key]];
                    }
                    data[key].push(value);
                } else {
                    data[key] = value;
                }
            }
            
            return data;
        },

        /**
         * Validate form fields
         * @param {HTMLFormElement} form - Form element
         * @returns {boolean}
         */
        validate(form) {
            const fields = form.querySelectorAll('input, select, textarea');
            let isValid = true;

            fields.forEach(field => {
                if (field.hasAttribute('required') && !field.value) {
                    isValid = false;
                    this.showError(field, 'This field is required');
                } else if (field.type === 'email' && field.value && !this.isValidEmail(field.value)) {
                    isValid = false;
                    this.showError(field, 'Please enter a valid email');
                }
            });

            return isValid;
        },

        /**
         * Show error message for form field
         * @param {HTMLElement} field - Form field
         * @param {string} message - Error message
         */
        showError(field, message) {
            const errorElement = Utils.dom.create('div', {
                class: 'form-error',
                'data-error': true
            }, [message]);

            // Remove existing error
            const existingError = field.parentNode.querySelector('[data-error]');
            if (existingError) {
                existingError.remove();
            }

            field.parentNode.appendChild(errorElement);
            field.classList.add('error');
        }
    },

    // Storage Utilities
    storage: {
        /**
         * Set item in storage with expiry
         * @param {string} key - Storage key
         * @param {*} value - Value to store
         * @param {number} [ttl] - Time to live in milliseconds
         * @param {string} [type='local'] - Storage type ('local' or 'session')
         */
        set(key, value, ttl, type = 'local') {
            const storage = type === 'local' ? localStorage : sessionStorage;
            const item = {
                value,
                timestamp: Date.now(),
                ttl
            };
            storage.setItem(key, JSON.stringify(item));
        },

        /**
         * Get item from storage
         * @param {string} key - Storage key
         * @param {string} [type='local'] - Storage type ('local' or 'session')
         * @returns {*}
         */
        get(key, type = 'local') {
            const storage = type === 'local' ? localStorage : sessionStorage;
            const item = JSON.parse(storage.getItem(key));
            
            if (!item) return null;
            
            if (item.ttl && Date.now() - item.timestamp > item.ttl) {
                storage.removeItem(key);
                return null;
            }
            
            return item.value;
        }
    },

    // String Utilities
    string: {
        /**
         * Slugify string
         * @param {string} str - String to slugify
         * @returns {string}
         */
        slugify(str) {
            return str
                .toLowerCase()
                .replace(/[^\w\s-]/g, '')
                .replace(/[\s_-]+/g, '-')
                .replace(/^-+|-+$/g, '');
        },

        /**
         * Truncate string
         * @param {string} str - String to truncate
         * @param {number} length - Maximum length
         * @param {string} [suffix='...'] - Suffix to add
         * @returns {string}
         */
        truncate(str, length, suffix = '...') {
            if (str.length <= length) return str;
            return str.substring(0, length - suffix.length) + suffix;
        }
    },

    // Date Utilities
    date: {
        /**
         * Format date
         * @param {Date|string} date - Date to format
         * @param {string} [format='YYYY-MM-DD'] - Date format
         * @returns {string}
         */
        format(date, format = 'YYYY-MM-DD') {
            date = new Date(date);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            
            return format
                .replace('YYYY', year)
                .replace('MM', month)
                .replace('DD', day)
                .replace('HH', hours)
                .replace('mm', minutes);
        },

        /**
         * Get relative time string
         * @param {Date|string} date - Date to compare
         * @returns {string}
         */
        relative(date) {
            const now = new Date();
            const then = new Date(date);
            const diff = Math.floor((now - then) / 1000);
            
            if (diff < 60) return 'just now';
            if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
            if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
            if (diff < 2592000) return `${Math.floor(diff / 86400)}d ago`;
            return this.format(date);
        }
    },

    // Validation Utilities
    validation: {
        /**
         * Validate email
         * @param {string} email - Email to validate
         * @returns {boolean}
         */
        isValidEmail(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        },

        /**
         * Validate URL
         * @param {string} url - URL to validate
         * @returns {boolean}
         */
        isValidUrl(url) {
            try {
                new URL(url);
                return true;
            } catch {
                return false;
            }
        }
    }
};

// Export as module
export default Utils;

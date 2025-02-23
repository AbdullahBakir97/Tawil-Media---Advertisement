// HTMX Configuration and Extensions
(function() {
    // HTMX Global Configuration
    htmx.config = {
        historyEnabled: true,
        defaultSwapStyle: 'innerHTML',
        defaultSwapDelay: 0,
        defaultSettleDelay: 20,
        includeIndicatorStyles: false,
        indicatorClass: 'htmx-indicator',
        requestClass: 'htmx-request',
        addedClass: 'htmx-added',
        settlingClass: 'htmx-settling',
        swappingClass: 'htmx-swapping',
        allowEval: false,
        attributesToSettle: ["class", "style", "width", "height"]
    };

    // Custom Loading States
    htmx.defineExtension('loading-states', {
        onEvent: function(name, evt) {
            if (name === "htmx:beforeRequest") {
                const target = evt.detail.target;
                const loadingStates = target.querySelectorAll('[data-loading]');
                
                loadingStates.forEach(el => {
                    const loadingText = el.dataset.loading;
                    el.dataset.originalText = el.innerText;
                    el.innerText = loadingText;
                    el.classList.add('is-loading');
                });
            }
            
            if (name === "htmx:afterRequest") {
                const target = evt.detail.target;
                const loadingStates = target.querySelectorAll('[data-loading]');
                
                loadingStates.forEach(el => {
                    el.innerText = el.dataset.originalText;
                    delete el.dataset.originalText;
                    el.classList.remove('is-loading');
                });
            }
        }
    });

    // Custom Error Handling
    htmx.defineExtension('error-handling', {
        onEvent: function(name, evt) {
            if (name === "htmx:responseError" || name === "htmx:sendError") {
                const target = evt.detail.target;
                const errorMessage = evt.detail.error || 'An error occurred';
                
                // Create error toast
                createToast({
                    type: 'error',
                    message: errorMessage,
                    duration: 5000
                });
            }
        }
    });

    // Custom Analytics Extension
    htmx.defineExtension('analytics', {
        onEvent: function(name, evt) {
            if (name === "htmx:afterRequest") {
                const path = evt.detail.pathInfo.requestPath;
                const method = evt.detail.requestConfig.method;
                
                // Track HTMX requests
                window.analytics?.trackEvent('htmx_request', {
                    path: path,
                    method: method,
                    status: evt.detail.xhr.status,
                    duration: evt.detail.duration
                });
            }
        }
    });

    // Custom Form Validation
    htmx.defineExtension('form-validation', {
        onEvent: function(name, evt) {
            if (name === "htmx:validateRequest") {
                const elt = evt.detail.elt;
                
                if (elt.tagName === "FORM") {
                    const isValid = elt.checkValidity();
                    if (!isValid) {
                        evt.preventDefault();
                        showFormErrors(elt);
                    }
                }
            }
        }
    });

    // Initialize Extensions
    htmx.addExtension('loading-states');
    htmx.addExtension('error-handling');
    htmx.addExtension('analytics');
    htmx.addExtension('form-validation');

    // Custom Event Handlers
    document.addEventListener('htmx:configRequest', function(evt) {
        // Add CSRF token to all requests
        evt.detail.headers['X-CSRFToken'] = getCookie('csrftoken');
    });

    document.addEventListener('htmx:afterSwap', function(evt) {
        // Reinitialize components after content swap
        initializeComponents(evt.detail.target);
    });

    // Utility Functions
    function getCookie(name) {
        let value = "; " + document.cookie;
        let parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(";").shift();
    }

    function showFormErrors(form) {
        const invalidFields = form.querySelectorAll(':invalid');
        invalidFields.forEach(field => {
            const errorMessage = field.validationMessage;
            const errorElement = document.createElement('div');
            errorElement.className = 'form-error';
            errorElement.textContent = errorMessage;
            field.parentNode.appendChild(errorElement);
        });
    }

    function createToast(options) {
        const { type, message, duration } = options;
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), duration);
    }

    function initializeComponents(target) {
        // Add any component initialization logic here
        // This will be called after HTMX content swaps
    }
})();

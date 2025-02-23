# Tawil Media JavaScript Architecture

## Overview
This document outlines the JavaScript architecture for the Tawil Media platform. The codebase follows a modular, component-based architecture with centralized state management and comprehensive analytics tracking.

## Directory Structure
```
static/js/
├── core/
│   ├── htmx-conf.js   # HTMX configuration and extensions
│   ├── utils.js       # Utility functions
│   └── state.js       # State management system
├── components/
│   ├── search.js      # Search functionality
│   ├── infinite-scroll.js # Infinite scrolling
│   └── lazy-load.js   # Lazy loading images
└── analytics/
    ├── tracking.js    # Analytics tracking
    └── performance.js # Performance monitoring
```

## Core Modules

### State Management (state.js)
Centralized state management with history tracking and persistence.

```javascript
import state from './core/state.js';

// Initialize state
state.init({
    theme: 'light',
    user: {
        preferences: {}
    }
});

// Subscribe to changes
state.subscribe('theme', theme => {
    document.documentElement.setAttribute('data-theme', theme);
});

// Update state
state.set('theme', 'dark');
```

### Utility Functions (utils.js)
Common utility functions for DOM manipulation, events, forms, etc.

```javascript
import Utils from './core/utils.js';

// DOM manipulation
const element = Utils.dom.create('div', { class: 'card' }, ['Content']);

// Event handling
const debouncedFn = Utils.events.debounce(() => {}, 300);

// Form handling
const formData = Utils.forms.serialize(formElement);
```

### HTMX Configuration (htmx-conf.js)
HTMX extensions and global configuration.

```html
<!-- Loading states -->
<button data-loading="Loading...">Submit</button>

<!-- Form validation -->
<form hx-post="/api/submit" hx-validate="true">
    ...
</form>
```

## Components

### Search Component
Advanced search with suggestions and keyboard navigation.

```html
<div class="search-container">
    <input type="search" 
           data-search-input
           placeholder="Search...">
    <div data-search-suggestions></div>
    <div data-search-results></div>
</div>

<script>
import SearchComponent from './components/search.js';

const search = new SearchComponent({
    searchInputSelector: '[data-search-input]',
    suggestionsContainerSelector: '[data-search-suggestions]',
    resultsContainerSelector: '[data-search-results]'
});
</script>
```

### Infinite Scroll
Infinite scrolling for content lists.

```html
<div data-infinite-scroll>
    <div data-scroll-item>Item 1</div>
    <div data-scroll-item>Item 2</div>
    <div data-scroll-loading>Loading...</div>
    <div data-scroll-end>No more items</div>
</div>

<script>
import InfiniteScroll from './components/infinite-scroll.js';

const infiniteScroll = new InfiniteScroll({
    containerSelector: '[data-infinite-scroll]',
    itemSelector: '[data-scroll-item]'
});
</script>
```

### Lazy Loading
Lazy loading for images and other media.

```html
<img data-lazy 
     data-src="/path/to/image.jpg" 
     alt="Lazy loaded image">

<script>
import LazyLoad from './components/lazy-load.js';

const lazyLoad = new LazyLoad({
    selector: '[data-lazy]',
    rootMargin: '50px 0px'
});
</script>
```

## Analytics

### Tracking
User interaction and event tracking.

```javascript
import Analytics from './analytics/tracking.js';

const analytics = new Analytics({
    enablePageViews: true,
    enableEvents: true
});

// Track custom event
analytics.trackEvent('button_click', {
    buttonId: 'signup',
    location: 'header'
});
```

### Performance Monitoring
Performance metrics and monitoring.

```javascript
import PerformanceMonitor from './analytics/performance.js';

const monitor = new PerformanceMonitor({
    enableResourceTiming: true,
    enableUserTiming: true
});

// Create performance marks
monitor.mark('feature-render-start');
// ... some code ...
monitor.mark('feature-render-end');
monitor.measure('feature-render', 'feature-render-start', 'feature-render-end');
```

## Best Practices

1. **State Management**
   - Use the centralized state manager for shared state
   - Subscribe to state changes instead of direct manipulation
   - Use local state for component-specific data

2. **Event Handling**
   - Use event delegation for dynamic elements
   - Debounce search inputs and scroll handlers
   - Clean up event listeners when components are destroyed

3. **Performance**
   - Lazy load images and heavy content
   - Use IntersectionObserver for scroll-based features
   - Monitor and optimize resource loading

4. **Error Handling**
   - Implement proper error boundaries
   - Log errors to analytics
   - Provide user feedback for failures

5. **Accessibility**
   - Ensure keyboard navigation works
   - Maintain proper ARIA attributes
   - Test with screen readers

## Development Workflow

1. **Adding New Features**
   - Create a new component file if needed
   - Register component in app.js
   - Add necessary HTML data attributes
   - Update documentation

2. **Testing**
   - Test across different browsers
   - Verify mobile responsiveness
   - Check performance impact
   - Validate accessibility

3. **Deployment**
   - Ensure all modules are properly imported
   - Check for console errors
   - Verify analytics tracking
   - Monitor performance metrics

## Browser Support
The codebase supports modern browsers with fallbacks for:
- IntersectionObserver
- ES6 Modules
- Custom Properties (CSS Variables)

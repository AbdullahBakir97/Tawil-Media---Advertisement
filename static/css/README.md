# Tawil Media CSS Architecture

## Overview
This document outlines the CSS architecture for the Tawil Media platform. The CSS follows a modular, component-based architecture with a focus on maintainability, reusability, and performance.

## Directory Structure
```
static/css/
├── base/
│   ├── variables.css   # CSS custom properties
│   ├── typography.css  # Typography styles
│   ├── colors.css      # Color system
│   └── animations.css  # Keyframes and transitions
├── layouts/
│   ├── grid.css       # Grid system
│   ├── flex.css       # Flexbox utilities
│   └── responsive.css # Responsive utilities
├── components/
│   ├── buttons.css    # Button styles
│   ├── forms.css      # Form elements
│   ├── cards.css      # Card components
│   └── modals.css     # Modal dialogs
└── themes/
    ├── light.css      # Light theme
    └── dark.css       # Dark theme
```

## Base Styles

### Variables (variables.css)
Global CSS custom properties for consistent styling.

```css
:root {
    /* Colors */
    --color-primary: #2563eb;
    --color-secondary: #4f46e5;
    --color-success: #10b981;
    --color-warning: #f59e0b;
    --color-error: #ef4444;

    /* Typography */
    --font-sans: 'Noto Sans', sans-serif;
    --font-serif: 'Noto Serif', serif;
    --font-arabic: 'Noto Sans Arabic', sans-serif;
    
    /* Spacing */
    --spacing-xs: 0.25rem;  /* 4px */
    --spacing-sm: 0.5rem;   /* 8px */
    --spacing-md: 1rem;     /* 16px */
    --spacing-lg: 1.5rem;   /* 24px */
    --spacing-xl: 2rem;     /* 32px */

    /* Border Radius */
    --radius-sm: 0.25rem;
    --radius-md: 0.375rem;
    --radius-lg: 0.5rem;
    --radius-full: 9999px;

    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);

    /* Transitions */
    --transition-base: 200ms ease-in-out;
    --transition-smooth: 300ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Typography (typography.css)
Typography scale and text utilities.

```css
/* Font Scale */
.text-xs { font-size: 0.75rem; line-height: 1rem; }
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }
.text-base { font-size: 1rem; line-height: 1.5rem; }
.text-lg { font-size: 1.125rem; line-height: 1.75rem; }
.text-xl { font-size: 1.25rem; line-height: 1.75rem; }

/* Font Weights */
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }

/* Text Alignment */
.text-right { text-align: right; }
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-justify { text-align: justify; }
```

### Colors (colors.css)
Color system with semantic colors and utilities.

```css
/* Text Colors */
.text-primary { color: var(--color-primary); }
.text-secondary { color: var(--color-secondary); }
.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }
.text-error { color: var(--color-error); }

/* Background Colors */
.bg-primary { background-color: var(--color-primary); }
.bg-secondary { background-color: var(--color-secondary); }
.bg-success { background-color: var(--color-success); }
.bg-warning { background-color: var(--color-warning); }
.bg-error { background-color: var(--color-error); }
```

### Animations (animations.css)
Reusable animations and transitions.

```css
/* Fade */
.fade-enter {
    opacity: 0;
    transition: opacity var(--transition-base);
}
.fade-enter-active {
    opacity: 1;
}

/* Slide */
.slide-up {
    transform: translateY(1rem);
    opacity: 0;
    animation: slideUp var(--transition-smooth) forwards;
}

@keyframes slideUp {
    to {
        transform: translateY(0);
        opacity: 1;
    }
}
```

## Layout System

### Grid (grid.css)
Responsive grid system using CSS Grid.

```css
.grid {
    display: grid;
    gap: var(--spacing-md);
}

/* Grid Columns */
.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

/* Responsive Grid */
@media (min-width: 768px) {
    .md\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
    .md\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
}
```

### Flexbox (flex.css)
Flexbox utilities for layout control.

```css
.flex { display: flex; }
.inline-flex { display: inline-flex; }

/* Direction */
.flex-row { flex-direction: row; }
.flex-col { flex-direction: column; }

/* Alignment */
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.justify-center { justify-content: center; }
```

### Responsive (responsive.css)
Responsive utilities and breakpoints.

```css
/* Breakpoints */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }

/* Responsive Display */
.hidden { display: none; }
@media (min-width: 768px) {
    .md\:block { display: block; }
    .md\:hidden { display: none; }
}
```

## Components

### Buttons (buttons.css)
Button variants and states.

```css
.btn {
    display: inline-flex;
    align-items: center;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-md);
    transition: all var(--transition-base);
}

.btn-primary {
    background-color: var(--color-primary);
    color: white;
}

.btn-secondary {
    background-color: var(--color-secondary);
    color: white;
}

/* Button Sizes */
.btn-sm { padding: var(--spacing-xs) var(--spacing-sm); }
.btn-lg { padding: var(--spacing-md) var(--spacing-lg); }
```

### Forms (forms.css)
Form elements and validation states.

```css
.form-input {
    width: 100%;
    padding: var(--spacing-sm);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    transition: border-color var(--transition-base);
}

.form-input:focus {
    border-color: var(--color-primary);
    outline: none;
    box-shadow: 0 0 0 2px var(--color-primary-light);
}

/* Validation States */
.form-input.error {
    border-color: var(--color-error);
}

.form-error {
    color: var(--color-error);
    font-size: var(--text-sm);
    margin-top: var(--spacing-xs);
}
```

### Cards (cards.css)
Card components for content display.

```css
.card {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    overflow: hidden;
}

.card-header {
    padding: var(--spacing-md);
    border-bottom: 1px solid var(--color-border);
}

.card-body {
    padding: var(--spacing-md);
}

.card-footer {
    padding: var(--spacing-md);
    border-top: 1px solid var(--color-border);
}
```

## Themes

### Light Theme (light.css)
Default light theme variables.

```css
[data-theme="light"] {
    --bg-primary: white;
    --bg-secondary: #f3f4f6;
    --text-primary: #111827;
    --text-secondary: #4b5563;
    --border-color: #e5e7eb;
}
```

### Dark Theme (dark.css)
Dark theme overrides.

```css
[data-theme="dark"] {
    --bg-primary: #111827;
    --bg-secondary: #1f2937;
    --text-primary: #f9fafb;
    --text-secondary: #d1d5db;
    --border-color: #374151;
}
```

## Best Practices

1. **CSS Custom Properties**
   - Use variables for consistent values
   - Override variables in themes
   - Keep scope-specific variables local

2. **Responsive Design**
   - Mobile-first approach
   - Use breakpoint mixins
   - Test all responsive variants

3. **Performance**
   - Minimize specificity
   - Use logical property order
   - Avoid deep nesting
   - Optimize critical CSS

4. **Maintainability**
   - Follow naming conventions
   - Document complex selectors
   - Keep files focused and organized

5. **Accessibility**
   - Maintain color contrast
   - Provide focus styles
   - Support reduced motion

## Development Workflow

1. **Adding New Styles**
   - Add to appropriate category
   - Follow naming convention
   - Document usage
   - Test cross-browser

2. **Modifying Existing Styles**
   - Check dependencies
   - Test all variants
   - Update documentation
   - Verify accessibility

3. **Theme Development**
   - Test both themes
   - Check contrast ratios
   - Verify component states
   - Test transitions

## Browser Support
The CSS supports modern browsers with considerations for:
- CSS Grid and Flexbox
- Custom Properties
- CSS Animations
- Media Queries

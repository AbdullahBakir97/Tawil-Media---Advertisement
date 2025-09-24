# Tawil Media CSS Architecture

This document outlines the CSS architecture used in the Tawil Media platform. We've implemented a hybrid approach combining ITCSS (Inverted Triangle CSS) for organization and BEM (Block Element Modifier) for component naming conventions.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Folder Structure](#folder-structure)
3. [Naming Conventions](#naming-conventions)
4. [Responsive Design](#responsive-design)
5. [Theming](#theming)
6. [Build Process](#build-process)
7. [Best Practices](#best-practices)

## Architecture Overview

Our CSS architecture follows these key principles:

- **Modularity**: Components are self-contained and reusable
- **Maintainability**: Clear organization and naming conventions
- **Performance**: Optimized with PurgeCSS and minification
- **Responsiveness**: Mobile-first approach with consistent breakpoints
- **Theming**: Support for light and dark modes via CSS variables

We use SCSS as a preprocessor to leverage features like nesting, variables, mixins, and functions.

## Folder Structure

Our SCSS files are organized following the ITCSS methodology, which arranges CSS by specificity and importance:

```
scss/
├── settings/         # Global variables, config
│   ├── _variables.scss
│   ├── _colors.scss
│   ├── _breakpoints.scss
│   └── _typography.scss
├── tools/            # Mixins and functions
│   ├── _mixins.scss
│   ├── _functions.scss
│   └── _animations.scss
├── generic/          # Reset and normalize styles
│   ├── _reset.scss
│   └── _box-sizing.scss
├── elements/         # Styling for bare HTML elements
│   ├── _headings.scss
│   └── _links.scss
├── objects/          # Class-based selectors for layout patterns
│   ├── _container.scss
│   ├── _grid.scss
│   └── _flex.scss
├── components/       # Specific UI components
│   ├── _header.scss
│   ├── _buttons.scss
│   └── _cards.scss
├── utilities/        # Helper classes
│   ├── _spacing.scss
│   ├── _typography.scss
│   └── _visibility.scss
├── themes/           # Theme-specific styles
│   ├── _light.scss
│   └── _dark.scss
├── main.scss         # Main file that imports all others
└── index.scss        # Entry point for the build process
```

## Naming Conventions

We use BEM (Block Element Modifier) for naming components:

```scss
// Block
.header { }

// Element (belongs to the block)
.header__logo { }
.header__navigation { }

// Modifier (changes the style of the block or element)
.header--transparent { }
.header__logo--large { }
```

For utility classes, we use a more concise approach:

```scss
.mt-4 { margin-top: 1rem; }
.text-center { text-align: center; }
.flex-between { justify-content: space-between; }
```

## Responsive Design

We follow a mobile-first approach with consistent breakpoints:

```scss
$breakpoints: (
  'xs': 0,
  'sm': 640px,
  'md': 768px,
  'lg': 1024px,
  'xl': 1280px,
  '2xl': 1536px
);
```

Use the responsive mixins for consistent media queries:

```scss
@include respond-to('md') {
  // Styles for medium screens and up
}

@include respond-below('lg') {
  // Styles for below large screens
}
```

## Theming

We use CSS custom properties (variables) for theming:

```scss
:root {
  // Light theme (default)
  --color-background: #f9fafb;
  --color-text: #111827;
}

.dark-theme {
  // Dark theme
  --color-background: #111827;
  --color-text: #f9fafb;
}
```

Then use these variables in your components:

```scss
.card {
  background-color: var(--color-background);
  color: var(--color-text);
}
```

## Build Process

Our build process uses PostCSS with several plugins:

- **postcss-import**: For importing CSS files
- **postcss-nested**: For nesting support
- **postcss-scss**: For SCSS syntax
- **postcss-preset-env**: For future CSS features
- **tailwindcss**: For utility classes
- **autoprefixer**: For browser compatibility
- **purgecss**: For removing unused CSS
- **cssnano**: For minification

## Best Practices

1. **Follow the ITCSS order** when importing files to manage specificity
2. **Use BEM for components** to maintain clear relationships
3. **Leverage utility classes** for common patterns
4. **Keep components focused** on a single responsibility
5. **Use variables** for consistent values (colors, spacing, etc.)
6. **Document complex components** with comments
7. **Test across devices** to ensure responsive behavior
8. **Minimize nesting** to avoid specificity issues
9. **Use mixins for repeated patterns** to stay DRY
10. **Keep accessibility in mind** when styling components

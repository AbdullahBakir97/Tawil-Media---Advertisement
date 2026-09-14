/** @type {import('tailwindcss').Config} */

// Brand palette (sky). Shared by bg-/text-/border-/ring-primary-* utilities.
const primary = {
  50: '#f0f9ff',
  100: '#e0f2fe',
  200: '#bae6fd',
  300: '#7dd3fc',
  400: '#38bdf8',
  500: '#0ea5e9',
  600: '#0284c7',
  700: '#0369a1',
  800: '#075985',
  900: '#0c4a6e',
};

// Semantic surface tokens. `bg-primary` / `text-primary` / `border-primary`
// resolve to the CSS variables defined in static/css/base/variables.css so
// they follow the light/dark theme, while `bg-primary-600` etc. keep using
// the brand palette above.
const surface = (prefix) => ({
  primary: { ...primary, DEFAULT: `var(--${prefix}-primary)` },
  secondary: { DEFAULT: `var(--${prefix}-secondary)` },
  tertiary: { DEFAULT: `var(--${prefix}-tertiary)` },
});

module.exports = {
  content: ['./templates/**/*.html', './source/**/*.py', './static/js/**/*.js'],
  darkMode: 'class',
  corePlugins: { container: false },
  theme: {
    extend: {
      colors: {
        primary,
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6',
      },
      backgroundColor: surface('bg'),
      textColor: surface('text'),
      borderColor: surface('border'),
      fontFamily: {
        sans: ['"Noto Sans"', 'system-ui', 'sans-serif'],
        serif: ['"Noto Serif"', 'Georgia', 'serif'],
        arabic: ['"Noto Sans Arabic"', 'sans-serif'],
      },
      keyframes: {
        'fade-in': { from: { opacity: '0' }, to: { opacity: '1' } },
        'slide-up': {
          from: { opacity: '0', transform: 'translateY(0.5rem)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 200ms ease-out',
        'slide-up': 'slide-up 250ms ease-out',
      },
    },
  },
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography')],
};

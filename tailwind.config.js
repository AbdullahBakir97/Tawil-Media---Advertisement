/** @type {import('tailwindcss').Config} */

// Palette values mirror static/css/base/variables.css so utilities and
// custom CSS agree. Semantic surfaces (bg-primary, text-secondary, …) resolve
// to CSS variables and follow the light/dark theme automatically.

const scale = (name) =>
  Object.fromEntries([50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((n) => [n, `var(--${name}-${n})`]));

const navy = scale('navy');
const gold = scale('gold');
const sky = scale('sky');
const gray = scale('gray');

const surface = (prefix, extra = {}) => ({
  primary: { ...sky, DEFAULT: `var(--${prefix}-primary)` },
  secondary: { DEFAULT: `var(--${prefix}-secondary)` },
  tertiary: { DEFAULT: `var(--${prefix}-tertiary)` },
  ...extra,
});

module.exports = {
  content: ['./templates/**/*.html', './source/**/*.py', './static/js/**/*.js'],
  darkMode: 'class',
  corePlugins: { container: false },
  theme: {
    extend: {
      colors: {
        navy,
        gold,
        sky,
        gray,
        primary: sky,
        almadina: { DEFAULT: 'var(--red-600)', light: 'var(--red-500)', dark: 'var(--red-700)' },
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        error: 'var(--color-error)',
        info: 'var(--color-info)',
        link: { DEFAULT: 'var(--link)', hover: 'var(--link-hover)' },
        accent: { DEFAULT: 'var(--accent)', ink: 'var(--accent-ink)' },
      },
      backgroundColor: surface('bg', {
        brand: { DEFAULT: 'var(--bg-brand)', deep: 'var(--bg-brand-deep)' },
      }),
      textColor: surface('text', {
        'on-brand': { DEFAULT: 'var(--text-on-brand)', muted: 'var(--text-on-brand-muted)' },
      }),
      borderColor: surface('border'),
      ringColor: { focus: 'var(--focus-ring)' },
      fontFamily: {
        display: ['"Playfair Display"', '"Amiri"', 'Georgia', 'serif'],
        body: ['"Source Sans 3"', '"IBM Plex Sans Arabic"', 'system-ui', 'sans-serif'],
        sans: ['"Source Sans 3"', '"IBM Plex Sans Arabic"', 'system-ui', 'sans-serif'],
        serif: ['"Playfair Display"', '"Amiri"', 'Georgia', 'serif'],
        arabic: ['"IBM Plex Sans Arabic"', 'sans-serif'],
        mono: ['ui-monospace', 'Menlo', 'Consolas', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.6875rem', { lineHeight: '1rem' }],
      },
      maxWidth: {
        measure: '65ch',
        'measure-narrow': '52ch',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        DEFAULT: 'var(--shadow-base)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        xl: 'var(--shadow-xl)',
        'glow-gold': 'var(--shadow-glow-gold)',
      },
      transitionTimingFunction: {
        out: 'cubic-bezier(0.2, 0.8, 0.2, 1)',
        'in-out': 'cubic-bezier(0.65, 0, 0.35, 1)',
      },
      keyframes: {
        'fade-in': { from: { opacity: '0' }, to: { opacity: '1' } },
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(0.75rem)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: { from: { backgroundPosition: '-200% 0' }, to: { backgroundPosition: '200% 0' } },
      },
      animation: {
        'fade-in': 'fade-in 250ms ease-out',
        'fade-up': 'fade-up 400ms cubic-bezier(0.2, 0.8, 0.2, 1)',
        shimmer: 'shimmer 1.6s linear infinite',
      },
      typography: ({ theme }) => ({
        DEFAULT: {
          css: {
            '--tw-prose-body': 'var(--text-primary)',
            '--tw-prose-headings': 'var(--text-primary)',
            '--tw-prose-links': 'var(--link)',
            '--tw-prose-bold': 'var(--text-primary)',
            '--tw-prose-quotes': 'var(--text-primary)',
            '--tw-prose-quote-borders': 'var(--gold-400)',
            '--tw-prose-captions': 'var(--text-tertiary)',
            '--tw-prose-hr': 'var(--border-primary)',
            '--tw-prose-invert-body': 'var(--text-primary)',
            '--tw-prose-invert-headings': 'var(--text-primary)',
            '--tw-prose-invert-links': 'var(--link)',
            maxWidth: '65ch',
            fontSize: '1.0625rem',
            lineHeight: '1.7',
            h1: { fontFamily: theme('fontFamily.display').join(','), fontWeight: '700', letterSpacing: '-0.01em' },
            h2: { fontFamily: theme('fontFamily.display').join(','), fontWeight: '700' },
            h3: { fontFamily: theme('fontFamily.display').join(','), fontWeight: '700' },
            a: { textUnderlineOffset: '3px', fontWeight: '600' },
            blockquote: { fontFamily: theme('fontFamily.display').join(','), fontStyle: 'normal', fontSize: '1.25em' },
          },
        },
      }),
    },
  },
  plugins: [require('@tailwindcss/forms')({ strategy: 'class' }), require('@tailwindcss/typography')],
};

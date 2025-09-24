module.exports = {
  plugins: {
    'postcss-import': {},
    'postcss-nested': {},
    'tailwindcss/nesting': {},
    'tailwindcss': {},
    'autoprefixer': {},
    'postcss-preset-env': {
      features: {
        'nesting-rules': false,
      },
    },
    ...(process.env.NODE_ENV === 'production' ? {
      '@fullhuman/postcss-purgecss': {
        content: [
          './templates/**/*.html',
          './static/js/**/*.js',
        ],
        defaultExtractor: content => content.match(/[\w-/:]+(?<!:)/g) || [],
        safelist: {
          standard: [/^html/, /^body/, /^:root/, /dark-theme/, /^h[1-6]/, /^a/, /^p/, /^ul/, /^ol/, /^li/],
          deep: [/dark/, /show/, /hide/, /open/, /active/, /disabled/],
          greedy: [/fade/, /slide/, /animate/]
        }
      },
      'cssnano': {
        preset: ['default', {
          discardComments: {
            removeAll: true,
          },
          normalizeWhitespace: false,
        }],
      }
    } : {})
  }
}

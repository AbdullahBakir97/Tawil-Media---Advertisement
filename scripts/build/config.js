const path = require('path');

const isProd = process.env.NODE_ENV === 'production';

module.exports = {
    // Common configuration
    isProd,
    rootDir: path.resolve(__dirname, '../..'),
    
    // CSS Configuration
    css: {
        srcDir: path.resolve(__dirname, '../../static/css'),
        destDir: path.resolve(__dirname, '../../static/dist/css'),
        entry: 'index.css',
        purge: {
            content: [
                '../../templates/**/*.html',
                '../../static/js/**/*.js'
            ]
        },
        minify: isProd,
        sourcemap: !isProd,
        plugins: {
            tailwind: true,
            autoprefixer: true,
            cssnano: isProd
        }
    },
    
    // JavaScript Configuration
    js: {
        srcDir: path.resolve(__dirname, '../../static/js'),
        destDir: path.resolve(__dirname, '../../static/dist/js'),
        bundles: {
            // Core bundle - always loaded
            core: {
                entry: 'core/index.js',
                include: [
                    'core/utils.js',
                    'core/state.js',
                    'core/htmx-conf.js'
                ]
            },
            // Components bundle
            components: {
                entry: 'components/index.js',
                include: [
                    'components/search.js',
                    'components/infinite-scroll.js',
                    'components/lazy-load.js'
                ]
            },
            // Analytics bundle - only in production
            analytics: {
                entry: 'analytics/index.js',
                include: [
                    'analytics/tracking.js',
                    'analytics/performance.js'
                ],
                condition: 'production'
            },
            // Main app bundle
            app: {
                entry: 'app.js'
            }
        },
        minify: isProd,
        sourcemap: !isProd,
        target: ['es2020', 'chrome58', 'firefox57', 'safari11'],
        format: 'esm',
        splitting: true,
        // External dependencies that should not be bundled
        external: [
            'htmx.org',
            'alpinejs'
        ]
    }
};

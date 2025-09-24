const postcss = require('postcss');
const cssnano = require('cssnano');
const autoprefixer = require('autoprefixer');
const tailwindcss = require('tailwindcss');
const postcssImport = require('postcss-import');
const postcssNested = require('postcss-nested');
const postcssScss = require('postcss-scss');
const postcssPurgecss = require('@fullhuman/postcss-purgecss');
const postcssPresetEnv = require('postcss-preset-env');
const fs = require('fs').promises;
const path = require('path');
const glob = require('glob');
const config = require('./config');

// Initialize PostCSS plugins
function initPlugins() {
    const plugins = [postcssImport];

    // Add postcss-nested for better CSS organization
    plugins.push(postcssNested);

    // Remove postcssScss from plugins - it should only be used as a syntax/parser
    // plugins.push(postcssScss);

    // Add postcss-preset-env for future CSS features
    plugins.push(postcssPresetEnv({
        features: {
            'nesting-rules': true,
            'custom-properties': true,
            'custom-media-queries': true
        }
    }));

    // Add Tailwind if enabled
    if (config.css.plugins.tailwind) {
        plugins.push(tailwindcss);
    }

    // Add autoprefixer if enabled
    if (config.css.plugins.autoprefixer) {
        plugins.push(autoprefixer({ grid: 'autoplace' }));
    }

    // Add PurgeCSS in production to remove unused CSS
    if (config.css.plugins.purgecss && config.isProd) {
        plugins.push(
            postcssPurgecss({
                content: [
                    './templates/**/*.html',
                    './static/js/**/*.js'
                ],
                defaultExtractor: content => content.match(/[\w-/:]+(?<!:)/g) || [],
                safelist: {
                    standard: [/^html/, /^body/, /^:root/],
                    deep: [/dark/, /light/, /active/, /open/, /show/],
                    greedy: [/^modal-/, /^dropdown-/, /^nav-/]
                }
            })
        );
    }

    // Add minification in production
    if (config.css.plugins.cssnano) {
        plugins.push(cssnano({
            preset: ['default', {
                discardComments: { removeAll: true },
                normalizeWhitespace: true
            }]
        }));
    }

    return plugins;
}

// Process a single CSS/SCSS file
async function processFile(file, plugins) {
    const css = await fs.readFile(file, 'utf8');
    const relativePath = path.relative(config.css.srcDir, file);
    
    // Change extension from .scss to .css for output
    const destPath = path.join(
        config.css.destDir, 
        relativePath.replace(/\.scss$/, '.css')
    );

    try {
        // Process with PostCSS
        const result = await postcss(plugins).process(css, {
            from: file,
            to: destPath,
            map: config.css.sourcemap ? { inline: true } : false,
            syntax: file.endsWith('.scss') ? postcssScss : undefined
        });

        // Ensure destination subdirectories exist
        await fs.mkdir(path.dirname(destPath), { recursive: true });

        // Write processed CSS
        await fs.writeFile(destPath, result.css);
        if (result.map) {
            await fs.writeFile(destPath + '.map', result.map.toString());
        }
        
        return { success: true, path: relativePath };
    } catch (error) {
        return { 
            success: false, 
            path: relativePath,
            error: `Error processing ${relativePath}: ${error.message}`
        };
    }
}

// Main build function
async function buildCSS() {
    console.log('🚀 Starting CSS build...');
    console.time('CSS Build Time');

    try {
        // Initialize plugins
        const plugins = initPlugins();
        
        // Ensure destination directory exists
        await fs.mkdir(config.css.destDir, { recursive: true });

        // Get all CSS and SCSS files
        const files = glob.sync(`${config.css.srcDir}/**/*.{css,scss}`);
        
        // Process files in parallel, but ensure entry file is first
        const entryFile = path.join(config.css.srcDir, config.css.entry);
        const entryResult = await processFile(entryFile, plugins);
        
        if (!entryResult.success) {
            throw new Error(`Entry file failed: ${entryResult.error}`);
        }
        
        console.log(`✓ Built entry file: ${config.css.entry}`);

        // Process remaining files in parallel
        const otherFiles = files.filter(f => f !== entryFile);
        const results = await Promise.all(
            otherFiles.map(file => processFile(file, plugins))
        );

        // Check for any failures
        const failures = results.filter(r => !r.success);
        if (failures.length > 0) {
            throw new Error(
                'Some files failed to process:\n' + 
                failures.map(f => f.error).join('\n')
            );
        }

        const processedFiles = [entryResult, ...results].filter(r => r.success);

        // Output build summary
        console.timeEnd('CSS Build Time');
        console.log('\nBuild Summary:');
        console.log('-------------');
        console.log(`Total files processed: ${processedFiles.length}`);
        console.log(`Output directory: ${path.relative(process.cwd(), config.css.destDir)}`);
        console.log(`Mode: ${config.isProd ? 'production' : 'development'}`);
        console.log(`Sourcemaps: ${config.css.sourcemap ? 'enabled' : 'disabled'}`);
        console.log(`Minification: ${config.css.plugins.cssnano ? 'enabled' : 'disabled'}`);
        console.log(`Plugins enabled: ${Object.entries(config.css.plugins)
            .filter(([, enabled]) => enabled)
            .map(([name]) => name)
            .join(', ')}`);

        return true;
    } catch (error) {
        console.error('\n❌ CSS build failed:', error);
        process.exit(1);
    }
}

// Watch mode
async function watch() {
    const chokidar = require('chokidar');
    
    console.log('👀 Watching for CSS/SCSS changes...');
    
    const watcher = chokidar.watch(`${config.css.srcDir}/**/*.{css,scss}`, {
        ignored: /(^|[\/\\])\../,
        persistent: true
    });

    watcher
        .on('change', async path => {
            console.log(`\nFile ${path} has been changed`);
            await buildCSS();
            console.log('\nWaiting for changes...');
        })
        .on('error', error => console.error(`Watcher error: ${error}`));
}

// Run build or watch based on arguments
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.includes('--watch')) {
        watch();
    } else {
        buildCSS();
    }
}

module.exports = {
    build: buildCSS,
    watch
};

const esbuild = require('esbuild');
const glob = require('glob');
const path = require('path');
const fs = require('fs').promises;
const config = require('./config');

// Create index files for bundles
async function createBundleIndexFiles() {
    for (const [name, bundle] of Object.entries(config.js.bundles)) {
        if (bundle.include) {
            const indexContent = bundle.include
                .map(file => `export * from '../${file}';`)
                .join('\n');
            
            const indexPath = path.join(config.js.srcDir, bundle.entry);
            await fs.mkdir(path.dirname(indexPath), { recursive: true });
            await fs.writeFile(indexPath, indexContent);
        }
    }
}

// Initialize esbuild configuration
function initBuildOptions() {
    // Get entry points from bundles
    const entryPoints = [];
    const mode = config.isProd ? 'production' : 'development';
    
    // Add bundles based on conditions
    Object.entries(config.js.bundles).forEach(([name, bundle]) => {
        if (!bundle.condition || bundle.condition === mode) {
            entryPoints.push(path.join(config.js.srcDir, bundle.entry));
        }
    });

    return {
        entryPoints,
        bundle: true,
        outdir: config.js.destDir,
        sourcemap: config.js.sourcemap,
        minify: config.js.minify,
        target: config.js.target || ['es2018'],
        format: config.js.format || 'esm',
        splitting: config.js.splitting,
        external: config.js.external || [],
        loader: {
            '.js': 'jsx',
            '.ts': 'tsx',
            '.svg': 'dataurl',
            '.png': 'dataurl',
            '.jpg': 'dataurl',
            '.gif': 'dataurl'
        },
        define: {
            'process.env.NODE_ENV': JSON.stringify(mode)
        },
        plugins: []
    };
}

// Main build function
async function buildJS() {
    try {
        console.log('🚀 Starting JavaScript build...');
        console.time('JS Build Time');

        // Create bundle index files
        await createBundleIndexFiles();

        const buildOptions = initBuildOptions();
        
        // Build with esbuild
        const result = await esbuild.build(buildOptions);

        // Output build summary
        console.timeEnd('JS Build Time');
        console.log('\nBuild Summary:');
        console.log('-------------');
        console.log(`Entry points: ${buildOptions.entryPoints.length}`);
        console.log(`Output directory: ${path.relative(process.cwd(), config.js.destDir)}`);
        console.log(`Mode: ${config.isProd ? 'production' : 'development'}`);
        console.log(`Format: ${buildOptions.format}`);
        console.log(`Target: ${buildOptions.target.join(', ')}`);
        console.log(`Sourcemaps: ${config.js.sourcemap ? 'enabled' : 'disabled'}`);
        console.log(`Minification: ${config.js.minify ? 'enabled' : 'disabled'}`);
        console.log(`Code splitting: ${config.js.splitting ? 'enabled' : 'disabled'}`);
        console.log('\nBundles:');
        Object.entries(config.js.bundles).forEach(([name, bundle]) => {
            const status = bundle.condition ? 
                `(${bundle.condition} only)` : 
                '(always included)';
            console.log(`- ${name}: ${bundle.entry} ${status}`);
        });

        if (result.errors.length > 0) {
            console.error('\nBuild Errors:', result.errors);
            process.exit(1);
        }

        if (result.warnings.length > 0) {
            console.warn('\nBuild Warnings:', result.warnings);
        }

        return true;
    } catch (error) {
        console.error('\n❌ JavaScript build failed:', error);
        process.exit(1);
    }
}

// Watch mode
async function watch() {
    try {
        console.log('👀 Watching for JavaScript changes...');

        // Create initial bundle index files
        await createBundleIndexFiles();

        const buildOptions = initBuildOptions();
        
        // Start esbuild watch mode
        const ctx = await esbuild.context({
            ...buildOptions,
            plugins: [
                {
                    name: 'watch-plugin',
                    setup(build) {
                        build.onEnd(result => {
                            if (result.errors.length > 0) {
                                console.error('\nWatch build failed:', result.errors);
                            } else {
                                console.log('\n✓ Build succeeded');
                                if (result.warnings.length > 0) {
                                    console.warn('Warnings:', result.warnings);
                                }
                            }
                        });
                    },
                },
            ],
        });

        await ctx.watch();
        console.log('\nWaiting for changes...');
    } catch (error) {
        console.error('Watch mode failed:', error);
        process.exit(1);
    }
}

// Run build or watch based on arguments
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.includes('--watch')) {
        watch();
    } else {
        buildJS();
    }
}

module.exports = {
    build: buildJS,
    watch
};

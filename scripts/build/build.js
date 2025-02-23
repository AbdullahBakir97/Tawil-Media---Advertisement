const { build: buildCSS, watch: watchCSS } = require('./css');
const { build: buildJS, watch: watchJS } = require('./js');

async function build() {
    console.log('🏗️  Starting full build process...\n');
    console.time('Total Build Time');

    try {
        // Run CSS and JS builds in parallel
        await Promise.all([
            buildCSS().catch(error => {
                console.error('CSS build failed:', error);
                throw error;
            }),
            buildJS().catch(error => {
                console.error('JS build failed:', error);
                throw error;
            })
        ]);

        console.timeEnd('Total Build Time');
        console.log('\n✨ Build completed successfully!\n');
    } catch (error) {
        console.error('\n❌ Build failed:', error);
        process.exit(1);
    }
}

async function watch() {
    console.log('🏗️  Starting watch mode...\n');

    try {
        // Start CSS and JS watchers
        await Promise.all([
            watchCSS(),
            watchJS()
        ]);

        console.log('\n👀 Watching for changes in both CSS and JS files...');
    } catch (error) {
        console.error('\n❌ Watch mode failed:', error);
        process.exit(1);
    }
}

// Run build or watch based on arguments
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.includes('--watch')) {
        watch();
    } else {
        build();
    }
}

module.exports = {
    build,
    watch
};

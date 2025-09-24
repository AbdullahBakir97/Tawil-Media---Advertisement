const { build: buildCSS, watch: watchCSS } = require('./css');
const { build: buildJS, watch: watchJS } = require('./js');
const { build: buildDesignSystem, watch: watchDesignSystem } = require('./design-system');

async function build() {
    console.log('🏗️  Starting full build process...\n');
    console.time('Total Build Time');

    try {
        // Run CSS, JS, and Design System builds in parallel
        await Promise.all([
            buildCSS().catch(error => {
                console.error('CSS build failed:', error);
                throw error;
            }),
            buildJS().catch(error => {
                console.error('JS build failed:', error);
                throw error;
            }),
            buildDesignSystem().catch(error => {
                console.error('Design System build failed:', error);
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
        // Start CSS, JS, and Design System watchers
        await Promise.all([
            watchCSS(),
            watchJS(),
            watchDesignSystem()
        ]);

        console.log('\n👀 Watching for changes in both CSS, JS, and Design System files...');
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

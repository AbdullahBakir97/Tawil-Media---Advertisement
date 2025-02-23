const path = require('path');
const fs = require('fs').promises;
const glob = require('glob');
const zlib = require('zlib');
const { promisify } = require('util');
const gzip = promisify(zlib.gzip);
const brotli = promisify(zlib.brotliCompress);

// Configuration
const config = {
    srcDir: path.resolve(__dirname, '../../static/dist'),
    compressExtensions: ['.js', '.css', '.html', '.svg', '.json'],
    hashLength: 8,
    manifest: 'asset-manifest.json'
};

async function optimizeAssets() {
    try {
        const manifest = {};
        const files = glob.sync(`${config.srcDir}/**/*.*`);

        for (const file of files) {
            const ext = path.extname(file);
            const relativePath = path.relative(config.srcDir, file);
            
            // Read file content
            const content = await fs.readFile(file);
            
            // Generate content hash
            const hash = require('crypto')
                .createHash('md5')
                .update(content)
                .digest('hex')
                .slice(0, config.hashLength);

            // Create hashed filename
            const parsedPath = path.parse(file);
            const hashedName = `${parsedPath.name}-${hash}${parsedPath.ext}`;
            const hashedPath = path.join(parsedPath.dir, hashedName);

            // Copy file with hashed name
            await fs.copyFile(file, hashedPath);

            // Compress if needed
            if (config.compressExtensions.includes(ext)) {
                // Gzip compression
                const gzipped = await gzip(content, { level: 9 });
                await fs.writeFile(`${hashedPath}.gz`, gzipped);

                // Brotli compression
                const brotlied = await brotli(content, {
                    params: {
                        [zlib.constants.BROTLI_PARAM_QUALITY]: 11
                    }
                });
                await fs.writeFile(`${hashedPath}.br`, brotlied);

                // Add compression info to manifest
                manifest[relativePath] = {
                    hashed: path.relative(config.srcDir, hashedPath),
                    size: content.length,
                    gzip: gzipped.length,
                    brotli: brotlied.length
                };
            } else {
                manifest[relativePath] = {
                    hashed: path.relative(config.srcDir, hashedPath),
                    size: content.length
                };
            }

            console.log(`Processed: ${relativePath}`);
        }

        // Write manifest
        const manifestPath = path.join(config.srcDir, config.manifest);
        await fs.writeFile(
            manifestPath,
            JSON.stringify(manifest, null, 2)
        );

        console.log('Asset optimization completed successfully!');
        console.log(`Manifest written to: ${config.manifest}`);

        // Output statistics
        const stats = {
            totalFiles: Object.keys(manifest).length,
            totalSize: Object.values(manifest)
                .reduce((sum, asset) => sum + asset.size, 0),
            compressedFiles: Object.values(manifest)
                .filter(asset => 'gzip' in asset).length
        };
        console.log('Optimization stats:', stats);

    } catch (error) {
        console.error('Asset optimization failed:', error);
        process.exit(1);
    }
}

// Helper function to clean dist directory
async function cleanDist() {
    try {
        await fs.rm(config.srcDir, { recursive: true, force: true });
        await fs.mkdir(config.srcDir, { recursive: true });
        console.log('Cleaned dist directory');
    } catch (error) {
        console.error('Clean failed:', error);
        process.exit(1);
    }
}

// Run optimization if called directly
if (require.main === module) {
    const args = process.argv.slice(2);
    
    Promise.resolve()
        .then(() => args.includes('--clean') ? cleanDist() : null)
        .then(() => optimizeAssets())
        .catch(error => {
            console.error('Optimization failed:', error);
            process.exit(1);
        });
}

module.exports = {
    optimize: optimizeAssets,
    clean: cleanDist
};

const sharp = require('sharp');
const glob = require('glob');
const path = require('path');
const fs = require('fs').promises;

// Configuration
const config = {
    srcDir: path.resolve(__dirname, '../../static/img'),
    destDir: path.resolve(__dirname, '../../static/dist/img'),
    formats: ['jpg', 'jpeg', 'png', 'webp'],
    sizes: {
        thumbnail: 150,
        small: 300,
        medium: 600,
        large: 1200
    },
    quality: {
        jpg: 80,
        jpeg: 80,
        png: 80,
        webp: 75
    }
};

async function optimizeImages() {
    try {
        // Create destination directory
        await fs.mkdir(config.destDir, { recursive: true });

        // Get all image files
        const files = glob.sync(`${config.srcDir}/**/*.{${config.formats.join(',')}}`);

        for (const file of files) {
            const relativePath = path.relative(config.srcDir, file);
            const fileName = path.parse(relativePath).name;
            const destSubDir = path.dirname(relativePath);

            // Create destination subdirectory
            const fullDestDir = path.join(config.destDir, destSubDir);
            await fs.mkdir(fullDestDir, { recursive: true });

            // Load image
            const image = sharp(file);
            const metadata = await image.metadata();

            // Process each size
            for (const [size, width] of Object.entries(config.sizes)) {
                // Skip if original is smaller
                if (metadata.width <= width) continue;

                const resized = image.clone().resize(width, null, {
                    withoutEnlargement: true,
                    fit: 'inside'
                });

                // Generate formats
                for (const format of config.formats) {
                    const outputPath = path.join(
                        fullDestDir,
                        `${fileName}-${size}.${format}`
                    );

                    await resized[format]({
                        quality: config.quality[format]
                    }).toFile(outputPath);

                    console.log(`Optimized: ${outputPath}`);
                }
            }

            // Generate WebP version of original
            const originalWebP = path.join(
                fullDestDir,
                `${fileName}.webp`
            );
            
            await image
                .webp({ quality: config.quality.webp })
                .toFile(originalWebP);

            console.log(`Created WebP: ${originalWebP}`);
        }

        console.log('Image optimization completed successfully!');
    } catch (error) {
        console.error('Image optimization failed:', error);
        process.exit(1);
    }
}

// Process SVG icons
async function optimizeSVGs() {
    const SVGO = require('svgo');
    const svgo = new SVGO({
        plugins: [
            { removeViewBox: false },
            { removeDimensions: true },
            { cleanupIDs: true }
        ]
    });

    const svgFiles = glob.sync(`${config.srcDir}/icons/**/*.svg`);

    for (const file of svgFiles) {
        const svg = await fs.readFile(file, 'utf8');
        const optimized = await svgo.optimize(svg);
        
        const relativePath = path.relative(config.srcDir, file);
        const destPath = path.join(config.destDir, relativePath);
        
        await fs.mkdir(path.dirname(destPath), { recursive: true });
        await fs.writeFile(destPath, optimized.data);
        
        console.log(`Optimized SVG: ${relativePath}`);
    }
}

// Run optimization if called directly
if (require.main === module) {
    Promise.all([
        optimizeImages(),
        optimizeSVGs()
    ]).catch(error => {
        console.error('Optimization failed:', error);
        process.exit(1);
    });
}

module.exports = {
    optimizeImages,
    optimizeSVGs
};

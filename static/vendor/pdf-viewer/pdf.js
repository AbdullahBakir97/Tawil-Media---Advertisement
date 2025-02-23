/**
 * PDF.js wrapper for Tawil Media platform
 * This file provides a simplified interface to PDF.js functionality
 */

class PDFDocument {
    constructor(options = {}) {
        this.url = options.url;
        this.worker = options.worker || 'pdf.worker.js';
        this.cMapUrl = options.cMapUrl || 'cmaps/';
        this.cMapPacked = options.cMapPacked || true;
        
        // Initialize PDF.js
        pdfjsLib.GlobalWorkerOptions.workerSrc = this.worker;
    }
    
    async load() {
        try {
            const loadingTask = pdfjsLib.getDocument({
                url: this.url,
                cMapUrl: this.cMapUrl,
                cMapPacked: this.cMapPacked
            });
            
            this.pdf = await loadingTask.promise;
            return this.pdf;
        } catch (error) {
            console.error('Error loading PDF:', error);
            throw error;
        }
    }
    
    async getPage(pageNumber) {
        try {
            return await this.pdf.getPage(pageNumber);
        } catch (error) {
            console.error(`Error getting page ${pageNumber}:`, error);
            throw error;
        }
    }
    
    async renderPage(page, canvas, scale = 1.0) {
        const viewport = page.getViewport({ scale });
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        
        const renderContext = {
            canvasContext: canvas.getContext('2d'),
            viewport: viewport
        };
        
        try {
            await page.render(renderContext).promise;
        } catch (error) {
            console.error('Error rendering page:', error);
            throw error;
        }
    }
    
    async getPageAsImage(pageNumber, scale = 1.0) {
        const page = await this.getPage(pageNumber);
        const viewport = page.getViewport({ scale });
        
        const canvas = document.createElement('canvas');
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        
        await this.renderPage(page, canvas, scale);
        
        return {
            dataUrl: canvas.toDataURL('image/jpeg'),
            width: viewport.width,
            height: viewport.height
        };
    }
    
    async getOutline() {
        try {
            return await this.pdf.getOutline();
        } catch (error) {
            console.error('Error getting outline:', error);
            return null;
        }
    }
    
    async getMetadata() {
        try {
            return await this.pdf.getMetadata();
        } catch (error) {
            console.error('Error getting metadata:', error);
            return null;
        }
    }
    
    async getAttachments() {
        try {
            return await this.pdf.getAttachments();
        } catch (error) {
            console.error('Error getting attachments:', error);
            return null;
        }
    }
    
    async getDestination(dest) {
        try {
            return await this.pdf.getDestination(dest);
        } catch (error) {
            console.error('Error getting destination:', error);
            return null;
        }
    }
    
    destroy() {
        if (this.pdf) {
            this.pdf.destroy();
        }
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PDFDocument;
}

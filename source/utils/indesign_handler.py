import os
import asyncio
import subprocess
from pathlib import Path
from django.conf import settings
from django.core.files.storage import default_storage
import logging
import json
from PIL import Image
import io
from source.apps.archives.models import Edition, EditionContent, ArchiveMetadata
from django.utils import timezone

logger = logging.getLogger(__name__)

class InDesignHandler:
    def __init__(self):
        self.temp_dir = settings.MEDIA_ROOT / 'temp' / 'indesign'
        self.output_dir = settings.MEDIA_ROOT / 'magazines'
        self.archive_dir = settings.MEDIA_ROOT / 'archives'
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure all necessary directories exist."""
        for directory in [self.temp_dir, self.output_dir, self.archive_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    async def process_edition_file(self, file_path, edition_id):
        """Process InDesign file for an edition and create all necessary assets."""
        try:
            edition = Edition.objects.get(id=edition_id)
            work_dir = self.temp_dir / str(edition_id)
            work_dir.mkdir(exist_ok=True)

            # Export to PDF
            pdf_path = await self.export_to_pdf(file_path, work_dir)
            
            # Generate assets and create content entries
            results = await self.generate_edition_assets(pdf_path, edition)
            
            # Update edition metadata
            self.update_edition_metadata(edition, results)
            
            # Clean up
            self.cleanup(work_dir)
            
            return results

        except Exception as e:
            logger.error(f"Error processing edition file: {e}")
            raise

    async def export_to_pdf(self, indesign_path, work_dir):
        """Export InDesign file to PDF using InDesign Server."""
        try:
            server_url = settings.INDESIGN_SERVER_URL
            
            export_settings = {
                "format": "PDF",
                "quality": "HIGH",
                "spreads": True,
                "optimization": {
                    "compression": "lossless",
                    "colorSpace": "RGB",
                    "resolution": 300
                },
                "metadata": {
                    "preserveMetadata": True,
                    "preserveStructure": True
                }
            }

            pdf_path = work_dir / "edition.pdf"
            
            process = await asyncio.create_subprocess_exec(
                'indesign-server',
                '--convert',
                str(indesign_path),
                '--output',
                str(pdf_path),
                '--settings',
                json.dumps(export_settings)
            )
            await process.wait()

            if not pdf_path.exists():
                raise Exception("PDF export failed")

            return pdf_path

        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}")
            raise

    async def generate_edition_assets(self, pdf_path, edition):
        """Generate all necessary assets for an edition."""
        results = {
            'pages': [],
            'contents': [],
            'metadata': {}
        }

        try:
            pages_dir = self.archive_dir / str(edition.archive_year.year) / str(edition.edition_number) / 'pages'
            pages_dir.mkdir(parents=True, exist_ok=True)

            # Convert PDF pages
            from pdf2image import convert_from_path
            pages = convert_from_path(
                pdf_path,
                dpi=300,
                fmt='png',
                thread_count=4
            )

            # Process each page
            for idx, page in enumerate(pages):
                page_num = idx + 1
                
                # Save high-quality page
                page_path = pages_dir / f'page_{page_num}.png'
                page.save(str(page_path), 'PNG', quality=95)
                
                # Generate thumbnail
                thumb = self.create_thumbnail(page)
                thumb_path = pages_dir / f'thumb_{page_num}.jpg'
                thumb.save(str(thumb_path), 'JPEG', quality=85)
                
                # Generate mobile version
                mobile = self.create_mobile_version(page)
                mobile_path = pages_dir / f'mobile_{page_num}.jpg'
                mobile.save(str(mobile_path), 'JPEG', quality=90)
                
                # Create EditionContent entry
                content = EditionContent.objects.create(
                    edition=edition,
                    page_number=page_num,
                    title=f"Page {page_num}",
                    content_type='article',
                    digital_content=str(page_path),
                    is_searchable=True
                )
                
                # Create metadata
                ArchiveMetadata.objects.create(
                    edition_content=content,
                    digitization_date=timezone.now().date(),
                    digitization_notes="Automatically processed from InDesign file",
                    preservation_status='excellent'
                )
                
                results['pages'].append({
                    'number': page_num,
                    'high_res': str(page_path),
                    'thumbnail': str(thumb_path),
                    'mobile': str(mobile_path),
                    'content_id': content.id
                })

            # Generate edition preview
            preview = self.create_preview(pages[0])
            preview_path = self.archive_dir / str(edition.archive_year.year) / str(edition.edition_number) / 'preview.jpg'
            preview.save(str(preview_path), 'JPEG', quality=90)
            results['preview'] = str(preview_path)

            # Generate optimized PDFs
            web_pdf = await self.optimize_pdf_for_web(pdf_path, edition)
            mobile_pdf = await self.optimize_pdf_for_mobile(pdf_path, edition)
            
            results['pdfs'] = {
                'web': str(web_pdf),
                'mobile': str(mobile_pdf)
            }

            return results

        except Exception as e:
            logger.error(f"Error generating edition assets: {e}")
            raise

    def update_edition_metadata(self, edition, results):
        """Update edition metadata with processing results."""
        try:
            edition.is_digitized = True
            edition.page_count = len(results['pages'])
            
            # Calculate total file size
            total_size = 0
            for page in results['pages']:
                total_size += os.path.getsize(page['high_res'])
            edition.file_size = total_size
            
            # Set cover image if not already set
            if not edition.cover_image and results['pages']:
                from source.apps.content.models import Media
                cover_media = Media.objects.create(
                    file=results['preview'],
                    media_type='image',
                    alt_text=f"Cover of {edition.title}"
                )
                edition.cover_image = cover_media
            
            edition.save()

        except Exception as e:
            logger.error(f"Error updating edition metadata: {e}")
            raise

    def create_thumbnail(self, image):
        """Create thumbnail version of a page."""
        thumbnail_size = (200, 283)  # Maintain aspect ratio
        thumbnail = image.copy()
        thumbnail.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
        return thumbnail

    def create_mobile_version(self, image):
        """Create mobile-optimized version of a page."""
        mobile_size = (828, 1170)  # Optimized for mobile devices
        mobile = image.copy()
        mobile.thumbnail(mobile_size, Image.Resampling.LANCZOS)
        return mobile

    def create_preview(self, image):
        """Create preview image for edition listing."""
        preview_size = (600, 848)
        preview = image.copy()
        preview.thumbnail(preview_size, Image.Resampling.LANCZOS)
        return preview

    async def optimize_pdf_for_web(self, pdf_path, edition):
        """Optimize PDF for web viewing."""
        output_path = self.archive_dir / str(edition.archive_year.year) / str(edition.edition_number) / 'web.pdf'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        process = await asyncio.create_subprocess_exec(
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/ebook',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={output_path}',
            str(pdf_path)
        )
        await process.wait()
        
        return output_path

    async def optimize_pdf_for_mobile(self, pdf_path, edition):
        """Optimize PDF for mobile devices."""
        output_path = self.archive_dir / str(edition.archive_year.year) / str(edition.edition_number) / 'mobile.pdf'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        process = await asyncio.create_subprocess_exec(
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/screen',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={output_path}',
            str(pdf_path)
        )
        await process.wait()
        
        return output_path

    def cleanup(self, work_dir):
        """Clean up temporary files."""
        try:
            import shutil
            shutil.rmtree(work_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {e}")

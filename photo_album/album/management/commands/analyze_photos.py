"""
Management command to process photos with AI analysis.
"""
import time
import os
from django.core.management.base import BaseCommand
from django.db.models import Q
from album.models import Photo
from album.services.ai_analysis_service import analyze_image, is_ai_analysis_available

class Command(BaseCommand):
    help = 'Analyzes photos with AI to generate descriptions and tags.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of AI analysis for all photos, even those that already have descriptions.',
        )
        parser.add_argument(
            '--album',
            type=str,
            help='Process only photos from a specific album (by title).',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of photos to process.',
        )

    def handle(self, *args, **options):
        force_regeneration = options['force']
        album_title = options.get('album')
        limit = options.get('limit')
        
        # Check if AI analysis is available
        if not is_ai_analysis_available():
            self.stdout.write(self.style.ERROR('AI analysis service is not available. Please check the model loading.'))
            return
        
        # Build queryset
        if force_regeneration:
            self.stdout.write(self.style.WARNING('Forcing regeneration for all photos.'))
            if album_title:
                photos_to_process = Photo.objects.filter(album__title=album_title)
            else:
                photos_to_process = Photo.objects.all()
        else:
            self.stdout.write('Processing photos that do not have AI descriptions...')
            filters = Q(ai_description__isnull=True) | Q(ai_description='')
            if album_title:
                filters &= Q(album__title=album_title)
            photos_to_process = Photo.objects.filter(filters)

        # Apply album filter if specified
        if album_title and not force_regeneration:
            photos_to_process = photos_to_process.filter(album__title=album_title)
            self.stdout.write(f'Filtering by album: {album_title}')

        # Apply limit if specified
        if limit:
            photos_to_process = photos_to_process[:limit]
            self.stdout.write(f'Limiting to {limit} photos')

        total_photos = photos_to_process.count()
        if total_photos == 0:
            self.stdout.write(self.style.SUCCESS('No photos to process.'))
            return

        self.stdout.write(f'Found {total_photos} photos to process.')
        
        start_time = time.time()
        processed_count = 0
        error_count = 0
        
        for photo in photos_to_process:
            if not photo.image or not hasattr(photo.image, 'path'):
                self.stdout.write(self.style.WARNING(f'Skipping photo {photo.pk} because it has no image file path.'))
                error_count += 1
                continue
            
            # Check if file exists
            if not os.path.exists(photo.image.path):
                self.stdout.write(self.style.WARNING(f'Skipping photo {photo.pk} because image file does not exist: {photo.image.path}'))
                error_count += 1
                continue
            
            try:
                self.stdout.write(f'Processing: {photo.title} ({photo.pk})')
                
                # Analyze the image
                analysis_result = analyze_image(photo.image.path)
                
                if analysis_result['description']:
                    # Update the photo with AI analysis results
                    Photo.objects.filter(pk=photo.pk).update(
                        ai_description=analysis_result['description'],
                        ai_tags=analysis_result['tags'],
                        ai_confidence_score=analysis_result['confidence'],
                        ai_processed=True
                    )
                    
                    processed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ {photo.title}: "{analysis_result["description"]}" '
                            f'(tags: {", ".join(analysis_result["tags"][:5])})'
                        )
                    )
                else:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'✗ Failed to analyze: {photo.title}'))
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'✗ Error processing {photo.title} ({photo.pk}): {e}'))

        end_time = time.time()
        duration = end_time - start_time
        
        self.stdout.write(self.style.SUCCESS('\n=== AI Analysis Complete ==='))
        self.stdout.write(f'Successfully processed: {processed_count} photos')
        self.stdout.write(f'Errors encountered: {error_count} photos')
        self.stdout.write(f'Total time: {duration:.2f} seconds')
        if processed_count > 0:
            self.stdout.write(f'Average time per photo: {duration/processed_count:.2f} seconds')
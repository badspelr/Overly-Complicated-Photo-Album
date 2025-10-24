"""
Management command to process videos with AI analysis using their thumbnails.
"""
import time
import os
from django.core.management.base import BaseCommand
from django.db.models import Q
from album.models import Video
from album.services.ai_analysis_service import analyze_image, is_ai_analysis_available
from album.services.embedding_service import generate_image_embedding

class Command(BaseCommand):
    help = 'Analyzes video thumbnails with AI to generate descriptions and tags for videos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of AI analysis for all videos, even those that already have descriptions.',
        )
        parser.add_argument(
            '--album',
            type=str,
            help='Process only videos from a specific album (by title).',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of videos to process.',
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
            self.stdout.write(self.style.WARNING('Forcing regeneration for all videos.'))
            if album_title:
                videos_to_process = Video.objects.filter(album__title=album_title)
            else:
                videos_to_process = Video.objects.all()
        else:
            self.stdout.write('Processing videos that do not have AI descriptions...')
            filters = Q(ai_description__isnull=True) | Q(ai_description='')
            if album_title:
                filters &= Q(album__title=album_title)
            videos_to_process = Video.objects.filter(filters)

        # Apply album filter if specified
        if album_title and not force_regeneration:
            videos_to_process = videos_to_process.filter(album__title=album_title)
            self.stdout.write(f'Filtering by album: {album_title}')

        # Apply limit if specified
        if limit:
            videos_to_process = videos_to_process[:limit]
            self.stdout.write(f'Limiting to {limit} videos')

        total_videos = videos_to_process.count()
        if total_videos == 0:
            self.stdout.write(self.style.SUCCESS('No videos to process.'))
            return

        self.stdout.write(f'Found {total_videos} videos to process.')
        
        start_time = time.time()
        processed_count = 0
        error_count = 0
        
        for video in videos_to_process:
            # Check if video has a thumbnail
            if not video.thumbnail or not hasattr(video.thumbnail, 'path'):
                self.stdout.write(self.style.WARNING(f'Skipping video {video.pk} because it has no thumbnail. Generate thumbnails first.'))
                error_count += 1
                continue
            
            # Check if thumbnail file exists
            if not os.path.exists(video.thumbnail.path):
                self.stdout.write(self.style.WARNING(f'Skipping video {video.pk} because thumbnail file does not exist: {video.thumbnail.path}'))
                error_count += 1
                continue
            
            try:
                self.stdout.write(f'Processing: {video.title} ({video.pk})')
                
                # Analyze the video thumbnail
                analysis_result = analyze_image(video.thumbnail.path)
                
                if analysis_result['description']:
                    # Generate embedding for the thumbnail
                    thumbnail_embedding = generate_image_embedding(video.thumbnail.path)
                    
                    # Update the video with AI analysis results
                    Video.objects.filter(pk=video.pk).update(
                        ai_description=analysis_result['description'],
                        ai_tags=analysis_result['tags'],
                        ai_confidence_score=analysis_result['confidence'],
                        ai_processed=True,
                        thumbnail_embedding=thumbnail_embedding
                    )
                    
                    processed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Processed video: {video.title} - "{analysis_result["description"][:50]}..."')
                    )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to generate description for video: {video.title}')
                    )
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing video {video.title}: {str(e)}')
                )
        
        elapsed_time = time.time() - start_time
        
        self.stdout.write(self.style.SUCCESS(
            '\\n📊 Processing complete!'
        ))
        self.stdout.write(f'✅ Successfully processed: {processed_count} videos')
        self.stdout.write(f'❌ Errors: {error_count} videos')
        self.stdout.write(f'⏱️  Total time: {elapsed_time:.2f} seconds')
        
        if processed_count > 0:
            avg_time = elapsed_time / processed_count
            self.stdout.write(f'📈 Average time per video: {avg_time:.2f} seconds')
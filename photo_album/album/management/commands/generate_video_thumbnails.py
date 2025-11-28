"""
Management command to generate thumbnails for videos that don't have them.
"""
from django.core.management.base import BaseCommand
from album.models import Video
from album.utils.media_utils import VideoThumbnailGenerator


class Command(BaseCommand):
    help = 'Generate thumbnails for videos that don\'t have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate thumbnails even if they already exist',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        if force:
            videos = Video.objects.all()
            self.stdout.write(f'Generating thumbnails for all {videos.count()} videos...')
        else:
            videos = Video.objects.filter(thumbnail='')
            self.stdout.write(f'Generating thumbnails for {videos.count()} videos without thumbnails...')
        
        success_count = 0
        error_count = 0
        
        for video in videos:
            self.stdout.write(f'Processing: {video.title}')
            
            if force and video.thumbnail:
                # Delete existing thumbnail if forcing regeneration
                video.thumbnail.delete()
            
            success = VideoThumbnailGenerator.generate_video_thumbnail(video)
            
            if success:
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Generated thumbnail for: {video.title}')
                )
            else:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to generate thumbnail for: {video.title}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Completed: {success_count} successful, {error_count} errors'
            )
        )
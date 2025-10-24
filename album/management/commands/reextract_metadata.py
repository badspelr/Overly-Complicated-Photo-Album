"""
Management command to re-extract metadata for photos and videos.
"""
from django.core.management.base import BaseCommand
from album.models import Photo, Video
from album.services.media_service import MediaService


class Command(BaseCommand):
    help = 'Re-extract metadata for photos and videos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--album',
            type=int,
            help='Album ID to process (processes all if not specified)',
        )
        parser.add_argument(
            '--photos-only',
            action='store_true',
            help='Process only photos',
        )
        parser.add_argument(
            '--videos-only',
            action='store_true',
            help='Process only videos',
        )

    def handle(self, *args, **options):
        album_id = options.get('album')
        photos_only = options.get('photos_only')
        videos_only = options.get('videos_only')

        # Process photos
        if not videos_only:
            photos = Photo.objects.all()
            if album_id:
                photos = photos.filter(album_id=album_id)
            
            photo_count = photos.count()
            self.stdout.write(f'Processing {photo_count} photos...')
            
            for i, photo in enumerate(photos, 1):
                try:
                    MediaService.extract_photo_metadata(photo)
                    if i % 100 == 0:
                        self.stdout.write(f'  Processed {i}/{photo_count} photos...')
                except Exception as e:
                    self.stderr.write(f'  Error processing photo {photo.id}: {e}')
            
            self.stdout.write(self.style.SUCCESS(f'✓ Processed {photo_count} photos'))

        # Process videos
        if not photos_only:
            videos = Video.objects.all()
            if album_id:
                videos = videos.filter(album_id=album_id)
            
            video_count = videos.count()
            self.stdout.write(f'Processing {video_count} videos...')
            
            for i, video in enumerate(videos, 1):
                try:
                    MediaService.extract_video_metadata(video)
                    if i % 100 == 0:
                        self.stdout.write(f'  Processed {i}/{video_count} videos...')
                except Exception as e:
                    self.stderr.write(f'  Error processing video {video.id}: {e}')
            
            self.stdout.write(self.style.SUCCESS(f'✓ Processed {video_count} videos'))

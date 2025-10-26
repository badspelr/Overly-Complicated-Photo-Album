"""
Management command to check AI processing status.
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from album.models import Photo, Video


class Command(BaseCommand):
    help = 'Check the status of AI processing for photos and videos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--album',
            type=str,
            help='Check only items from a specific album (by title).',
        )
        parser.add_argument(
            '--media-type',
            type=str,
            choices=['photos', 'videos', 'both'],
            default='both',
            help='Type of media to check (photos, videos, or both).',
        )

    def handle(self, *args, **options):
        album_title = options.get('album')
        media_type = options['media_type']

        # Check photos
        if media_type in ['photos', 'both']:
            self.stdout.write(self.style.SUCCESS('\n=== Photo Processing Status ==='))
            
            photo_queryset = Photo.objects.all()
            if album_title:
                photo_queryset = photo_queryset.filter(album__title=album_title)
            
            total_photos = photo_queryset.count()
            completed = photo_queryset.filter(
                processing_status=Photo.ProcessingStatus.COMPLETED
            ).count()
            processing = photo_queryset.filter(
                processing_status=Photo.ProcessingStatus.PROCESSING
            ).count()
            failed = photo_queryset.filter(
                processing_status=Photo.ProcessingStatus.FAILED
            ).count()
            pending = photo_queryset.filter(
                Q(processing_status=Photo.ProcessingStatus.PENDING) |
                Q(processing_status__isnull=True)
            ).count()
            
            # Show unprocessed (no AI description yet)
            unprocessed = photo_queryset.filter(
                Q(ai_description__isnull=True) | Q(ai_description='')
            ).count()
            
            self.stdout.write(f'Total Photos: {total_photos}')
            self.stdout.write(f'  ✓ Completed: {completed}')
            self.stdout.write(f'  ⏳ Processing: {processing}')
            self.stdout.write(f'  ⏸ Pending: {pending}')
            self.stdout.write(f'  ✗ Failed: {failed}')
            self.stdout.write(f'  📝 Unprocessed (no AI description): {unprocessed}')
            
            # Show recently failed photos
            if failed > 0:
                self.stdout.write('\nRecently Failed Photos:')
                failed_photos = photo_queryset.filter(
                    processing_status=Photo.ProcessingStatus.FAILED
                ).order_by('-modified_at')[:5]
                
                for photo in failed_photos:
                    error_msg = getattr(photo, 'ai_processing_error', 'No error message')
                    self.stdout.write(
                        self.style.ERROR(
                            f'  • {photo.title} (ID: {photo.id}): {error_msg}'
                        )
                    )
            
            # Show currently processing
            if processing > 0:
                self.stdout.write('\nCurrently Processing:')
                processing_photos = photo_queryset.filter(
                    processing_status=Photo.ProcessingStatus.PROCESSING
                ).order_by('-modified_at')[:10]
                
                for photo in processing_photos:
                    self.stdout.write(
                        self.style.WARNING(f'  • {photo.title} (ID: {photo.id})')
                    )

        # Check videos
        if media_type in ['videos', 'both']:
            self.stdout.write(self.style.SUCCESS('\n=== Video Processing Status ==='))
            
            video_queryset = Video.objects.all()
            if album_title:
                video_queryset = video_queryset.filter(album__title=album_title)
            
            total_videos = video_queryset.count()
            completed = video_queryset.filter(
                processing_status=Video.ProcessingStatus.COMPLETED
            ).count()
            processing = video_queryset.filter(
                processing_status=Video.ProcessingStatus.PROCESSING
            ).count()
            failed = video_queryset.filter(
                processing_status=Video.ProcessingStatus.FAILED
            ).count()
            pending = video_queryset.filter(
                Q(processing_status=Video.ProcessingStatus.PENDING) |
                Q(processing_status__isnull=True)
            ).count()
            
            # Show unprocessed (no AI description yet)
            unprocessed = video_queryset.filter(
                Q(ai_description__isnull=True) | Q(ai_description='')
            ).count()
            
            self.stdout.write(f'Total Videos: {total_videos}')
            self.stdout.write(f'  ✓ Completed: {completed}')
            self.stdout.write(f'  ⏳ Processing: {processing}')
            self.stdout.write(f'  ⏸ Pending: {pending}')
            self.stdout.write(f'  ✗ Failed: {failed}')
            self.stdout.write(f'  📝 Unprocessed (no AI description): {unprocessed}')
            
            # Show recently failed videos
            if failed > 0:
                self.stdout.write('\nRecently Failed Videos:')
                failed_videos = video_queryset.filter(
                    processing_status=Video.ProcessingStatus.FAILED
                ).order_by('-modified_at')[:5]
                
                for video in failed_videos:
                    error_msg = getattr(video, 'ai_processing_error', 'No error message')
                    self.stdout.write(
                        self.style.ERROR(
                            f'  • {video.title} (ID: {video.id}): {error_msg}'
                        )
                    )
            
            # Show currently processing
            if processing > 0:
                self.stdout.write('\nCurrently Processing:')
                processing_videos = video_queryset.filter(
                    processing_status=Video.ProcessingStatus.PROCESSING
                ).order_by('-modified_at')[:10]
                
                for video in processing_videos:
                    self.stdout.write(
                        self.style.WARNING(f'  • {video.title} (ID: {video.id})')
                    )
        
        self.stdout.write(self.style.SUCCESS('\n✓ Status check complete'))

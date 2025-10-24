"""
Management command to clean up orphaned Photo and Video records.
Removes database entries for media files that no longer exist on disk.
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from album.models import Photo, Video


class Command(BaseCommand):
    help = 'Remove database records for photos and videos whose files no longer exist'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(self.style.WARNING('Scanning for orphaned media records...'))
        
        # Check photos
        orphaned_photos = []
        total_photos = Photo.objects.count()
        
        self.stdout.write(f'Checking {total_photos} photos...')
        
        for photo in Photo.objects.all():
            # Check if original image exists
            if photo.image and not os.path.exists(photo.image.path):
                orphaned_photos.append(photo)
        
        # Check videos
        orphaned_videos = []
        total_videos = Video.objects.count()
        
        self.stdout.write(f'Checking {total_videos} videos...')
        
        for video in Video.objects.all():
            # Check if original video exists
            if video.video and not os.path.exists(video.video.path):
                orphaned_videos.append(video)
        
        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.WARNING('ORPHANED RECORDS FOUND:'))
        self.stdout.write('='*70)
        self.stdout.write(f'Photos: {len(orphaned_photos)} orphaned out of {total_photos} total')
        self.stdout.write(f'Videos: {len(orphaned_videos)} orphaned out of {total_videos} total')
        self.stdout.write('='*70 + '\n')
        
        if not orphaned_photos and not orphaned_videos:
            self.stdout.write(self.style.SUCCESS('✓ No orphaned records found! Database is clean.'))
            return
        
        # Show sample of what will be deleted
        if orphaned_photos:
            self.stdout.write(self.style.WARNING('\nOrphaned Photos (sample):'))
            for photo in orphaned_photos[:10]:
                album_info = f' (Album: {photo.album.title})' if photo.album else ''
                self.stdout.write(f'  - {photo.image.name}{album_info}')
            if len(orphaned_photos) > 10:
                self.stdout.write(f'  ... and {len(orphaned_photos) - 10} more')
        
        if orphaned_videos:
            self.stdout.write(self.style.WARNING('\nOrphaned Videos (sample):'))
            for video in orphaned_videos[:10]:
                album_info = f' (Album: {video.album.title})' if video.album else ''
                self.stdout.write(f'  - {video.video.name}{album_info}')
            if len(orphaned_videos) > 10:
                self.stdout.write(f'  ... and {len(orphaned_videos) - 10} more')
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS('\n✓ Dry run complete. No records were deleted.'))
            self.stdout.write('Run without --dry-run to actually delete these records.')
            return
        
        # Confirm deletion
        if not force:
            self.stdout.write(self.style.WARNING('\n⚠️  WARNING: This will permanently delete these database records!'))
            confirm = input('Are you sure you want to continue? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Aborted.'))
                return
        
        # Delete orphaned records
        deleted_photos = 0
        deleted_videos = 0
        
        if orphaned_photos:
            self.stdout.write('\nDeleting orphaned photos...')
            for photo in orphaned_photos:
                photo.delete()
                deleted_photos += 1
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {deleted_photos} orphaned photo records'))
        
        if orphaned_videos:
            self.stdout.write('\nDeleting orphaned videos...')
            for video in orphaned_videos:
                video.delete()
                deleted_videos += 1
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {deleted_videos} orphaned video records'))
        
        # Final summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('CLEANUP COMPLETE'))
        self.stdout.write('='*70)
        self.stdout.write(f'Photos deleted: {deleted_photos}')
        self.stdout.write(f'Videos deleted: {deleted_videos}')
        self.stdout.write(f'Total deleted: {deleted_photos + deleted_videos}')
        self.stdout.write('='*70)
        
        self.stdout.write(self.style.SUCCESS('\n✓ Database cleaned successfully!'))

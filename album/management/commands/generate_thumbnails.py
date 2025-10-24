"""
Django management command to pre-generate thumbnails for photos.
"""
from django.core.management.base import BaseCommand, CommandError
from album.models import Photo
import os


class Command(BaseCommand):
    help = 'Pre-generate thumbnails for photos to improve performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--album-id',
            type=int,
            help='Album ID to generate thumbnails for specific album'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of photos to process at once (default: 10)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of existing thumbnails'
        )

    def handle(self, *args, **options):
        album_id = options.get('album_id')
        batch_size = options.get('batch_size')
        force = options.get('force')

        # Get photos to process
        if album_id:
            try:
                photos = Photo.objects.filter(album_id=album_id)
                album_name = photos.first().album.title if photos.exists() else f"Album {album_id}"
                self.stdout.write(f'Processing photos for album: {album_name}')
            except Photo.DoesNotExist:
                raise CommandError(f'No photos found for album ID {album_id}')
        else:
            photos = Photo.objects.all()
            self.stdout.write('Processing all photos in the database')

        total_photos = photos.count()
        if total_photos == 0:
            self.stdout.write(self.style.WARNING('No photos found to process'))
            return

        self.stdout.write(f'Found {total_photos} photos to process')

        processed = 0
        errors = 0

        # Process photos in batches
        for i in range(0, total_photos, batch_size):
            batch = photos[i:i + batch_size]

            for photo in batch:
                try:
                    self.process_photo(photo, force)
                    processed += 1

                    if processed % 10 == 0:
                        self.stdout.write(f'Processed {processed}/{total_photos} photos...')

                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f'Error processing photo {photo.id} ({photo.title}): {e}')
                    )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {processed} photos')
        )
        if errors > 0:
            self.stdout.write(
                self.style.WARNING(f'Encountered {errors} errors during processing')
            )

    def process_photo(self, photo, force=False):
        """Process a single photo to generate thumbnails."""
        # Check if thumbnail already exists and we're not forcing regeneration
        if not force and photo.thumbnail and os.path.exists(photo.thumbnail.path):
            return

        # Access the thumbnail property to trigger generation
        try:
            # This will generate the thumbnail if it doesn't exist
            photo.thumbnail.url
            self.stdout.write(f'Generated thumbnail for: {photo.title}')
        except Exception as e:
            raise Exception(f'Failed to generate thumbnail: {e}')

        # Also generate the optimized version
        try:
            if hasattr(photo, 'optimized') and photo.optimized:
                photo.optimized.url
                self.stdout.write(f'Generated optimized version for: {photo.title}')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Failed to generate optimized version for {photo.title}: {e}')
            )

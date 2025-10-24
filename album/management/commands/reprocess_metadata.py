import logging
from django.core.management.base import BaseCommand
from album.models import Photo
from album.services.media_service import MediaService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Re-processes existing photos to extract EXIF metadata like Date Taken.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reprocessing of all photos, not just those with a missing date_taken.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate the process without saving any changes to the database.',
        )

    def handle(self, *args, **options):
        force = options['force']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING("--- DRY RUN MODE --- No changes will be saved."))

        if force:
            self.stdout.write(self.style.WARNING("Forcing reprocessing for all photos."))
            photos_to_process = Photo.objects.all()
        else:
            self.stdout.write("Processing photos with no 'date_taken' set.")
            photos_to_process = Photo.objects.filter(date_taken__isnull=True)

        if not photos_to_process.exists():
            self.stdout.write(self.style.SUCCESS("No photos to process."))
            return

        self.stdout.write(f"Found {photos_to_process.count()} photos to process.")
        
        updated_count = 0
        error_count = 0

        for photo in photos_to_process.iterator():
            self.stdout.write(f"Processing photo ID: {photo.id} ({photo.image.name})...", ending='')
            try:
                # Store the old date to check if it changed
                old_date = photo.date_taken

                if not dry_run:
                    # This service function only extracts metadata and saves the photo instance.
                    # It does not affect relationships like albums, categories, or tags.
                    MediaService.extract_photo_metadata(photo)
                
                # Reload from DB to check the new value if not in dry-run
                if not dry_run:
                    photo.refresh_from_db()
                    if photo.date_taken != old_date:
                        self.stdout.write(self.style.SUCCESS(f" -> Updated date to {photo.date_taken}"))
                        updated_count += 1
                    else:
                        self.stdout.write(self.style.NOTICE(" -> No date information found or date unchanged."))
                else:
                    # Simulate a successful update for dry-run reporting
                    self.stdout.write(self.style.SUCCESS(" -> Would be processed."))
                    updated_count += 1

            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f" -> ERROR: File not found at {photo.image.path}"))
                error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f" -> ERROR: An unexpected error occurred: {e}"))
                logger.error(f"Error reprocessing photo {photo.id}: {e}", exc_info=True)
                error_count += 1
        
        self.stdout.write("\n" + self.style.SUCCESS("--- Reprocessing Complete ---"))
        self.stdout.write(f"Successfully processed: {updated_count} photos.")
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"Failed to process: {error_count} photos. Check logs for details."))
        if dry_run:
            self.stdout.write(self.style.WARNING("--- DRY RUN MODE --- No changes were saved."))

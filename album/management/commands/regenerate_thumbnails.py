from django.core.management.base import BaseCommand
from album.models import Photo

class Command(BaseCommand):
    help = 'Regenerates all thumbnails for all photos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--album_id',
            type=int,
            help='Only regenerate thumbnails for photos in the specified album.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate the command without making any changes.',
        )

    def handle(self, *args, **options):
        album_id = options['album_id']
        dry_run = options['dry_run']
        
        photos = Photo.objects.all()
        if album_id:
            photos = photos.filter(album_id=album_id)

        successful = 0
        errors = 0
        
        for photo in photos:
            try:
                # Check if the image file actually exists
                if not photo.image or not photo.image.storage.exists(photo.image.name):
                    self.stdout.write(
                        self.style.WARNING(f'Skipping {photo.image.name if photo.image else "photo with no image"} - file does not exist')
                    )
                    errors += 1
                    continue
                    
                self.stdout.write(f'Regenerating thumbnail for {photo.image.name}...')
                if not dry_run:
                    photo.thumbnail.generate(force=True)
                successful += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {photo.image.name if photo.image else f"photo {photo.id}"}: {e}')
                )
                errors += 1
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'Dry run complete. {successful} thumbnails would be regenerated, {errors} errors found.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully regenerated {successful} thumbnails, {errors} errors encountered.'))

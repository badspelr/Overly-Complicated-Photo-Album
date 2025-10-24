import os
from django.core.management.base import BaseCommand
from album.models import Photo
from django.conf import settings
from django.db.models import Count

class Command(BaseCommand):
    help = 'Deletes duplicate photos from the database and filesystem.'

    def handle(self, *args, **options):
        # Find all checksums that have more than one photo
        duplicate_checksums = (
            Photo.objects.values('checksum')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
            .values_list('checksum', flat=True)
        )

        if not duplicate_checksums:
            self.stdout.write(self.style.SUCCESS('No duplicate photos found.'))
            return

        self.stdout.write(self.style.WARNING(f'Found {len(list(duplicate_checksums))} sets of duplicate photos.'))

        for checksum in duplicate_checksums:
            # Get all photos with this checksum
            photos = Photo.objects.filter(checksum=checksum).order_by('id')
            
            # Keep the first one and delete the rest
            photos_to_delete = photos[1:]
            
            self.stdout.write(self.style.SUCCESS(f'Found {len(photos_to_delete)} duplicates for checksum {checksum}.'))

            for photo in photos_to_delete:
                # Get the full path to the image file
                image_path = os.path.join(settings.MEDIA_ROOT, photo.image.name)

                # Delete the image file if it exists
                if os.path.exists(image_path):
                    os.remove(image_path)
                    self.stdout.write(self.style.SUCCESS(f'Deleted file: {image_path}'))
                else:
                    self.stdout.write(self.style.WARNING(f'File not found: {image_path}'))

                # Delete the Photo object from the database
                photo.delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted photo object: {photo.title}'))

        self.stdout.write(self.style.SUCCESS('Finished deleting duplicate photos.'))

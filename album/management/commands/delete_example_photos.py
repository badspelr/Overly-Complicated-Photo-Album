import os
from django.core.management.base import BaseCommand
from album.models import Photo
from django.conf import settings

class Command(BaseCommand):
    help = 'Deletes photos with filenames starting with "example" from the database and filesystem.'

    def handle(self, *args, **options):
        # Find all photos where the image path starts with 'photos/example'
        photos_to_delete = Photo.objects.filter(image__startswith='photos/example')

        if not photos_to_delete.exists():
            self.stdout.write(self.style.SUCCESS('No photos matching "example*" were found.'))
            return

        count = photos_to_delete.count()
        self.stdout.write(self.style.WARNING(f'Found {count} photos to delete.'))

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

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} photos.'))

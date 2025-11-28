import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from album.models import Photo, Album, Category

class Command(BaseCommand):
    help = 'Imports photos from the media/photos directory into the database.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username of the owner of the imported photos.')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist.'))
            return

        # Create a default album and category for the imported photos
        category, _ = Category.objects.get_or_create(name='Imported Photos', created_by=user)
        album, _ = Album.objects.get_or_create(title='Imported Photos', owner=user, category=category)

        photos_dir = 'media/photos'
        for filename in os.listdir(photos_dir):
            if filename.startswith('.'):
                continue

            filepath = os.path.join(photos_dir, filename)
            if os.path.isdir(filepath):
                continue

            # Check if a photo with this image path already exists
            if Photo.objects.filter(image=f'photos/{filename}').exists():
                self.stdout.write(self.style.WARNING(f'Skipping "{filename}" as it already exists in the database.'))
                continue

            self.stdout.write(self.style.SUCCESS(f'Importing "{filename}"...'))
            with open(filepath, 'rb') as f:
                photo = Photo(
                    title=filename,
                    album=album,
                    category=category,
                )
                photo.image.save(filename, File(f), save=True)

        self.stdout.write(self.style.SUCCESS('Finished importing photos.'))

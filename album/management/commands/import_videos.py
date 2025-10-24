import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from album.models import Video, Album, Category

class Command(BaseCommand):
    help = 'Imports videos from the media/videos directory into the database.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username of the owner of the imported videos.')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist.'))
            return

        # Create a default album and category for the imported videos
        category, _ = Category.objects.get_or_create(name='Imported Videos', created_by=user)
        album, _ = Album.objects.get_or_create(title='Imported Videos', owner=user, category=category)

        videos_dir = 'media/videos'
        for filename in os.listdir(videos_dir):
            if filename.startswith('.'):
                continue

            filepath = os.path.join(videos_dir, filename)
            if os.path.isdir(filepath):
                continue

            # Check if a video with this video path already exists
            if Video.objects.filter(video=f'videos/{filename}').exists():
                self.stdout.write(self.style.WARNING(f'Skipping "{filename}" as it already exists in the database.'))
                continue

            self.stdout.write(self.style.SUCCESS(f'Importing "{filename}"...'))
            with open(filepath, 'rb') as f:
                video = Video(
                    title=filename,
                    album=album,
                    category=category,
                )
                video.video.save(filename, File(f), save=True)

        self.stdout.write(self.style.SUCCESS('Finished importing videos.'))

import hashlib
from django.core.management.base import BaseCommand
from album.models import Photo

class Command(BaseCommand):
    help = 'Regenerates checksums for all existing photos.'

    def handle(self, *args, **options):
        photos = Photo.objects.all()
        count = photos.count()
        self.stdout.write(self.style.SUCCESS(f'Found {count} photos to process.'))

        for photo in photos:
            if photo.image:
                try:
                    hasher = hashlib.md5()
                    for chunk in photo.image.chunks():
                        hasher.update(chunk)
                    checksum = hasher.hexdigest()
                    
                    if photo.checksum != checksum:
                        photo.checksum = checksum
                        photo.save()
                        self.stdout.write(self.style.SUCCESS(f'Updated checksum for photo: {photo.title}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Checksum for photo: {photo.title} is already up to date.'))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to generate checksum for photo {photo.pk}: {e}'))

        self.stdout.write(self.style.SUCCESS('Finished regenerating checksums.'))

import time
from django.core.management.base import BaseCommand
from django.db.models import Q
from album.models import Photo
from album.services.embedding_service import generate_image_embedding

class Command(BaseCommand):
    help = 'Generates embeddings for existing photos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of embeddings for all photos, even those that already have one.',
        )

    def handle(self, *args, **options):
        force_regeneration = options['force']
        
        if force_regeneration:
            self.stdout.write(self.style.WARNING('Forcing regeneration for all photos.'))
            photos_to_process = Photo.objects.exclude(Q(image='') | Q(image__isnull=True))
        else:
            self.stdout.write('Starting to generate embeddings for photos that do not have them...')
            photos_to_process = Photo.objects.filter(embedding__isnull=True).exclude(Q(image='') | Q(image__isnull=True))

        # Count photos without images for reporting
        photos_without_images = Photo.objects.filter(Q(image='') | Q(image__isnull=True)).count()
        
        total_photos = photos_to_process.count()
        if total_photos == 0:
            self.stdout.write(self.style.SUCCESS('No photos to process.'))
            if photos_without_images > 0:
                self.stdout.write(self.style.WARNING(f'Note: {photos_without_images} photo records have no image files and were skipped.'))
            return

        self.stdout.write(f'Found {total_photos} photos to process.')
        if photos_without_images > 0:
            self.stdout.write(self.style.WARNING(f'Note: {photos_without_images} photo records have no image files and will be skipped.'))
        
        start_time = time.time()
        processed_count = 0
        error_count = 0
        
        for photo in photos_to_process:
            # Double-check image exists (shouldn't be needed but safer)
            if not photo.image or not hasattr(photo.image, 'path'):
                error_count += 1
                continue
            
            try:
                embedding = generate_image_embedding(photo.image.path)
                
                if embedding:
                    Photo.objects.filter(pk=photo.pk).update(embedding=embedding)
                    processed_count += 1
                    if processed_count % 50 == 0:  # Progress update every 50 photos
                        self.stdout.write(f'Processed {processed_count}/{total_photos} photos...')
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to generate embedding for photo: {photo.title} ({photo.pk})'))
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'An error occurred for photo {photo.pk}: {e}'))
                error_count += 1

        end_time = time.time()
        duration = end_time - start_time
        
        self.stdout.write(self.style.SUCCESS('\n=== Embedding Generation Complete ==='))
        self.stdout.write(f'Successfully processed: {processed_count} photos')
        self.stdout.write(f'Errors encountered: {error_count} photos')
        if photos_without_images > 0:
            self.stdout.write(f'Photos without images (skipped): {photos_without_images} photos')
        self.stdout.write(f'Total time taken: {duration:.2f} seconds')

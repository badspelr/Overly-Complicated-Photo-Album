"""
Signals for the album app.
"""
import logging
import hashlib
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Photo, Video
from .utils.media_utils import VideoThumbnailGenerator
from .services.embedding_service import generate_image_embedding

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Photo)
def generate_photo_checksum(sender, instance, **kwargs):
    """
    Generate and save the checksum for a new photo.
    """
    if instance.image and not instance.checksum:
        try:
            hasher = hashlib.md5()
            for chunk in instance.image.chunks():
                hasher.update(chunk)
            instance.checksum = hasher.hexdigest()
        except Exception as e:
            logger.error(f"Failed to generate checksum for photo {instance.pk}: {e}")


@receiver(post_save, sender=Photo)
def generate_photo_embedding_signal(sender, instance, created, **kwargs):
    """
    Generate and save embedding for a new photo.
    """
    if created:
        if instance.image:
            try:
                embedding = generate_image_embedding(instance.image.path)
                if embedding:
                    # Use update to avoid triggering the signal again
                    Photo.objects.filter(pk=instance.pk).update(embedding=embedding)
                    logger.info(f"Generated and saved embedding for photo: {instance.title}")
            except Exception as e:
                logger.error(f"Failed to generate embedding for photo {instance.pk}: {e}")


@receiver(post_save, sender=Video)
def generate_video_thumbnail(sender, instance, created, **kwargs):
    """
    Generate thumbnail for newly uploaded videos.
    """
    # Only generate thumbnail for new videos or videos without thumbnails
    if created or not instance.thumbnail:
        if instance.video:  # Make sure video file exists
            logger.info(f"Generating thumbnail for video: {instance.title}")
            success = VideoThumbnailGenerator.generate_video_thumbnail(instance)
            if not success:
                logger.warning(f"Failed to generate thumbnail for video: {instance.title}")
        else:
            logger.warning(f"No video file found for video: {instance.title}")
"""
Celery tasks for background AI processing of photos and videos.
"""
import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.core.management import call_command

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_photo_ai(self, photo_id):
    """
    Process a single photo with AI analysis.
    
    Args:
        photo_id: ID of the Photo object to process
        
    Returns:
        dict: Processing result with status and details
    """
    from album.models import Photo
    
    try:
        photo = Photo.objects.get(id=photo_id)
        photo.processing_status = Photo.ProcessingStatus.PROCESSING
        photo.save(update_fields=['processing_status'])
        
        logger.info(f"Processing photo {photo_id}: {photo.filename}")
        
        # Use existing management command for processing
        call_command('process_photos_ai', photo_ids=[photo_id])
        
        # Update status
        photo.refresh_from_db()
        if photo.ai_processed:
            photo.processing_status = Photo.ProcessingStatus.COMPLETED
            photo.save(update_fields=['processing_status'])
            logger.info(f"Successfully processed photo {photo_id}")
            return {'status': 'success', 'photo_id': photo_id}
        else:
            raise Exception("AI processing completed but ai_processed flag not set")
            
    except Photo.DoesNotExist:
        logger.error(f"Photo {photo_id} not found")
        return {'status': 'error', 'photo_id': photo_id, 'error': 'Photo not found'}
        
    except Exception as exc:
        logger.error(f"Error processing photo {photo_id}: {exc}")
        
        try:
            photo = Photo.objects.get(id=photo_id)
            photo.processing_status = Photo.ProcessingStatus.FAILED
            photo.ai_processing_error = str(exc)
            photo.save(update_fields=['processing_status', 'ai_processing_error'])
        except:
            pass
        
        # Retry up to 3 times
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_video_ai(self, video_id):
    """
    Process a single video with AI analysis.
    
    Args:
        video_id: ID of the Video object to process
        
    Returns:
        dict: Processing result with status and details
    """
    from album.models import Video
    
    try:
        video = Video.objects.get(id=video_id)
        video.processing_status = Video.ProcessingStatus.PROCESSING
        video.save(update_fields=['processing_status'])
        
        logger.info(f"Processing video {video_id}: {video.filename}")
        
        # Use existing management command for processing
        call_command('process_videos_ai', video_ids=[video_id])
        
        # Update status
        video.refresh_from_db()
        if video.ai_processed:
            video.processing_status = Video.ProcessingStatus.COMPLETED
            video.save(update_fields=['processing_status'])
            logger.info(f"Successfully processed video {video_id}")
            return {'status': 'success', 'video_id': video_id}
        else:
            raise Exception("AI processing completed but ai_processed flag not set")
            
    except Video.DoesNotExist:
        logger.error(f"Video {video_id} not found")
        return {'status': 'error', 'video_id': video_id, 'error': 'Video not found'}
        
    except Exception as exc:
        logger.error(f"Error processing video {video_id}: {exc}")
        
        try:
            video = Video.objects.get(id=video_id)
            video.processing_status = Video.ProcessingStatus.FAILED
            video.ai_processing_error = str(exc)
            video.save(update_fields=['processing_status', 'ai_processing_error'])
        except:
            pass
        
        # Retry up to 3 times
        raise self.retry(exc=exc)


@shared_task
def process_pending_photos_batch():
    """
    Scheduled task to process pending photos in batch.
    Runs daily at 2 AM via Celery Beat.
    """
    from album.models import Photo
    
    if not settings.AI_SCHEDULED_PROCESSING:
        logger.info("Scheduled AI processing is disabled")
        return {'status': 'disabled'}
    
    batch_size = settings.AI_BATCH_SIZE
    
    # Get pending photos
    pending_photos = Photo.objects.filter(
        processing_status=Photo.ProcessingStatus.PENDING,
        ai_processed=False
    ).order_by('uploaded_at')[:batch_size]
    
    count = pending_photos.count()
    logger.info(f"Starting batch processing of {count} pending photos (max {batch_size})")
    
    if count == 0:
        logger.info("No pending photos to process")
        return {'status': 'success', 'processed': 0}
    
    # Queue individual tasks
    for photo in pending_photos:
        process_photo_ai.delay(photo.id)
    
    logger.info(f"Queued {count} photos for processing")
    return {'status': 'success', 'queued': count}


@shared_task
def process_pending_videos_batch():
    """
    Scheduled task to process pending videos in batch.
    Runs daily at 2:30 AM via Celery Beat.
    """
    from album.models import Video
    
    if not settings.AI_SCHEDULED_PROCESSING:
        logger.info("Scheduled AI processing is disabled")
        return {'status': 'disabled'}
    
    batch_size = settings.AI_BATCH_SIZE
    
    # Get pending videos
    pending_videos = Video.objects.filter(
        processing_status=Video.ProcessingStatus.PENDING,
        ai_processed=False
    ).order_by('uploaded_at')[:batch_size]
    
    count = pending_videos.count()
    logger.info(f"Starting batch processing of {count} pending videos (max {batch_size})")
    
    if count == 0:
        logger.info("No pending videos to process")
        return {'status': 'success', 'processed': 0}
    
    # Queue individual tasks
    for video in pending_videos:
        process_video_ai.delay(video.id)
    
    logger.info(f"Queued {count} videos for processing")
    return {'status': 'success', 'queued': count}


@shared_task
def process_media_on_upload(media_type, media_id):
    """
    Process media immediately after upload if auto-processing is enabled.
    
    Args:
        media_type: 'photo' or 'video'
        media_id: ID of the media object
    """
    if not settings.AI_AUTO_PROCESS_ON_UPLOAD:
        logger.info(f"Auto-processing on upload is disabled for {media_type} {media_id}")
        return {'status': 'disabled'}
    
    if media_type == 'photo':
        return process_photo_ai(media_id)
    elif media_type == 'video':
        return process_video_ai(media_id)
    else:
        logger.error(f"Unknown media type: {media_type}")
        return {'status': 'error', 'error': 'Unknown media type'}

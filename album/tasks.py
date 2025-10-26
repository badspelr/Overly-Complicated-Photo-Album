"""
Celery tasks for background AI processing of photos and videos.
"""
import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.core.management import call_command

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, time_limit=600, soft_time_limit=540)
def process_photo_ai(self, photo_id):
    """
    Process a single photo with AI analysis.
    
    Args:
        photo_id: ID of the Photo object to process
        
    Returns:
        dict: Processing result with status and details
    """
    from album.models import Photo
    from album.services.ai_analysis_service import analyze_image, is_ai_analysis_available
    import os
    
    try:
        photo = Photo.objects.get(id=photo_id)
        photo.processing_status = Photo.ProcessingStatus.PROCESSING
        photo.save(update_fields=['processing_status'])
        
        logger.info(f"Processing photo {photo_id}: {photo.title}")
        
        # Check if AI analysis is available
        if not is_ai_analysis_available():
            raise Exception("AI analysis service is not available")
        
        # Check if image file exists
        if not photo.image or not hasattr(photo.image, 'path'):
            raise Exception("Photo has no image file path")
        
        if not os.path.exists(photo.image.path):
            raise Exception(f"Image file does not exist: {photo.image.path}")
        
        # Analyze the image
        analysis_result = analyze_image(photo.image.path)
        
        if analysis_result['description']:
            # Update the photo with AI analysis results
            photo.ai_description = analysis_result['description']
            photo.ai_tags = analysis_result['tags']
            photo.ai_confidence_score = analysis_result['confidence']
            photo.ai_processed = True
            photo.processing_status = Photo.ProcessingStatus.COMPLETED
            photo.save(update_fields=[
                'ai_description', 'ai_tags', 'ai_confidence_score',
                'ai_processed', 'processing_status'
            ])
            
            logger.info(f"Successfully processed photo {photo_id}")
            return {'status': 'success', 'photo_id': photo_id}
        else:
            raise Exception("AI analysis returned no description")
            
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


@shared_task(bind=True, max_retries=3, default_retry_delay=60, time_limit=600, soft_time_limit=540)
def process_video_ai(self, video_id):
    """
    Process a single video with AI analysis.
    
    Args:
        video_id: ID of the Video object to process
        
    Returns:
        dict: Processing result with status and details
    """
    from album.models import Video
    from album.services.ai_analysis_service import analyze_image, is_ai_analysis_available
    from album.services.embedding_service import generate_image_embedding
    import os
    
    try:
        video = Video.objects.get(id=video_id)
        video.processing_status = Video.ProcessingStatus.PROCESSING
        video.save(update_fields=['processing_status'])
        
        logger.info(f"Processing video {video_id}: {video.title}")
        
        # Check if AI analysis is available
        if not is_ai_analysis_available():
            raise Exception("AI analysis service is not available")
        
        # Check if video has a thumbnail
        if not video.thumbnail or not hasattr(video.thumbnail, 'path'):
            raise Exception("Video has no thumbnail. Generate thumbnails first.")
        
        # Check if thumbnail file exists
        if not os.path.exists(video.thumbnail.path):
            raise Exception(f"Thumbnail file does not exist: {video.thumbnail.path}")
        
        # Analyze the video thumbnail
        analysis_result = analyze_image(video.thumbnail.path)
        
        if analysis_result['description']:
            # Generate embedding for the thumbnail
            thumbnail_embedding = generate_image_embedding(video.thumbnail.path)
            
            # Update the video with AI analysis results
            video.ai_description = analysis_result['description']
            video.ai_tags = analysis_result['tags']
            video.ai_confidence_score = analysis_result['confidence']
            video.ai_processed = True
            video.processing_status = Video.ProcessingStatus.COMPLETED
            video.thumbnail_embedding = thumbnail_embedding
            video.save(update_fields=[
                'ai_description', 'ai_tags', 'ai_confidence_score',
                'ai_processed', 'processing_status', 'thumbnail_embedding'
            ])
            
            logger.info(f"Successfully processed video {video_id}")
            return {'status': 'success', 'video_id': video_id}
        else:
            raise Exception("AI analysis returned no description")
            
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

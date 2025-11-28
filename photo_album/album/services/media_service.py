"""
Media service for handling photo and video operations.
"""
import logging
from django.core.exceptions import ValidationError
from django.db import transaction
from PIL import Image, ExifTags
from moviepy.editor import VideoFileClip
from ..models import Photo, Video
from ..security import secure_file_upload, ALLOWED_IMAGE_TYPES, ALLOWED_VIDEO_TYPES
from ..logging_utils import ErrorHandler, log_user_action, log_security_event

logger = logging.getLogger(__name__)


class MediaService:
    """Service class for media operations."""
    
    @staticmethod
    def extract_photo_metadata(photo):
        """Extract metadata from uploaded photo."""
        with ErrorHandler('extract_photo_metadata', additional_context={'photo_id': photo.id}):
            try:
                img = Image.open(photo.image.path)
                # Use the public getexif() method and check if it exists
                exif_data = None
                if hasattr(img, 'getexif'):
                    exif_data = img.getexif()
                
                if exif_data:
                    # Create a dictionary of decoded EXIF tags for easier access
                    exif = {
                        ExifTags.TAGS[k]: v
                        for k, v in exif_data.items()
                        if k in ExifTags.TAGS
                    }

                    # Prioritize DateTimeOriginal, fall back to DateTime
                    date_str = exif.get('DateTimeOriginal') or exif.get('DateTime')
                    if date_str:
                        from datetime import datetime
                        try:
                            # Handle potential timezone offsets or other formats if necessary in the future
                            photo.date_taken = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Could not parse EXIF date string '{date_str}': {e}")

                    photo.camera_make = exif.get('Make')
                    photo.camera_model = exif.get('Model')
                    
                    gps_info = exif.get('GPSInfo')
                    if gps_info:
                        MediaService._extract_gps_data(photo, gps_info)
                
                photo.save()
                logger.info(f"Successfully extracted metadata for photo {photo.id}")
                
            except Exception as e:
                logger.error(f"Error extracting photo metadata for photo {photo.id}: {e}")
                raise
    
    @staticmethod
    def _extract_gps_data(photo, gps_value):
        """Extract GPS data from EXIF."""
        try:
            gps_info = {}
            for t in gps_value:
                sub_tag = ExifTags.GPSTAGS.get(t, t)
                gps_info[sub_tag] = gps_value[t]
            
            if all(key in gps_info for key in ['GPSLatitude', 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef']):
                lat_ref = gps_info['GPSLatitudeRef']
                lon_ref = gps_info['GPSLongitudeRef']
                lat = gps_info['GPSLatitude']
                lon = gps_info['GPSLongitude']
                
                lat_deg = lat[0][0] / lat[0][1] + lat[1][0] / lat[1][1] / 60 + lat[2][0] / lat[2][1] / 3600
                lon_deg = lon[0][0] / lon[0][1] + lon[1][0] / lon[1][1] / 60 + lon[2][0] / lon[2][1] / 3600
                
                if lat_ref == 'S':
                    lat_deg = -lat_deg
                if lon_ref == 'W':
                    lon_deg = -lon_deg
                
                photo.latitude = lat_deg
                photo.longitude = lon_deg
                
        except Exception as e:
            logger.warning(f"Error parsing GPSInfo in EXIF: {e}")
    
    @staticmethod
    def extract_video_metadata(video):
        """Extract metadata from uploaded video."""
        with ErrorHandler('extract_video_metadata', additional_context={'video_id': video.id}):
            try:
                clip = VideoFileClip(video.video.path)
                video.duration = clip.duration
                video.width, video.height = clip.size

                import os
                from datetime import datetime
                file_creation_time = os.path.getctime(video.video.path)
                video.date_recorded = datetime.fromtimestamp(file_creation_time)

                if hasattr(clip, 'reader') and hasattr(clip.reader, 'infos'):
                    infos = clip.reader.infos
                    if 'creation_time' in infos:
                        creation_time = infos['creation_time']
                        if isinstance(creation_time, str):
                            try:
                                video.date_recorded = datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
                            except ValueError as e:
                                logger.warning(f"Invalid creation_time format in video metadata: {creation_time} ({e})")

                video.save()
                logger.info(f"Successfully extracted metadata for video {video.id}")
                
            except Exception as e:
                logger.error(f"Error extracting video metadata for video {video.id}: {e}")
                raise
    
    @staticmethod
    @transaction.atomic
    def upload_media_files(media_files, album=None, category=None, title=None, description=None, user=None):
        """
        Upload multiple media files with proper error handling.
        
        Returns:
            dict: Results with counts of uploaded files and any errors
        """
        results = {
            'uploaded_photos': 0,
            'uploaded_videos': 0,
            'errors': [],
            'warnings': []
        }
        
        for media_file in media_files:
            try:
                # Security validation
                if media_file.content_type.startswith('image/'):
                    secure_file_upload(media_file, ALLOWED_IMAGE_TYPES, is_image=True)
                elif media_file.content_type.startswith('video/'):
                    secure_file_upload(media_file, ALLOWED_VIDEO_TYPES, is_image=False)
                else:
                    results['warnings'].append(f'File {media_file.name} is not a supported media type. Skipped.')
                    continue

                # Check for duplicates
                if album and media_file.content_type.startswith('image/'):
                    if Photo.objects.filter(album=album, image__icontains=media_file.name).exists():
                        results['warnings'].append(f'Photo {media_file.name} already exists in this album. Skipped.')
                        continue
                elif album and media_file.content_type.startswith('video/'):
                    if Video.objects.filter(album=album, video__icontains=media_file.name).exists():
                        results['warnings'].append(f'Video {media_file.name} already exists in this album. Skipped.')
                        continue

                # Create and save media object
                if media_file.content_type.startswith('image/'):
                    photo = Photo(
                        album=album,
                        category=category,
                        title=title or media_file.name,
                        description=description,
                        image=media_file
                    )
                    photo.save()
                    
                    # Extract metadata
                    MediaService.extract_photo_metadata(photo)
                    
                    results['uploaded_photos'] += 1
                    log_user_action('photo_uploaded', user, 'photo', photo.id)
                    
                elif media_file.content_type.startswith('video/'):
                    video = Video(
                        album=album,
                        category=category,
                        title=title or media_file.name,
                        description=description,
                        video=media_file
                    )
                    video.save()
                    
                    # Extract metadata
                    MediaService.extract_video_metadata(video)
                    
                    results['uploaded_videos'] += 1
                    log_user_action('video_uploaded', user, 'video', video.id)
                    
            except ValidationError as e:
                error_msg = f'File {media_file.name}: {str(e)}'
                results['errors'].append(error_msg)
                log_security_event('file_validation_failed', user, f'File: {media_file.name}, Error: {str(e)}')
                
            except Exception as e:
                error_msg = f'Error processing {media_file.name}: {str(e)}'
                results['errors'].append(error_msg)
                logger.error(f"Error processing {media_file.name}: {e}", exc_info=True)
        
        return results
    
    @staticmethod
    def delete_media(media_obj, user):
        """Delete a media object with proper logging."""
        with ErrorHandler('delete_media', user, additional_context={'media_type': type(media_obj).__name__, 'media_id': media_obj.id}):
            media_id = media_obj.id
            media_title = media_obj.title
            media_type = type(media_obj).__name__.lower()
            
            media_obj.delete()
            
            log_user_action(f'{media_type}_deleted', user, media_type, media_id)
            logger.info(f"Successfully deleted {media_type} {media_title} (ID: {media_id})")
            
            return True
